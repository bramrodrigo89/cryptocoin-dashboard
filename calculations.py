import json
import plotly
import plotly.graph_objs as go
from iexfinance.stocks import Stock, get_historical_data


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

def create_plot(updated_price_obj,user_object):
    """
    This function ...

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