
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