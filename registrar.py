#!/usr/bin/env python

#from web3 import Web3, HTTPProvider
#from json import load

#with open('account.json') as file:
#    account_config = load(file)

#with open('database.json') as file:
#    database = load(file)

#with open('network.json') as file:
#    net_config = load(file)

SOLC_COMPILER="/usr/local/bin/solc"

CONTRACT_PATH="contracts/registrar.sol"

### Put your code below this comment ###

#!/usr/bin/env python
# coding: utf-8

import argparse
import json
from web3 import Web3, HTTPProvider
from eth_account import Account
#from solc import compile_source
#from solc import compile_standard
import requests
from time import sleep
from subprocess import check_output
import re
import os
from json import loads

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("--deploy",help="contract registration",action='store_true')
ap.add_argument("--add", help="user name registration")
ap.add_argument("--del", help="removing correspondence",action='store_true')
ap.add_argument("--getacc", help="getting account by name")
ap.add_argument("--getname", help="getting name by account")
ap.add_argument("--list", help="getting name by account",action='store_true')

args = vars(ap.parse_args())

with open("network.json", "r") as f:
    network_config = json.load(f)
with open("account.json", "r") as f:
    account_config = json.load(f)
with open(CONTRACT_PATH, "r") as f:
    contract_source_code = f.read()

def read_ca():
    with open("database.json", "r") as f:
        ca = json.load(f)
    return ca['registrar']
def read_bn():
    with open("database.json", "r") as f:
        ca = json.load(f)
    return ca['startBlock']

#network_config['rpcUrl'],network_config['gasPriceUrl']
#account_config['account']

def gasprice(oracle = network_config['gasPriceUrl']):
    #1 way
    # curl = 'curl -X GET '+ oracle +''' -H "accept: application/json"'''
    # result = json.loads(os.popen(curl).read())
    #2 way
    response = requests.get(
        oracle,
        headers={'Accept': 'application/json'},
        )
    result = response.json()

    return int(result['fast']*1000000000)


solc_output = check_output([SOLC_COMPILER, "--optimize", "--bin", "--abi", "contracts/registrar.sol"]).decode()

bytecode = re.findall("Binary:\\n(.*?)\\n", solc_output)[0]
abi = loads(re.findall("Contract JSON ABI\\n(.*?)\\n", solc_output)[0])

w3 = Web3(HTTPProvider(network_config['rpcUrl']))
account = Account.privateKeyToAccount(account_config['account'])

#if not w3.eth.getBalance(account.address):
#    raise Exception(f'The account {account.address} must own some coins to do transactions')


if args['deploy']:
    contract = w3.eth.contract(abi = abi, bytecode = bytecode)
    gas_estimated = contract.constructor().estimateGas({
        'from': account.address,
        'gasPrice': gasprice()
    })

    tx_wo_sign = contract.constructor().buildTransaction({
        'from': account.address,
        'nonce': w3.eth.getTransactionCount(account.address),
        'gas': gas_estimated,
        'gasPrice': gasprice()
    })

    signed_tx = account.signTransaction(tx_wo_sign)
    txId = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    txReceipt = w3.eth.waitForTransactionReceipt(txId)
    if txReceipt['status'] == 1:
        while txReceipt['blockNumber'] == None:
            sleep(0.1)
            txReceipt = w3.eth.getTransactionReceipt(txId)
        #print(f'{txId.hex()} confirmed')
        #print("contract address: " + txReceipt['contractAddress'])
        #print("deployed at block: " + str(txReceipt['blockNumber']))

        print(f'Contract address: '+txReceipt['contractAddress'])

        with open('database.json', 'w') as f:
            json.dump({"registrar": txReceipt['contractAddress'], "startBlock": txReceipt['blockNumber']}, f)


if args['add']:
    contract = w3.eth.contract(address = read_ca(), abi = abi)

    gas_estimated=0
    try:
        gas_estimated = contract.functions.registerName(args['add']).estimateGas({
            'from': account.address,
            'gasPrice': gasprice()
        })
    except ValueError as err:
        print("One account must correspond one name")

    if w3.eth.getBalance(account.address)<(gas_estimated*Web3.toWei(1, "gwei")):
        gas_estimated=0
        print('No enough funds to add name')

    if gas_estimated:
        #or update previous fields
        tx_wo_sign = contract.functions.registerName(args['add']).buildTransaction({
            'from': account.address,
            'nonce': w3.eth.getTransactionCount(account.address),
            'gas': gas_estimated,
            'gasPrice': gasprice()
        })

        signed_tx = account.signTransaction(tx_wo_sign)
        txId = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        txReceipt = w3.eth.waitForTransactionReceipt(txId)

        if txReceipt['status'] == 1:
            while txReceipt['blockNumber'] == None:
                sleep(0.1)
                txReceipt = w3.eth.getTransactionReceipt(txId)

            print(f'Successfully added by {txId.hex()}')


if args['del']:
    contract = w3.eth.contract(address = read_ca(), abi = abi)

    gas_estimated=0
    try:
        gas_estimated = contract.functions.unregisterName().estimateGas({
            'from': account.address,
            'gasPrice': gasprice()
        })
    except ValueError as err:
        print("No name found for your account")

    if w3.eth.getBalance(account.address)<(gas_estimated*Web3.toWei(1, "gwei")):
        gas_estimated=0
        print('No enough funds to delete name')

    if gas_estimated:
        #or update previous fields
        tx_wo_sign = contract.functions.unregisterName().buildTransaction({
            'from': account.address,
            'nonce': w3.eth.getTransactionCount(account.address),
            'gas': gas_estimated,
            'gasPrice': gasprice()
        })

        signed_tx = account.signTransaction(tx_wo_sign)
        txId = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        txReceipt = w3.eth.waitForTransactionReceipt(txId)

        if txReceipt['status'] == 1:
            while txReceipt['blockNumber'] == None:
                sleep(0.1)
                txReceipt = w3.eth.getTransactionReceipt(txId)

            print(f'Successfully deleted by {txId.hex()}')


if args['getacc']:
    contract = w3.eth.contract(address = read_ca(), abi = abi)

    al = contract.functions.getAddresses(args['getacc']).call()
    if len(al)==1:
        print(f'Registered account is {al[0]}')

    if len(al)==0:
        print('No account registered for this name')

    if len(al)>1:
        print('Registered accounts are:')
        for i in range(len(al)):
            print(al[i])


if args['getname']:
    contract = w3.eth.contract(address = read_ca(), abi = abi)

    al = contract.functions.getName(w3.toChecksumAddress(f"{int(args['getname'],16):#0{42}x}")).call()
    if al:
        print(f'Registered account is "{al}"')
    else:
        print(f'No name registered for this account')


if args['list']:
    contract = w3.eth.contract(address = read_ca(), abi = abi)
    address_list=[]

    event_filter = contract.events.NameRegistered.createFilter(fromBlock=read_bn())
    all_events = event_filter.get_all_entries()
    for i in all_events:
        address_list.append(i.args['_address'])

    for i in set(address_list):
        al = contract.functions.getName(w3.toChecksumAddress(f"{int(i,16):#0{42}x}")).call()
        if al:
            print(f'"{al}": {i}')
