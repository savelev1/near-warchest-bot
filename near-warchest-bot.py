#!/usr/bin/python3

import sys
import os
import datetime
import json

configFileName = 'config.json';

# Function definitions

def getFullPath(filename):
    return os.path.dirname(os.path.realpath(__file__)) + '/' + filename

def getNowDateString():
    now = datetime.datetime.now()
    return f'{now.day}.{now.month}.{now.year} {now.hour}:{now.minute}:{now.second}:{now.microsecond}'

def logInFile(text):
    if config["configurable"]["enableLog"] == False:
        return
    open(getFullPath(config["configurable"]["logFileName"]), 'a')
    with open(getFullPath(config["configurable"]["logFileName"]), 'a') as file:
        file.write(f'[{getNowDateString()}] {text}\r\n')

def printAndLog(text):
    print(text)
    logInFile(text)

def plexit():
    printAndLog('exit()\r\n\r\n')
    exit()

def getConfig():
    defaultConfig = {
        "configurable": {
            "poolId": 'poolName.stakehouse.betanet',
            "accountId": 'accounName.betanet',
            "network": 'betanet',
            "epochBlockLength": 10000,
            "poolOverBalance": 500,
            "enableLog": True,
            "logFileName": 'near-warchest-bot.log',
        },
        "lastEpochProgress": 1,
        "waitNextEpochCountForChangeBalance": 0,
        "currentWaitEpochCount": 0,
        "YNear": 10 ** 24,
    }
    open(getFullPath(configFileName), 'a')
    with open(getFullPath(configFileName), 'r') as file:
        if len(file.read()) > 0:
            file.seek(0, 0)
            config = json.load(file)
        else:
            config = defaultConfig;
    return config

def saveConfig(config):
    with open(getFullPath(configFileName), "w") as file:
        json.dump(config, file)

def getEpochProgress():
    latestBlockHeight = int(os.popen(" curl --silent https://rpc." + config["configurable"]["network"] + ".near.org/status | jq .sync_info.latest_block_height ").read())
    startHeight = int(os.popen(" curl --silent -d '{\"jsonrpc\": \"2.0\", \"method\": \"validators\", \"id\": \"dontcare\", \"params\": [null]}' -H 'Content-Type: application/json' https://rpc." + config["configurable"]["network"] + ".near.org | jq .result.epoch_start_height ").read())
    blockLeft =  startHeight + config["configurable"]["epochBlockLength"] - latestBlockHeight
    progress = 1 - blockLeft / config["configurable"]["epochBlockLength"]
    return progress

def isNewValidatorInNextEpoch():
    isNew = os.popen(" near validators next | awk '/" + poolId + "/ {print $2}' ").read()
    return 'New' in isNew

def getCurrentPoolSize():
    poolSizeString = os.popen(" near validators current | awk '/" + poolId + "/ {print $4}' ").read()
    if len(poolSizeString) > 0:
        return int(poolSizeString.replace(',', ''))

def getNextPoolSize():
    nextPoolSizeString = os.popen(" near validators next | awk '/" + poolId + "/ {print $6}' ").read()
    if len(nextPoolSizeString) > 0:
        return int(nextPoolSizeString.replace(',', ''))

def getPoolSize():
    currentPoolSize = getCurrentPoolSize()
    if isinstance(currentPoolSize, int):
        return currentPoolSize
    if isNewValidatorInNextEpoch():
        nextPoolSize = getNextPoolSize()
        if isinstance(nextPoolSize, int):
            return nextPoolSize
    printAndLog("Can't get current pool balance. Probably pool is not a validator")
    pingPool()
    #raise Exception("Can't get current pool balance")
    return 0;

def getStakedBalance(): 
    findStringBeforeStakedBalance = 'Contract total staked balance is ';
    findStringAfterStakedBalance = '.';
    response = os.popen('near call ' + poolId + ' unstake \'{"amount": "' + str(config["YNear"]) + '"}\' --accountId ' + accountId).read()
    startPosition = response.find(findStringBeforeStakedBalance)
    if startPosition >= 0:
        endPosition = response.find(findStringAfterStakedBalance, startPosition)
        if endPosition >= 0:
            startBalancePosition = startPosition + len(findStringBeforeStakedBalance)
            if len(response[startBalancePosition:endPosition]):
                return int(int(response[startBalancePosition:endPosition]) / config["YNear"])
    printAndLog("Can't get staked balance")
    raise Exception("Can't get staked balance")

def getCurrentSeatPrice():
    seatPriceString = os.popen(" near validators current | awk '/price/ {print substr($6, 1, length($6)-2)}' ").read()
    return int(seatPriceString.replace(',', ''))

