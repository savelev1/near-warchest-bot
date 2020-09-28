# near-warchest-bot

## Описание [RU]

near-warchest-bot это скрипт для валидаторов [NEAR](https://near.org/), который управляет вашим местом валидатора и поддерживает его количество до одного. Ведет логи, определяет причину изгнания из списка валидаторов, пингует пул.

## Установка

### Установка зависимостей

```sudo apt update```

```sudo apt install python3 git curl jq```

Так же у вас должен быть установлен [near-cli](https://github.com/near/near-cli), [залогиненный](https://github.com/nearprotocol/stakewars/blob/master/challenges/challenge001.md#1connect-near-cli-to-your-betanet-wallet) под ваш аккаунт 

### Установка near-warchest-bot

```git clone https://github.com/savelev1/near-warchest-bot.git $HOME/near-warchest-bot```

near-warchest-bot установится в директорию *$HOME/near-warchest-bot*. Вы можете ее изменить на свое усмотрение.

Откройте директорию в которую установился скрипт и создайте файл config.json из config.example.json:

```cd $HOME/near-warchest-bot && cp config.example.json config.json```

Откройте config.json для настройки скрипта

```nano config.json```

### Описание параметров файла config.json

⚠️ Внимание! Изменяйте только *configurable* секцию
 
```poolId``` - название пула

```accountId``` - название аккаунта

```network``` - название сети блокчейна

```epochBlockLength``` - длина эпохи (на данный момент betanet = 10000, testnet = 43200, mainnet = 43200)

```poolOverBalance``` - дополнительные токены NEAR для небольшого излишка на балансе (для подстраховки)

```enableLog``` - включен ли лог в файл

```logFileName``` - название файла лога

**Вам необходимо** вписать свой ```poolId``` и ```accountId``` в соответствующие поля в файле config.json

### Настройка запуска near-warchest-bot с интервалом 30 минут

```crontab -e```

В открывшемся окне редактирования Crontab добавьте в конец новую строку:

```*/30 * * * * /usr/bin/python3 $HOME/near-warchest-bot/near-warchest-bot.py > /tmp/near-warchest-bot.log 2>&1```

**✅Установка завершена**

Вы можете запустить скрипт вручную, чтобы убедиться что все работает:

```python3 $HOME/near-warchest-bot/near-warchest-bot.py```

Логи находятся в файле near-warchest-bot.log в той же директории.

### Обновление near-warchest-bot

Перейдите в директорию расположения скрипта и вытяните обновления:

```cd $HOME/near-warchest-bot && git pull```

## Description [EN]

near-warchest-bot is a script for [NEAR](https://near.org/) validators that manage your validator seat and maintain its number to one. It keeps logs, determines the reason for kicked out from the validator list, pings the pool.

## Installation

### Installation of Dependency

```sudo apt update```

```sudo apt install python3 git curl jq```

You should also have installed [near-cli](https://github.com/near/near-cli), and [logged](https://github.com/nearprotocol/stakewars/blob/master/challenges/challenge001.md#1connect-near-cli-to-your-betanet-wallet) in to your account 

### Installation of near-warchest-bot

```git clone https://github.com/savelev1/near-warchest-bot.git $HOME/near-warchest-bot```

near-warchest-bot will install in the directory *$HOME/near-warchest-bot*. You can change it at your discretion.

Open the directory where the script is installed and create an config.json file from the config.example.json:

```cd $HOME/near-warchest-bot && cp config.example.json config.json```

Open config.json to configure the script

```nano config.json```

### Description of file parameters config.json

⚠️ Attention! Change only *configurable* section
 
```poolId``` - pool name

```accountId``` - account name

```network``` - network name of the blockchain

```epochBlockLength``` - epoch length (at the moment betanet = 10000, testnet = 43200, mainnet = 43200)

```poolOverBalance``` - additional NEAR tokens for small over balance (for insurance)

```enableLog``` - enable logging in a file

```logFileName``` - name of the log file

**You need** to enter your ```polId``` and ```accountId``` in the corresponding fields in the config.json file

### Setting the start of near-warchest-bot at 30 minutes intervals

```crontab -e```

In the Crontab edit window that opens add a new line to the end:

```*/30 * * * * /usr/bin/python3 $HOME/near-warchest-bot/near-warchest-bot.py > /tmp/near-warchest-bot.log 2>&1```

**✅Installation completed**

You can run the script manually to make sure that everything works:

```python3 $HOME/near-warchest-bot/near-warchest-bot.py```

The logs are in the near-warchest-bot.log file in the same directory.

### Update near-warchest-bot

Go to the script directory and pull out the updates:

```cd $HOME/near-warchest-bot && git pull```
