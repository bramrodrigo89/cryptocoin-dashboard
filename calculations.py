import os, json, locale
import pandas as pd
import numpy as np
import plotly
import plotly.graph_objs as go #Pie Chart
from datetime import datetime
from flask import Flask, render_template, redirect, request, url_for, jsonify
from flask_pymongo import PyMongo
from iexfinance.stocks import Stock, get_historical_data

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

def fetch_wallet_coins_data(wallet_object,db_cryptocoin_list):
    updated_price_wallet_coins=updated_price_coins(wallet_object)
    wallet_coins=wallet_object['coins']
    wallet_coins_list=[]
    for symbol,obj in wallet_coins.items():
        wallet_coins_list.append(symbol+'USDT')
    cryptobatch = Stock(wallet_coins_list)
    quote_batch_data= cryptobatch.get_quote()
    for coin_name, coin_info in quote_batch_data.items():
        for elem in db_cryptocoin_list:
            if coin_name == elem['symbol_long']:
                coin_info['name'] = elem['name']
    return quote_batch_data

def create_plot(user_object):
    cash_value=user_object['cash']
    user_wallet=user_object['wallet']
    updated_price_coins_list=updated_price_coins(user_wallet)
    pie_labels=['Available Cash']
    pie_values=[cash_value]
    for coin,value in updated_price_coins_list.items():
        pie_labels.append(coin)
        pie_values.append(float(value))
    labels = ['Oxygen','Hydrogen','Carbon_Dioxide','Nitrogen']
    values = [4500, 2500, 1053, 500]
    data_pie=[go.Pie(labels=pie_labels, values=pie_values, hole=.3)]
    graphJSON = json.dumps(data_pie, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON