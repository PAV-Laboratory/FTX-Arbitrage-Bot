# import necessary modules
from datetime import datetime
from datetime import timezone as tz
from datetime import timedelta as td
import json

# import Ftx Rest API
from apis.FtxRest import FtxClient

with open("api_keys/api_keys.json") as f: # retrieve api keys from api_keys.json
    api_keys = json.load(f)

acc = api_keys['name']
api_key = api_keys['api_key']
api_secret = api_keys['api_secret']

ftx = FtxClient(api_key = api_key, api_secret = api_secret, subaccount_name = acc)

loop = 0 # initiate loop for counting

# start bot
while True:

    start_time = datetime.now(tz = tz.utc) # get start time

    # coins info
    token = "TOKEN_YOU_LIKE"
    base = "BASE_PAIR" # e.g. USDT/USD
    arb_size = 1

    base1 = base.split("/")[0]
    base2 = base.split("/")[1]

    # request taker fee information
    fee = float(ftx.get_account_info()['takerFee'])

    # request balance information
    bal_api = ftx.get_balances()
    time_now = str(datetime.now(tz = tz.utc))

    bal = [{'ts': time_now, 
            'account': acc, 
            'coin': coin['coin'], 
            'amount': coin['total'], 
            'usdValue': coin['usdValue']} for coin in bal_api]

    bal.append({'fee': fee})

    with open("hist/bal_hist.json") as f: # store balance history and fee data into bal_hist.json
        bal_hist = json.load(f)

    bal_hist['balance_history'].append(bal)

    with open("hist/bal_hist.json", 'w') as f:
        json.dump(bal_hist, f, indent = 3)

    # request coin information
    mkt_list = [token + '/' + base1, token + '/' + base2, base]
    orderbook = {}
    orderbook['ts'] = time_now

    for mkt in mkt_list:
        mkt_api = ftx.get_orderbook(mkt) # get orderbook data from api
        orderbook[mkt] = {}
        orderbook[mkt]['ask'] = mkt_api['asks'][0][0]
        orderbook[mkt]['bid'] = mkt_api['bids'][0][0]

    with open("hist/orderbook_hist.json") as f: # store orederbook data into orderbook_hist.json
        orderbook_hist = json.load(f)

    orderbook_hist['orderbook_history'].append(orderbook)

    with open("hist/orderbook_hist.json", 'w') as f:
        json.dump(orderbook_hist, f, indent = 3)

    # adjust the orderbook price with fee data -> effective price
    for pair in orderbook:
        if pair == "ts":
            continue
        else:
            orderbook[pair]['ask'] *= (1 + fee)
            orderbook[pair]['bid'] *= (1 - fee)

    # get implied information
    base_implied = {}

    # route1: base1 -> token -> base2 -> base1
    base_implied[base1] = 1 / orderbook[token + "/" + base1]["ask"] * orderbook[token + "/" + base2]["bid"] / orderbook[base1 + "/" + base2]["ask"]

    # route2: base2 -> token -> base1 -> base2
    base_implied[base2] = 1 / orderbook[token + "/" + base2]["ask"] * orderbook[token + "/" + base1]["bid"] * orderbook[base1 + "/" +base2]["bid"]

    # start trade
    if base_implied[base1] > 1: # check condition
        print("Buying " + token + "/" + base1) # log
        ftx.place_order(market = token + "/" + base1, side = "buy", type = "market" ,size = arb_size) # trade
        print("Selling " + token + "/" + base2)
        ftx.place_order(market = token + "/" + base2, side = "sell", type = "market" ,size = arb_size)
        print("Buying " + base1 + "/" + base2)
        ftx.place_order(market = base1 + "/" + base2, side = "buy", type = "market", size = orderbook[token + "/" + base2]["bid"])
        print("Finish " + base1 +" arbitrage")

    if base_implied[base2] > 1: # check condition
        print("Buying " + token + "/" + base2) # log
        ftx.place_order(market = token + "/" + base2, side = "buy", type = "market" ,size = arb_size) # trade
        print("Selling " + token + "/" + base1)
        ftx.place_order(market = token + "/" + base1, side = "sell", type = "market" ,size = arb_size)
        print("Buying " + base1 + "/" + base2)
        ftx.place_order(market = base1 + "/" + base2, side = "sell", type = "market", size = orderbook[token + "/" + base2]["bid"])
        print("Finish " + base1 +" arbitrage")

    end_time = datetime.now(tz = tz.utc) # get end time
    used_time = end_time - start_time
    loop += 1

    print("Loop: " + str(loop) + " | Time used: " + str(used_time)) # log
