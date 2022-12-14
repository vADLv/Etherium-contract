Описание задачи
====

Контракты в сети блокчейн могут использоваться для разных нужд - автоматически исполнять заранее заданные договоренности при достижении каких-то условий или возникнования событий, описывать ценности реального мира и взаимодействие с ними, проводить голосования, предоставлять доступ к структурированной информации, отличающейся от информации об изменении балансов.

То, что код контракта, помещенный в блокчейн, не может изменяться (если это заранее не обговорено в самом контракте) позволяет гарантировать, что даже через несколько месяцев никто не сможет изменить его поведение после того, как пользователь ознакомился с контрактом. Это как раз и позволяет гарантировать исполнение заранее заданных договоренностей.

Ваща задача - написать децентрализованное приложение, частью которого является контракт, отвечающий за хранение соответствий имен пользователей и аккаунтов блокчейн сети. Такой контракт может быть часть KYC (Know Your Customer) систем, которые требуются от криптовалютных бирж и обменников, чтобы не нарушать законодальство.    

Вам необходимо разработать приложение (python-скрипт), которое бы принимало параметры через командную строку и в зависимости от параметров выполняло следующие функции:
  * регистрация в блокчейн сети контракта `Registrar`, находящегося в файле `contracts/registrar.sol`;
  * добавление нового соответствия между именем пользователя и его аккаунтом;
  * удаление соответствия между именем пользователя и его аккаунтом;
  * получение аккаунта по имени пользователя;
  * получение имени пользователя по аккаунту.

Имя исполняемого скрипта должно быть `registrar.py`

Скрипт должен работать с Ethereum узлом исключительно через подключение по RPC. 

Скрипт должен выполнять действия, включая регистрацию контракта, оперируя приватным ключом Ethereum аккаунта. Приватный ключ указывается в файле `account.json` в шестнадцатиричном формате:

```json
{"account": "c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470"}
```

Цена газа во всех транзакциях должна браться из оракула (поставщик данных из реального мира), возвращающего данные о цене в виде:

```json
{"block_time":19.91,"fast":14.4,"instant":25.0,"block_number":7240426,"standard":5.0,"health":true,"slow":3.0}
```

При выборе должна использоваться цена из значения `fast`, измеряемая в `Gwei`. Оракул доступен по HTTP протоколу. Пример оракула: https://gasprice.poa.network.

Ссылки на RPC узел и оракула цены газа передаются через конфигурационный файл `network.json`. Он содержит следующую информацию:
  * `rpcUrl` - URL для доступа к узлу по JSON RPC;
  * `gasPriceUrl` - URL для доступа к сервису, предоставляющему цену за газ.

Пример файла:
```json
{"rpcUrl": "https://sokol.poa.network", "gasPriceUrl": "https://gasprice.poa.network/"}
``` 

### Примеры использования

#### Регистрация контракта (US-01)

Пользователь может зарегистрировать контракт в блокчейн, чтобы в дальнейшем пользователи сервиса обращались к данному контракту по его адресу.
```shell
$ registrar.py --deploy
Contract address: 0xc78282BF9b270e632309bc6901D3F46416E12c5A
```
После регистрации контракта в директории, из которой запускается скрипт `registrar.py` должен создаться файл `database.json` с адресом контракта и номером блока, в котором данный контракт был зарегистрирован:
```shell
$ cat database.json
{"registrar": "0xc78282BF9b270e632309bc6901D3F46416E12c5A",
"startBlock": 123456}
```
Последующий вызов `registrar.py --deploy` регистрирует новый контракт вне зависимости от того, есть в текущей директории файл `database.json`.

#### Цена газа для транзакции регистрации контракта (US-02)

Для проведения транзакции выбирается цена из значения `fast`, возвращенного сервисом `https://gasprice.poa.network`.

