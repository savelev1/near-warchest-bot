#!/usr/bin/python3

import sys
import os
import datetime
import json
import subprocess
import shlex
import re

configFileName = 'config.json';

# Function definitions

def runCommand(commandString):
    commands = commandString.split("|")
    procs = []
    for command in commands:
        args = shlex.split(command)
        if len(procs) == 0:
            procs.append(subprocess.Popen(args, stdout = subprocess.PIPE,  stderr = subprocess.STDOUT));
        else:
            procs.append(subprocess.Popen(args, stdin = procs[len(procs) - 1].stdout, stdout = subprocess.PIPE, stderr = subprocess.STDOUT));
    
    for i in range(len(procs)):
        if i < len(procs) - 1:
            procs[i].stdout.close()

    lastProc = procs[len(procs) - 1]
    
    result = {
        "output": lastProc.communicate()[0].decode("utf-8"),
        "code": lastProc.returncode,
    }
    return result

def escapeAnsi(line):
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)

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

def mergeTwoDicts(x, y):
    z = x.copy()
    z.update(y)
    return z

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
        "YNear": 10 ** 24,
    }
    open(getFullPath(configFileName), 'a')
    with open(getFullPath(configFileName), 'r') as file:
        if len(file.read()) > 0:
            file.seek(0, 0)
            config = mergeTwoDicts(defaultConfig, json.load(file))
        else:
            config = defaultConfig;
    return config

def saveConfig(config):
    with open(getFullPath(configFileName), "w") as file:
        json.dump(config, file)

def getEpochProgress():
    latestBlockHeight = int(runCommand("curl --silent https://rpc." + config["configurable"]["network"] + ".near.org/status | jq .sync_info.latest_block_height")["output"])
    startHeight = int(runCommand("curl --silent -d '{\"jsonrpc\": \"2.0\", \"method\": \"validators\", \"id\": \"dontcare\", \"params\": [null]}' -H 'Content-Type: application/json' https://rpc." + config["configurable"]["network"] + ".near.org | jq .result.epoch_start_height")["output"])
    blockLeft =  startHeight + config["configurable"]["epochBlockLength"] - latestBlockHeight
    progress = 1 - blockLeft / config["configurable"]["epochBlockLength"]
    return progress

def isNewValidatorInNextEpoch():
    isNew = runCommand("near validators next | awk '/" + poolId + "/ {print $2}'")["output"]
    return 'New' in isNew

def getCurrentPoolSize():
    poolSizeString = runCommand("near validators current | awk '/" + poolId + "/ {print $4}'")["output"]
    if len(poolSizeString) > 0:
        return int(poolSizeString.replace(',', ''))

def getNextPoolSize():
    nextPoolSizeString = runCommand("near validators next | awk '/" + poolId + "/ {print $6}'")["output"]
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
    #raise Exception("Can't get current pool balance")
    return 0;

def getStakedBalance(): 
    findStringBeforeStakedBalance = "'";
    findStringAfterStakedBalance = "'";
    response = escapeAnsi(runCommand("near view " + poolId + " get_total_staked_balance '{}'")["output"])
    startPosition = response.find(findStringBeforeStakedBalance)
    if startPosition >= 0:
        endPosition = response.find(findStringAfterStakedBalance, startPosition + 1)
        if endPosition >= 0:
            startBalancePosition = startPosition + len(findStringBeforeStakedBalance)
            if len(response[startBalancePosition:endPosition]):
                return int(int(response[startBalancePosition:endPosition]) / config["YNear"])
                
    printAndLog("Can't get staked balance")
    raise Exception("Can't get staked balance")

def getCurrentSeatPrice():
    seatPriceString = runCommand("near validators current | awk '/price/ {print substr($6, 1, length($6)-2)}'")["output"]
    return int(seatPriceString.replace(',', ''))

def getNextSeatPrice():
    seatPriceString = runCommand("near validators next | awk '/price/ {print substr($7, 1, length($7)-2)}'")["output"]
    return int(seatPriceString.replace(',', ''))

def getProposalsSeatPrice():
    seatPriceString = runCommand("near proposals | awk '/price =/ {print substr($15, 1, length($15)-1)}'")["output"]
    return int(seatPriceString.replace(',', ''))