def getNextSeatPrice():
    seatPriceString = os.popen(" near validators next | awk '/price/ {print substr($7, 1, length($7)-2)}' ").read()
    return int(seatPriceString.replace(',', ''))

def getProposalsSeatPrice():
    seatPriceString = os.popen(" near proposals | awk '/price =/ {print substr($15, 1, length($15)-1)}' ").read()
    return int(seatPriceString.replace(',', ''))

def isKickedOutPool():
    return bool(os.popen(" near validators next | grep 'Kicked out' | grep '" + poolId + "' ").read())

def getKickedOutReason():
    return os.popen(" curl --silent -d '{\"jsonrpc\": \"2.0\", \"method\": \"validators\", \"id\": \"dontcare\", \"params\": [null]}' -H 'Content-Type: application/json' https://rpc." + config["configurable"]["network"] + ".near.org | jq -c '.result.prev_epoch_kickout[] | select(.account_id | contains (\"" + poolId + "\"))' | jq .reason ").read()

def pingPool(): 
    printAndLog('Ping pool')
    os.popen(" near call " + poolId + " ping '{}' --accountId " + accountId + " ")

# Function definitions end

# Script body

config = getConfig()
lastEpochProgress = config['lastEpochProgress']
epochProgress = getEpochProgress()
config['lastEpochProgress'] = epochProgress
saveConfig(config)

poolId = config["configurable"]["poolId"]
accountId = config["configurable"]["accountId"]
printAndLog(f"Start script. Pool ID {poolId}, Account ID {accountId}")

if isKickedOutPool():
    printAndLog("Pool is kicked out in next epoch")

kickedOutReason = getKickedOutReason();
if bool(kickedOutReason):
    printAndLog(f'Kicked out reason: {kickedOutReason}')
    pingPool()

if isNewValidatorInNextEpoch():
    printAndLog(f'Pool will try be a validator in next epoch')
    pingPool()

currentSeatPrice = getCurrentSeatPrice()
nextSeatPrice = getNextSeatPrice()
proposalsSeatPrice = getProposalsSeatPrice()
maxSeatPrice = max(nextSeatPrice, proposalsSeatPrice)
printAndLog(f"Seat price: current {currentSeatPrice}, next {nextSeatPrice}, proposals {proposalsSeatPrice}, max (selected) {maxSeatPrice}")

poolSize = getPoolSize()
printAndLog(f"Pool size: {poolSize}")

if epochProgress >= lastEpochProgress:
    printAndLog(f'Wait next epoch. Epoch progress: {epochProgress} (previous {lastEpochProgress})')
    plexit()

stakedBalance = getStakedBalance()
printAndLog(f"Staked balance: {stakedBalance}")

if config['currentWaitEpochCount'] > 0:
    config['currentWaitEpochCount'] -= 1;
    saveConfig(config)
    printAndLog(f"Wait after next epoch count: {config['currentWaitEpochCount']}")
    plexit()

needStake = maxSeatPrice - stakedBalance
needStakeYNear = needStake * config["YNear"]

if needStake == 0:
    printAndLog(f"Pool size is equal to seat price ({stakedBalance} == {maxSeatPrice})")
else:
    if needStake < 0:
        needUnstakeYNear = needStakeYNear * -1
        needUnstakeYNearWithReserve = needUnstakeYNear - config["configurable"]["poolOverBalance"] * config["YNear"]
        if needUnstakeYNearWithReserve > 0:
            needUnstakeWithReserve = needUnstakeYNearWithReserve / config["YNear"]
            printAndLog(f"Unstake {needUnstakeYNearWithReserve} ({needUnstakeWithReserve}). Over balance " + str(config["configurable"]["poolOverBalance"]))
            config['currentWaitEpochCount'] = config['waitNextEpochCountForChangeBalance']
            saveConfig(config)
            printAndLog(os.popen('near call ' + poolId + ' unstake \'{"amount": "' + str(needUnstakeYNearWithReserve) + '"}\' --accountId ' + accountId).read())
        else:
            printAndLog("Can't unstake. Reached reserve limit. It's ok")
    else:
        needStakeYNearWithReserve = needStakeYNear + config["configurable"]["poolOverBalance"] * config["YNear"]
        needStakeWithReserve = needStakeYNearWithReserve / config["YNear"]
        printAndLog(f"Stake {needStakeYNearWithReserve} ({needStakeWithReserve}). Over balance " + str(config["configurable"]["poolOverBalance"]))
        config['currentWaitEpochCount'] = config['waitNextEpochCountForChangeBalance']
        saveConfig(config)
        printAndLog(os.popen('near call ' + poolId + ' stake \'{"amount": "' + str(needStakeYNearWithReserve) + '"}\' --accountId ' + accountId).read())

printAndLog("Script ends \r\n\r\n")

# Script body end