Сразу после регистрации контракта значение из `fast` умноженное на 1000000000 из вывода команды
```shell
$ curl -X GET "https://gasprice.poa.network" -H "accept: application/json"
```
и значение `gasPrice` из самой первой транзакции в списке из вывода следующей команды:
```shell
$ curl -X GET "https://blockscout.com/poa/sokol/api?module=account&action=txlist&address=<ACCOUNT>&sort=desc" -H "accept: application/json"
```
должны совпадать.

#### Регистрация имени пользователя (US-03)

Пользователь может добавить в контракт соответствие имени своему аккаунту. 
```shell
$ registrar.py --add "Elon Musk"
Successfully added by 0x27d6236b24f3643fb6f55442572f0a382bc6fc3674ef64a62f706591235f0ecf
```
Адрес контракта для регистрации пользователя берется из файла `database.json`.

#### Запрет нескольких регистраций с одного аккаунта (US-04)

Пользователь не может добавить в контракт соответствие еще одного имени своему аккаунту. 
```shell
$ registrar.py --add "Mark Zuckerberg"
One account must correspond one name
```
В сети блокчейн не создается траназакций с данного аккаунта.

#### Обработка ошибок при регистрации имени пользователя (US-05)

Если на счету пользователя недостаточно средств для проведения транзакции, то выводится соответствующее сообщение: 
```shell
$ registrar.py --add "Vitalik Buterin"
No enough funds to add name
```

#### Цена газа для траназкции на регистрации имени пользователя  (US-06)

Для проведения транзакции выбирается цена из значения `fast`, возвращенного сервисом `https://gasprice.poa.network`.

Сразу после добавления имени пользователя в контракт значение из `fast` умноженное на 1000000000 из вывода команды
```shell
$ curl -X GET "https://gasprice.poa.network" -H "accept: application/json"
```
и значение `gasPrice` из самой первой транзакции в списке из вывода следующей команды:
```shell
$ curl -X GET "https://blockscout.com/poa/sokol/api?module=account&action=txlist&address=<ACCOUNT>&sort=desc" -H "accept: application/json"
```
должны совпадать.

#### Удаление имени пользователя (US-07)

Пользователь может удалить из контракта соответствие имени своему аккаунту. 
```shell
$ registrar.py --del
Successfully deleted by 0x5442572f0a382bc6fc3674ef64a62f706591235f0ecf27d6236b24f3643fb6f5
```
Адрес контракта для удаления пользователя берется из файла `database.json`.

#### Удаление несуществующего соответствия (US-08)

Если в контракте нет соответствия имени пользователя и аккаунта, то выводится соответствующее сообщение. 
```shell
$ registrar.py --del
No name found for your account
```

#### Обработка ошибок при удалении имени пользователя (US-09)

Если на счету пользователя недостаточно средств для проведения транзакции, то выводится соответствующее сообщение: 
```shell
$ registrar.py --del
No enough funds to delete name
```

#### Цена газа для траназкции на удаление имени пользователя  (US-10)

Для проведения транзакции выбирается цена из значения `fast`, возвращенного сервисом `https://gasprice.poa.network`.

Сразу после удаления имени пользователя в контракт значение из `fast` умноженное на 1000000000 из вывода команды
```shell
$ curl -X GET "https://gasprice.poa.network" -H "accept: application/json"
```
и значение `gasPrice` из самой первой транзакции в списке из вывода следующей команды:
```shell
$ curl -X GET "https://blockscout.com/poa/sokol/api?module=account&action=txlist&address=<ACCOUNT>&sort=desc" -H "accept: application/json"
```
должны совпадать.

#### Получение аккаунта по имени пользователя (US-11)

Любой пользователь может получить аккаунт по имени пользователя
```shell
$ registrar.py --getacc "Elon Musk"
Registered account is 0x9cce34f7ab185c7aba1b7c8140d620b4bda941d6.
```
Транзакция в блокчейн не отправляется.

#### Обработка ошибок при получении аккаунта по имени пользователя (US-12)

Если имя пользователя не было зарегистрировано, выдается соответствующая сообщение.
```shell
$ registrar.py --getacc "Vitalik Buterin"
No account registered for this name
```
Транзакция в блокчейн не отправляется.

#### Получение аккаунта для удаленного соответствия (US-13)

Если пользователь удалил соответствие имени и аккаунта, выдается такое же сообщение как и в том случае, когда соответствие не было зарегистрировано вообще. 
```shell
$ registrar.py --add "Mark Zuckerberg"
Successfully added by 0xdc367624ef64a62f72706591235f0eb6f554425cf2724f3636b43ff0a382bc6f
$ registrar.py --del
Successfully deleted by 0xecf27d6236b24f3643fb6f55442572f0a382bc6fc3674ef64a62f706591235f0
$ registrar.py --getacc "Mark Zuckerberg"
No account registered for this name
```

#### Получение имени пользователя по аккаунту (US-14)

Любой пользователь может получить имя пользователя по аккаунту 
```shell
$ registrar.py --getname 0x9cce34f7ab185c7aba1b7c8140d620b4bda941d6
Registered account is "Elon Musk"
```
Транзакция в блокчейн не отправляется.

#### Обработка ошибок при получении имени пользователя по аккаунту (US-15)

Если имя пользователя не было зарегистрировано, выдается соответствующая сообщение.
```shell
$ registrar.py --getname 0xca35b7d915458ef540ade6068dfe2f44e8fa733c
No name registered for this account
```
Транзакция в блокчейн не отправляется.

#### Получение аккаунта для удаленного соответствия (US-16)

Если пользователь удалил соответствие имени и аккаунта, выдается такое же сообщение как и в том случае, когда соответствие не было зарегистрировано вообще. 
```shell
$ registrar.py --add "Mark Zuckerberg"
Successfully added by 0xdc367624ef64a62f72706591235f0eb6f554425cf2724f3636b43ff0a382bc6f
$ registrar.py --del
Successfully deleted by 0xecf27d6236b24f3643fb6f55442572f0a382bc6fc3674ef64a62f706591235f0
$ registrar.py --getname 0x14723a09acff6d2a60dcdf7aa4aff308fddc160c
No account registered for this name
```

#### Получение списка всех соответствий (US-17)

Пользователь может получить все зарегистрированные соответствия 
```shell
$ registrar.py --add "Vitalik Buterin"
Successfully added by 0x62f72706591235f0eb6f554425cf2724f36dc367624ef64a36b43ff0a382bc6f
$ registrar.py --del
Successfully deleted by 0xe0a382bc6fc3674ef64a62f706591235f0cf27d6236b24f3643fb6f55442572f
$ registrar.py --list
 "Elon Musk": 0x9cce34f7ab185c7aba1b7c8140d620b4bda941d6
 "Mark Zuckerberg": 0xdd870fa1b7c4700f2bd7f44238821c26f7392148
```
Транзакция в блокчейн не отправляется.

#### Получение нескольких аккаунтов по одному имени пользователя (US-18)

Любой пользователь получит несколько аккаунтов, если зарегистрировано несколько пользователей под этим именем
```shell
$ registrar.py --getacc "Elon Musk"
Registered accounts are:
0x9cce34f7ab185c7aba1b7c8140d620b4bda941d6
0x4b0897b0513fdc7c541b6d9d7e929c4e5364d2db
```
Транзакция в блокчейн не отправляется.

#### Оптимизация контракта (US-19)

Если пользователь удалил соответствие имени и аккаунта, то транзакция потребила меньше 24000 газа.
Если после выполнения:
```shell
$ registrar.py --add "Mark Zuckerberg"
Successfully added by 0xdc367624ef64a62f72706591235f0eb6f554425cf2724f3636b43ff0a382bc6f
$ registrar.py --del
Successfully deleted by 0xecf27d6236b24f3643fb6f55442572f0a382bc6fc3674ef64a62f706591235f0
```
запустить
```
$ curl -X GET "https://blockscout.com/poa/sokol/api?module=transaction&action=gettxinfo&txhash=0xecf27d6236b24f3643fb6f55442572f0a382bc6fc3674ef64a62f706591235f0" -H "accept: application/json"
```
то значение `gasUsed` будет меньше `24000`.
