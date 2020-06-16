import os
import json
import plotly
import plotly.graph_objs as go
import datetime
import pandas as pd
import numpy as np
from datetime import datetime
from iexfinance.stocks import Stock
from alpha_vantage.cryptocurrencies import CryptoCurrencies


def updated_price_coins(wallet_object):
    """
    This function returns a a dict {'symbol':value} of the total value of every cryptocoin
    in the user's wallet, using the formula:

    Total Value = Latest Price * Total Ticker in Wallet

    This value is used later to calculate the total balance in wallet
    """
    wallet_coins=wallet_object['coins']
    updated_price_wallet_coins={}
    for symbol,obj in wallet_coins.items():
        updated_quote=Stock(symbol)
        updated_price=float(updated_quote.get_price())*obj['total_ticker']
        updated_price_wallet_coins[symbol]=updated_price
    return updated_price_wallet_coins

def value_change_coins(wallet_object):
    """
    This function returns a dict {'symbol':value} of the value change for every cryptocoin
    in the user's wallet, using the formula:

    Value Change = (Latest Price * Total Ticker) - Previous Prices * Transaction Tickers

    So that all the previous transactions on that specific asset are considered. These 
    values ared used later to calculate the value change in the total balance.
    """
    wallet_coins=wallet_object['coins']
    value_change_coins={}
    for symbol,obj in wallet_coins.items():
        updated_quote=Stock(symbol)
        updated_price=float(updated_quote.get_price())
        total_value_updated=updated_price*obj['total_ticker']
        value_change=total_value_updated
        for transaction in obj['transactions']:
            value_change-=float(transaction['ticker'])*float(transaction['price'])
        value_change_coins[symbol]=value_change
    return value_change_coins

def balance_prices_and_changes(wallet_object,available_cash):
    """
    This function returns an object with information about the in the user's wallet. 
    The returned values of the previous functions are added up and returned here as
    Balance_Object = { 'total': value, 'change':value, 'percent':value }

    The objects returned from the two functions defined before are returned again to be
    passed into the following calculationsf, in order to avoid calling Stock.get_quote() 
    which produces slightly different cryptocoin prices every second it is called. 

    """
    updated_price_coins_obj=updated_price_coins(wallet_object)
    value_change_coins_obj=value_change_coins(wallet_object)
    total_balance=float(available_cash)
    total_value_change_coins=0
    balance_and_change_object={}
    for symbol,added_value in updated_price_coins_obj.items():
        total_balance+=added_value
    balance_and_change_object['total']=total_balance
    for symbol,change_value in value_change_coins_obj.items():
        total_value_change_coins+=change_value
    balance_and_change_object['change']=total_value_change_coins
    balance_and_change_object['percentChange']=100*total_value_change_coins/total_balance
    return balance_and_change_object, updated_price_coins_obj, value_change_coins_obj

def fetch_wallet_coins_data(updated_price_obj, value_change_obj, wallet_object, db_cryptocoin_obj):
    """
    This function produces the object used for "My Crypto Wallet" section. The same updated
    prices and value changes from the previous functions are inserted here again to produce
    a new dict with this content for every coin in the user's wallet. :

    {'symbol':{'name':str, 'symbol_short':str, 'balance':value, 'value_change':value, 
    'change_percent':value, 'total_ticker':value }}

    In the case that the user only has one coin in wallet, the value insertion is assigned 
    first in a different manner. If there are no coins in wallet, an empty object is returned

    """
    wallet_coins=wallet_object['coins']
    wallet_coins_list=[]
    for symbol,obj in wallet_coins.items():
        wallet_coins_list.append(symbol)
    #Check if user's wallet has no coins
    if wallet_coins_list==[]:
        empty_object={}
        return empty_object
    # Check if user's wallet cointains only one coin
    elif len(wallet_coins_list)==1:
        crypto = Stock(wallet_coins_list)
        wallet_coin_info= crypto.get_quote()
        for elem in db_cryptocoin_obj:
            if wallet_coin_info['symbol'] == elem['symbol_long']:
                wallet_coin_info['name'] = elem['name']
                wallet_coin_info['symbol_short'] = elem['symbol_short']
        wallet_coin_info['balance']=updated_price_obj[wallet_coin_info['symbol']]
        wallet_coin_info['value_change']=value_change_obj[wallet_coin_info['symbol']]
        wallet_coin_info['value_change_percent']=100*wallet_coin_info['value_change']/wallet_coin_info['balance']
        for symbol,obj in wallet_coins.items():
            wallet_coin_info['total_ticker']=obj['total_ticker']
        wallet_coin_object={}
        wallet_coin_object[wallet_coin_info['symbol']]=wallet_coin_info
        return wallet_coin_object
    # User's wallet cointains multiple coins
    else:
        cryptobatch = Stock(wallet_coins_list)
        wallet_coins_object= cryptobatch.get_quote()
        for coin_symbol, coin_info in wallet_coins_object.items():
            for elem in db_cryptocoin_obj:
                if coin_symbol == elem['symbol_long']:
                    coin_info['name'] = elem['name']
                    coin_info['symbol_short'] = elem['symbol_short']
            for symbol,balance in updated_price_obj.items():
                if coin_symbol == symbol:
                    coin_info['balance']= balance
            for symbol,change in value_change_obj.items():
                if coin_symbol == symbol:
                    coin_info['value_change']= change
                    coin_info['value_change_percent']=100*change/coin_info['balance']
            for symbol,obj in wallet_coins.items():
                if coin_symbol == symbol:
                    coin_info['total_ticker']=obj['total_ticker']
        return wallet_coins_object

