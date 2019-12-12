import requests
import json
import alpaca_trade_api

tickers_list = []

with open('tickers.txt', 'r+') as tickers_file:
  tickers_list = tickers_file.read().splitlines()

tenquant_key = 'FAKE_KEY'
tenquant_base_url = 'https://api.tenquant.io'

import alpaca_trade_api as tradeapi
key = 'FAKE_KEY'
secret = 'FAKE_SECRET'
base_url = 'https://paper-api.alpaca.markets'

api = tradeapi.REST(key, secret, base_url, api_version='v2')
account = api.get_account()
print(account.status)

all_stocks_data = {}

for stock in tickers_list:
  request_url = (tenquant_base_url + '/data?ticker={TICKER}&key={KEY}').replace('{TICKER}', stock).replace('{KEY}', tenquant_key)

  stock_json = requests.get(request_url).content

  try:
    stock_data = dict(json.loads(stock_json))
  except:
    print('BAD!!! ' + stock)
    continue
  if 'error' in stock_data.keys():
    print('BAD!!! ' + stock)
    continue  # skip this ticker if there is an error

  current_assets = stock_data['currentassets']
  current_liabilities = stock_data['currentliabilities']

  current_ratio = current_assets / current_liabilities

  print(stock)
  print(current_ratio)

stocks_data = sorted(stocks_data.items(), key=lambda x: x[1])
shorts = stocks_data[:int(len(stocks_data)/5) + 1]

portfolio_val = float(account.portfolio_value)

weightings = {}
portfolio_value = float(account.portfolio_value)

for stock, current_ratio in shorts:
  price = api.get_barset(stock, "minute", 1)[sym][0].c

  weightings[stock] = ((portfolio_value/2) / len(shorts.keys())) / price

qqq_price = api.get_barset('QQQ', "minute", 1)['QQQ'][0].c
weightings['QQQ'] = (portfolio_value/2) / qqq_price

print('weightings: ')
print(weightings)

for short_stock in weightings.keys():
    qty = weightings[short_stock]
    side = 'sell'
    try:
        api.submit_order(short_stock, qty, side, "market", "day")
        print("Market order of | " + str(qty) + " " + short_stock + " " + side + " | completed.")
    except:
        print("Order of | " + str(qty) + " " + short_stock + " " + side + " | did not go through.")
