import json
import plotly
import plotly.graph_objs as go
from datetime import datetime
from iexfinance.stocks import Stock, get_historical_data
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
# Trying Alpha Vantage
key = 'A4XH6LOM4M6ZABPE'
ts = TimeSeries(key)
ti = TechIndicators(key)
btc, meta = ts.get_daily(symbol='BTC')
print(btc)


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

def create_pie_chart(updated_price_obj,user_object):
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
        pie_labels.append(coin)
        pie_values.append(float(value))
    data_pie=[go.Pie(labels=pie_labels, values=pie_values, hole=.3)]
    graphJSON = json.dumps(data_pie, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def create_line_chart(user_object):
    """
    This function ...

    """
    user_wallet=user_object['wallet']
    wallet_coins=user_wallet['coins']
    coins_list=[]
    labels=[]
    values=[]
    for coin,obj in wallet_coins.items():
        coins_list.append(coin)

    
    start = datetime(2020, 5, 1)
    end = datetime(2020, 6, 1)
    df = get_historical_data("BTCUSDT", start, end)
    print(df)
    
    # data_plot=[go.Pie(labels=labels, values=values, hole=.3)]
    # graphJSON = json.dumps(data_plot, cls=plotly.utils.PlotlyJSONEncoder)
    # return graphJSON

    #example

    # Add data
    # month = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
    #          'August', 'September', 'October', 'November', 'December']
    # high_2000 = [32.5, 37.6, 49.9, 53.0, 69.1, 75.4, 76.5, 76.6, 70.7, 60.6, 45.1, 29.3]
    # low_2000 = [13.8, 22.3, 32.5, 37.2, 49.9, 56.1, 57.7, 58.3, 51.2, 42.8, 31.6, 15.9]
    # high_2007 = [36.5, 26.6, 43.6, 52.3, 71.5, 81.4, 80.5, 82.2, 76.0, 67.3, 46.1, 35.0]
    # low_2007 = [23.6, 14.0, 27.0, 36.8, 47.6, 57.7, 58.9, 61.2, 53.3, 48.5, 31.0, 23.6]
    # high_2014 = [28.8, 28.5, 37.0, 56.8, 69.7, 79.7, 78.5, 77.8, 74.1, 62.6, 45.3, 39.9]
    # low_2014 = [12.7, 14.3, 18.6, 35.5, 49.9, 58.0, 60.0, 58.6, 51.7, 45.2, 32.2, 29.1]

    # fig = go.Figure()
    # # Create and style traces
    # fig.add_trace(go.Scatter(x=month, y=high_2014, name='High 2014',
    #                          line=dict(color='firebrick', width=4)))
    # fig.add_trace(go.Scatter(x=month, y=low_2014, name = 'Low 2014',
    #                          line=dict(color='royalblue', width=4)))
    # fig.add_trace(go.Scatter(x=month, y=high_2007, name='High 2007',
    #                          line=dict(color='firebrick', width=4,
    #                               dash='dash') # dash options include 'dash', 'dot', and 'dashdot'
    # ))
    # fig.add_trace(go.Scatter(x=month, y=low_2007, name='Low 2007',
    #                          line = dict(color='royalblue', width=4, dash='dash')))
    # fig.add_trace(go.Scatter(x=month, y=high_2000, name='High 2000',
    #                          line = dict(color='firebrick', width=4, dash='dot')))
    # fig.add_trace(go.Scatter(x=month, y=low_2000, name='Low 2000',
    #                          line=dict(color='royalblue', width=4, dash='dot')))

    # # Edit the layout
    # fig.update_layout(title='Average High and Low Temperatures in New York',
    #                    xaxis_title='Month',
    #                    yaxis_title='Temperature (degrees F)')


    # fig.show()

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