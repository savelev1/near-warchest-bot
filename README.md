# near-warchest-bot

## Описание [RU]

near-warchest-bot это скрипт, который управляет вашим местом валидатора и поддерживает его количество до одного. Ведет логи, определяет причину изгнания из списка валидаторов, пингует пул.

 ⚠️ Внимание! Текущий баланс пула берется из логов метода unstake, так как в логах он обновляется мгновенно, а не через одну эпоху.

## Установка

**Установка зависимостей**

```sudo apt update```

```sudo apt install python3 git curl jq```

Так же у вас должен быть установлен [near-cli](https://github.com/near/near-cli)

**Установка near-warchest-bot**

```git clone https://github.com/savelev1/near-warchest-bot.git /home/near/near-warchest-bot```

near-warchest-bot установится в директорию */home/near/near-warchest-bot*. Вы можете ее изменить на свое усмотрение.

Откройте директорию в которую установился скрипт и создайте файл конфига из примера:

```cd /home/near/near-warchest-bot && cp config.example.json config.json```

Откройте config.json для настройки скрипта

```nano config.json```

**Описание параметров файла config.json**

⚠️ Внимание! Изменяйте только *configurable* секцию
 
```poolId``` - название пула

```accountId``` - название аккаунта

```network``` - сеть блокчейна

```epochBlockLength``` - длина эпохи (на данный момент betanet = 10000, testnet = 43200, mainnet = 43200)

```poolOverBalance``` - величина излишка на балансе (для подстраховки)

```enableLog``` - включен ли лог в файл

```logFileName``` - название файла лога

**Вам необходимо** вписать свой ```poolId``` и ```accountId``` в соответствующие поля в файле config.json

**Настройка запуска near-warchest-bot с интервалом 1 час**

```crontab -e```

В открывшемся окне редактирования Crontab добавьте в конец новую строку:

```0 */1 * * * export NODE_ENV=betanet && /usr/bin/python3 /home/near/near-warchest-bot/near-warchest-bot.py > /tmp/near-warchest-bot.log 2>&1```

**Установка завершена**

Вы можете запустить скрипт вручную, чтобы убедится что все работает:

```python3 /home/near/near-warchest-bot/near-warchest-bot.py```
