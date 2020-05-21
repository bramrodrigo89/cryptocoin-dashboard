import os, json, globalVal
from datetime import datetime
from flask_pymongo import PyMongo
from iexfinance.stocks import Stock, get_historical_data, get_historical_intraday

def spent_cash(ticker,price):
    spent_cash=float(ticker)*float(price)
    return spent_cash

def updated_price_coins(wallet_object):
    wallet_coins=wallet_object['coins']
    updated_price_wallet_coins={}
    for symbol,obj in wallet_coins.items():
        updated_quote=Stock(symbol+'USDT')
        updated_price=float(updated_quote.get_price())*obj['total_ticker']
        updated_price_wallet_coins[symbol]=updated_price
    return updated_price_wallet_coins

def value_change_coins(wallet_object):
    wallet_coins=wallet_object['coins']
    value_change_coins={}
    for symbol,obj in wallet_coins.items():
        updated_quote=Stock(symbol+'USDT')
        updated_price=float(updated_quote.get_price())
        total_value_updated=updated_price*obj['total_ticker']
        value_change=total_value_updated
        for key,value in obj['transactions'].items():
            value_change-=float(value['ticker'])*float(value['price'])
        value_change_coins[symbol]=value_change
    return value_change_coins

def calculate_balance_and_change(wallet_object,available_cash):
    updated_price_coins_list=updated_price_coins(wallet_object)
    value_change_coins_list=value_change_coins(wallet_object)
    total_balance=float(available_cash)
    total_value_change_coins=0
    balance_and_change_object={}
    for symbol,added_value in updated_price_coins_list.items():
        total_balance+=added_value
    balance_and_change_object['total']=total_balance
    for symbol,change_value in value_change_coins_list.items():
        total_value_change_coins+=change_value
    balance_and_change_object['change']=total_value_change_coins
    balance_and_change_object['percentChange']=100*total_value_change_coins/total_balance
    return balance_and_change_object
