
def calculate_balance(wallet_object,available_cash):
    for cryptocoin in wallet_object:
        total_ticker=0
        total_balance_toAdd=0
        for transaction in cryptocoin:
            print(transaction.items())
            total_ticker+=transaction.ticker
            total_balance_toAdd+=transaction.ticker*transaction.price
        print('Total ticker Crypto: '+total_ticker)
        print('Total balance to add for this crypto: '+ total_balance_toAdd)
        print('Available cash: '+available_cash)