def isKickedOutPool():
    return bool(runCommand("near validators next | grep 'Kicked out' | grep '" + poolId + "'")["output"])

def getKickedOutReason():
    return os.popen("curl --silent -d '{\"jsonrpc\": \"2.0\", \"method\": \"validators\", \"id\": \"dontcare\", \"params\": [null]}' -H 'Content-Type: application/json' https://rpc." + config["configurable"]["network"] + ".near.org | jq -c '.result.prev_epoch_kickout[] | select(.account_id | contains (\"" + poolId + "\"))' | jq .reason").read()

def pingPool(): 
    printAndLog('Ping pool')
    runCommand("near call " + poolId + " ping '{}' --accountId " + accountId)

# Function definitions end

# Script body

config = getConfig()
os.environ["NODE_ENV"] = config["configurable"]["network"]

poolId = config["configurable"]["poolId"]
accountId = config["configurable"]["accountId"]
printAndLog(f'Start script. Pool ID: {poolId}, Account ID: {accountId}, Network: {config["configurable"]["network"]}')

lastEpochProgress = config['lastEpochProgress']
epochProgress = getEpochProgress()
config['lastEpochProgress'] = epochProgress
saveConfig(config)

if isKickedOutPool():
    printAndLog("Pool is kicked out in next epoch")

kickedOutReason = getKickedOutReason();
if bool(kickedOutReason):
    printAndLog(f'Kicked out reason: {kickedOutReason}')

if isNewValidatorInNextEpoch():
    printAndLog(f'Pool will try be a validator in next epoch')

currentSeatPrice = getCurrentSeatPrice()
nextSeatPrice = getNextSeatPrice()
proposalsSeatPrice = getProposalsSeatPrice()
maxSeatPrice = max(nextSeatPrice, proposalsSeatPrice)
printAndLog(f"Seat price: current {currentSeatPrice}, next {nextSeatPrice}, proposals {proposalsSeatPrice}, max (selected) {maxSeatPrice}")

poolSize = getPoolSize()
printAndLog(f"Pool size: {poolSize}")

stakedBalance = getStakedBalance()
printAndLog(f"Total Staked balance: {stakedBalance}")

needUpdateBalance = False;

if maxSeatPrice != stakedBalance - config["configurable"]["poolOverBalance"]:
    needUpdateBalance = True;

if epochProgress < lastEpochProgress:
    needUpdateBalance = True;

if needUpdateBalance == False:
    printAndLog(f'Wait next epoch. Epoch progress: {epochProgress} (previous {lastEpochProgress})')
    plexit()

pingPool()

needStake = maxSeatPrice - (stakedBalance - config["configurable"]["poolOverBalance"])
needStakeYNear = needStake * config["YNear"]
if needStake == 0:
    printAndLog(f'Pool size is equal to seat price ({stakedBalance} - {config["configurable"]["poolOverBalance"]} == {maxSeatPrice})')
else:
    if needStake < 0:
        needUnstakeYNear = needStakeYNear * -1
        if needUnstakeYNear > 0:
            needUnstake = needUnstakeYNear / config["YNear"]
            printAndLog(f"Unstake {needUnstakeYNear} ({needUnstake}). Over balance " + str(config["configurable"]["poolOverBalance"]))
            response = runCommand('near call ' + poolId + ' unstake \'{"amount": "' + str(needUnstakeYNear) + '"}\' --accountId ' + accountId)
            printAndLog(response["output"]);
            if (response["code"] == 0):
                printAndLog(f'New Staked Balance: {getStakedBalance()}')
        else:
            printAndLog("Can't unstake. Reached reserve limit. It's ok")
    else:
        needStakeWithReserve = needStakeYNear / config["YNear"]
        printAndLog(f"Stake {needStakeYNear} ({needStakeWithReserve}). Over balance " + str(config["configurable"]["poolOverBalance"]))
        response = runCommand('near call ' + poolId + ' stake \'{"amount": "' + str(needStakeYNear) + '"}\' --accountId ' + accountId)
        printAndLog(response["output"]);
        if (response["code"] == 0):
            printAndLog(f'New Staked Balance: {getStakedBalance()}')

printAndLog("Script ends \r\n\r\n")

# Script body end