def create_pie_chart(updated_price_obj,user_object,cryptocoin_db):
    """
    This function produces a JSON object to create a pie diagram of the wallet's
    coins distribution and calculates proportions. It also considers the available cash
    as the first element in the list. 

    """
    cash_value=user_object['cash']
    user_wallet=user_object['wallet']
    pie_labels=['Available Cash']
    pie_values=[cash_value]
    for coin,value in updated_price_obj.items():
        # pie_labels.append(coin)
        pie_values.append(float(value))
        for elem in cryptocoin_db:
            if coin == elem['symbol_long']:
                coin_name=elem['name'].replace(' USD','')
                pie_labels.append(coin_name)
    data_pie=[go.Pie(labels=pie_labels, values=pie_values, hole=.5)]
    graphJSON = json.dumps(data_pie, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def create_line_chart(user_object):
    """
    This function creates a line chart for the user's wallet performance. It querries
    the user's wallet and calls the API Alpha Vantage in order to get historical data
    of those specific cryptocurrencies. The values are filtered to only those 
    after the coins have been purchased for the first time. For simplicity purposes, 
    it assumes A CONSTANT TICKER DURING THE WHOLE TIME PERIOD. 

    """

    # Alpha Vantage
    Alpha_Vantage_Key = os.getenv("ALPHAVANTAGE_API_KEY")
    cc = CryptoCurrencies(Alpha_Vantage_Key)


    # Fetching historical data for specific coins in user's wallet
    user_wallet=user_object['wallet']
    wallet_coins=user_wallet['coins']
    coins_obj={}
    for coin,obj in wallet_coins.items():
        symbol=coin.replace('USDT','')
        coins_obj[coin] = {}
        ticker= obj['total_ticker']
        coins_obj[coin]['ticker'] = ticker
        start_date = pd.to_datetime(obj['transactions'][0]['date'])
        coins_obj[coin]['coin_name'] = obj['transactions'][0]['name']
        coins_obj[coin]['start_date'] = start_date

        #API Call for every coin in wallet, market is set to United States US$
        cc_data, meta_data = cc.get_digital_currency_daily(symbol=symbol, market='USD')

        filter_data={}
        for date,data in cc_data.items():
            date = pd.to_datetime(date)
            # Filter only relevant values by date and calculate total value
            if date >= start_date:
                filter_data[date]=float(data['4b. close (USD)'])*ticker
        coins_obj[coin]['historical_data']=filter_data


    # Plotly line chart initiation
    figure = go.Figure()

    # Add data to figure
    for coin,info in coins_obj.items():
        historical_data=info['historical_data']
        coin_name=info['coin_name']
        labels=[]
        values=[]
        for time,value in historical_data.items():
            labels.append(time)
            values.append(value)
        trace = go.Scatter(
            x = labels,
            y = values,
            mode = 'lines',
            name = coin_name
        )
        figure.add_trace(trace)

    # Edit the layout
    figure.update_layout(title='My CryptoWallet Performance',
                    xaxis_title='Month',
                    yaxis_title='Total value (US$)')
                
    # Json the data to be parsed later onto the html template. 
    graphJSON = json.dumps(figure, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def favorite_list_data(user_object,wallet_coins_object,db_cryptocoin_obj):
    """
    This functions creates an object with data for creating cards only for favorite
    coins which are watched by the user. It discards the coins that are not in the favorite list
    """
    favorite_list=user_object['favorites']
    if favorite_list == '':
        return False
    elif favorite_list != '':
        favorite_list_data={}
        if len(favorite_list)==1:
            favorite_tuple=favorite_list
        elif len(favorite_list)>1:
            favorite_tuple=favorite_list.split(",")
        for favorite in favorite_tuple:
            for coin_symbol, coin_info in wallet_coins_object.items():
                if favorite == coin_symbol:
                    favorite_list_data[coin_symbol]=coin_info
            if favorite not in wallet_coins_object.keys():
                new_quote_favorite=Stock(favorite)
                quote_favorite_data=new_quote_favorite.get_quote()
                favorite_list_data[favorite]=quote_favorite_data
                for elem in db_cryptocoin_obj:
                    if favorite == elem['symbol_long']:
                        favorite_list_data[favorite]['name'] = elem['name']
                        favorite_list_data[favorite]['symbol_short'] = elem['symbol_short']
        return favorite_list_data

def not_favorite_list_data(user_object,db_cryptocoin_obj):
    """
    This functions creates an object with data for creating cards only for NOT favorite
    coins that are NOT watched by the user. It discards the coins that ARE in the favorite list
    """
    favorite_list=user_object['favorites']
    favorite_tuple=favorite_list.split(",")
    not_favorite_tuple=[]
    not_favorite_data={}
    for elem in db_cryptocoin_obj:
        not_favorite_tuple.append(elem['symbol_long'])
    for favorite in favorite_tuple:
            if favorite in not_favorite_tuple:
                not_favorite_tuple.remove(favorite)
    new_quote_batch=Stock(not_favorite_tuple)
    not_favorite_data=new_quote_batch.get_quote()
    for elem in db_cryptocoin_obj:
        for coin in not_favorite_data.keys():
            if coin == elem['symbol_long']:
                not_favorite_data[coin]['name'] = elem['name']
                not_favorite_data[coin]['symbol_short'] = elem['symbol_short']
    return not_favorite_data