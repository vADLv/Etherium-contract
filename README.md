Simple registrar for KYC
====

## Introduction

Contracts in the network can be used for different needs - they can automatically execute predefined agreements when any conditions or events occure, implement real world assets and interactions with them, manage voting and provide access to structured information that differs from the information just about balances modification.

The fact that the contract code placed on the blockchain cannot be modified (unless this is described in advance in the this contract) allows to guarantee that no one can change its behavior after the user's aggreement with the contract.

Your task is to develop a decentralized application containing a contract that is responsible for storing the correspondance between users names and their Ethereum accounts. For example, such contract could be a part of the KYC (Know Your Customer) sub-system of a cryptocurrency exchanges where KYC procedure is required by the law.

The application will consist of two parts the contract and a python script which will translate user actions to the contract.

## Registrar application

The application is a python script that will accept parameters from the command line and perform the following actions with the registrar contract depending on the parameters:
  * deployment of the registrar contract locating in the file `contracts/registrar.sol`;
  * register new correspondence between the name of the user and its account;
  * unregister the correspondge between the name and the account;
  * get account(s) corresponding to a name;
  * get name for a corresponding account.

The name of the script must be `registrar.py`.

The application must interact with an Ethereum node by using JSON-RPC.

The script must sign transactions and authenticate `call`-requests by using a private key. The private key must be stored in the json-file `account.json`:
```json
{"account": "c57e7db2dcc703c0e500b653ca82273b7bfad8045d85a4d2460186f7233c9270"}
```

The gas price for the transactions must be fed from a gas price oracle. It is defined that the oracle will return gas price prediction in form of a json-structure:
```json
{"block_time":19.91,"fast":14.4,"instant":25.0,"block_number":7240426,"standard":5.0,"health":true,"slow":3.0}
```
The price specified in `fast` (defined in `Gwei`) must be used. The oracle is available by HTTP requests. Example of such oracle: https://gasprice.poa.network.

RPC url and gas price oracle url will be specified in `network.json` before the script execution. The file contains the following fields:
  * `rpcUrl` - URL to access an Ethereum node by JSON RPC;
  * `gasPriceUrl` -- URL to access the gas price oracle.

The example of `network.json`:
```json
{"rpcUrl": "https://sokol.poa.network", "gasPriceUrl": "https://gasprice.poa.network/"}
``` 

Below is detailed description of the application functionality.

### 1. Contract registration (US-01)

A user is able to deploy the contract to the blockchain.

```shell
$ registrar.py --deploy
Contract address: 0xc78282BF9b270e632309bc6901D3F46416E12c5A
```

As soon as the contract deployed the directory where the script is invoked from contains the file `database.json` with an address of the deployed contract and the block number that includes the deployment transaction.

```shell
$ cat database.json
{"registrar": "0xc78282BF9b270e632309bc6901D3F46416E12c5A", "startBlock": 123456}
```

The next invocation of `registrar.py --deploy` will deploy a new instance of the contract even if the current working directory contain `database.json`

### 2. Gas price for the deployment transacton (US-02)

In order to send a deployment transaction the script choses `fast` from the JSON-structure returned by the gas price oracle

Just after the deployment tranaction verification the value from the field `fast` returned by the command:
```shell
$ curl -X GET "https://gasprice.poa.network" -H "accept: application/json"
```

and multiplied by `1000000000` will match with the value from the field `gasPrice` of the very first transaction returned by the command:
```shell
$ curl -X GET "https://blockscout.com/poa/sokol/api?module=account&action=txlist&address=<ACCOUNT>&sort=desc" -H "accept: application/json"
```

### 3. User name registration (US-03)

An user is able to register in the contract correspondence between the name and his/her account.

```shell
$ registrar.py --add "Elon Musk"
Successfully added by 0x27d6236b24f3643fb6f55442572f0a382bc6fc3674ef64a62f706591235f0ecf
```

The address of the contract is taken from the `database.json` file.

### 4. Interdict to register several names for the same account (US-04)

It must not be possible to register another name for the account if this account has already correspondence with a name in the contract.

```shell
$ registrar.py --add "Mark Zuckerberg"
One account must correspond one name
```

There is no transaction in the chain from the account executing this command.

### 5. Error handling for registration attempts (US-05)

If the account has no enough balance to send the transaction, the following message is displayed:

```shell
$ registrar.py --add "Vitalik Buterin"
No enough funds to add name
```

There is no transaction in the chain from the account executing this command.

### 6. Gas price for the transacton to register a name (US-06)

In order to send a transaction to register a name the script choses `fast` from the JSON-structure returned by the gas price oracle.

Just after verification of the tranaction to register a name the value from the field `fast` returned by the command:
```shell
$ curl -X GET "https://gasprice.poa.network" -H "accept: application/json"
```

and multiplied by `1000000000` will match with the value from the field `gasPrice` of the very first transaction returned by the command:
```shell
$ curl -X GET "https://blockscout.com/poa/sokol/api?module=account&action=txlist&address=<ACCOUNT>&sort=desc" -H "accept: application/json"
```

### 7. Removing correspondence between account and name (US-07)

An user is able to remove from the contract the correspondence between the account and his/her name.

```shell
$ registrar.py --del
Successfully deleted by 0x5442572f0a382bc6fc3674ef64a62f706591235f0ecf27d6236b24f3643fb6f5
```

The address of the contract is taken from the `database.json` file.

### 8. Attempt to remove non-existent correspondence (US-08)

If there is no correspondence between the account and a name in the contract the following message is displayed:

```shell
$ registrar.py --del
No name found for your account
```

There is no transaction in the chain from the account executing this command.

### 9. Error handling for unregistration attempts (US-09)

If the account has no enough balance to send the transaction, the following message is displayed:

```shell
$ registrar.py --del
No enough funds to delete name
```

There is no transaction in the chain from the account executing this command.

### 10. Gas price for the transacton to unregister a name (US-10)

In order to send a transaction to register a name the script choses `fast` from the JSON-structure returned by the gas price oracle.

Just after verification of the tranaction to unregister a name the value from the field `fast` returned by the command:
```shell
$ curl -X GET "https://gasprice.poa.network" -H "accept: application/json"
```

and multiplied by `1000000000` will match with the value from the field `gasPrice` of the very first transaction returned by the command:
```shell
$ curl -X GET "https://blockscout.com/poa/sokol/api?module=account&action=txlist&address=<ACCOUNT>&sort=desc" -H "accept: application/json"
```

### 11. Getting account by name (US-11)

Any user is able to get account if they provide a name

```shell
$ registrar.py --getacc "Elon Musk"
Registered account is 0x9cce34f7ab185c7aba1b7c8140d620b4bda941d6.
```

There is no transaction in the chain from the account executing this command.

### 12. Error handling for attempts to get the account by name (US-12)

If there is no correspondence between the account and a name in the contract the following message is displayed:

```shell
$ registrar.py --getacc "Vitalik Buterin"
No account registered for this name
```

There is no transaction in the chain from the account executing this command.

### 13. Getting account for removed correspondence (US-13)

For the case when the correspondence was removed from the contract, the same message is displayed as for the case when the correspondence was not registered at all.

```shell
$ registrar.py --add "Mark Zuckerberg"
Successfully added by 0xdc367624ef64a62f72706591235f0eb6f554425cf2724f3636b43ff0a382bc6f
$ registrar.py --del
Successfully deleted by 0xecf27d6236b24f3643fb6f55442572f0a382bc6fc3674ef64a62f706591235f0
$ registrar.py --getacc "Mark Zuckerberg"
No account registered for this name
```

### 14. Getting name by account (US-14)

Any user is able to get a name if they provide an account

```shell
$ registrar.py --getname 0x9cce34f7ab185c7aba1b7c8140d620b4bda941d6
Registered account is "Elon Musk"
```

There is no transaction in the chain from the account executing this command.

### 15. Error handling for attempts to get the name by account (US-15)

If there is no correspondence between the account and a name in the contract the following message is displayed:

```shell
$ registrar.py --getname 0xca35b7d915458ef540ade6068dfe2f44e8fa733c
No name registered for this account
```

There is no transaction in the chain from the account executing this command.

### 16. Getting name for removed correspondence (US-16)

For the case when the correspondence was removed from the contract, the same message is displayed as for the case when the correspondence was not registered at all.

```shell
$ registrar.py --add "Mark Zuckerberg"
Successfully added by 0xdc367624ef64a62f72706591235f0eb6f554425cf2724f3636b43ff0a382bc6f
$ registrar.py --del
Successfully deleted by 0xecf27d6236b24f3643fb6f55442572f0a382bc6fc3674ef64a62f706591235f0
$ registrar.py --getname 0x14723a09acff6d2a60dcdf7aa4aff308fddc160c
No account registered for this name
```

### 17. Getting all registered correspondences (US-17)

Any user is able to get all registered correspondences.

```shell
$ registrar.py --add "Vitalik Buterin"
Successfully added by 0x62f72706591235f0eb6f554425cf2724f36dc367624ef64a36b43ff0a382bc6f
$ registrar.py --del
Successfully deleted by 0xe0a382bc6fc3674ef64a62f706591235f0cf27d6236b24f3643fb6f55442572f
$ registrar.py --list
 "Elon Musk": 0x9cce34f7ab185c7aba1b7c8140d620b4bda941d6
 "Mark Zuckerberg": 0xdd870fa1b7c4700f2bd7f44238821c26f7392148
```

There is no transaction in the chain from the account executing this command.

### 18. Getting all accounts registered for the same name (US-18)

Any user is able to get all accounts that were registered for the same name

```shell
$ registrar.py --getacc "Elon Musk"
Registered accounts are:
0x9cce34f7ab185c7aba1b7c8140d620b4bda941d6
0x4b0897b0513fdc7c541b6d9d7e929c4e5364d2db
```

There is no transaction in the chain from the account executing this command.

### 19. Gas usage optimization

If a user unregister a correspondence, the transaction does not consume more than `24000` gas.

When after execution of

```shell
$ registrar.py --add "Mark Zuckerberg"
Successfully added by 0xdc367624ef64a62f72706591235f0eb6f554425cf2724f3636b43ff0a382bc6f
$ registrar.py --del
Successfully deleted by 0xecf27d6236b24f3643fb6f55442572f0a382bc6fc3674ef64a62f706591235f0
```

the following command is executed

```shell
$ curl -X GET "https://blockscout.com/poa/sokol/api?module=transaction&action=gettxinfo&txhash=0xecf27d6236b24f3643fb6f55442572f0a382bc6fc3674ef64a62f706591235f0" -H "accept: application/json"
```

the value of `gasUsed` in the output will be less or equal to `24000`.