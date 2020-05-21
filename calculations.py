import os, json, globalVal
from datetime import datetime
from flask_pymongo import PyMongo
from iexfinance.stocks import Stock, get_historical_data, get_historical_intraday

def spent_cash(ticker,price):
    spent_cash=float(ticker)*float(price)
    return spent_cash

def updated_price_coins(wallet_object):
    wallet_coins=wallet_object['coins']
    updated_price_wallet_coins=[]
    for symbol,obj in wallet_coins.items():
        updated_quote=Stock(symbol+'USDT')
        updated_price=float(updated_quote.get_price())*obj['total_ticker']
        updated_price_wallet_coins+=(symbol,updated_price)
    return updated_price_wallet_coins

def value_change_coins(wallet_object):
    return "Hello world"

def calculate_balance(wallet_object,available_cash):
    for coin,obj in wallet_object.items():
        total_ticker=0
        total_balance_toAdd=0
        for date,transaction in obj.items():
            total_ticker+=transaction['ticker']
            total_balance_toAdd+=transaction['ticker']*transaction['price']
            print('Now adding ',total_balance_toAdd)
            #total_ticker+=transaction.ticker
            #total_balance_toAdd+=transaction.ticker*transaction.price
        print('Total ticker for ',coin,'is ',total_ticker)
        print('Total balance to add for ',coin,'is ',total_balance_toAdd)