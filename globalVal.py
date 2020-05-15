import os
import json

os.environ['CRYPTO_SYMBOLS'] = "BTCUSDT,EOSUSDT,ETHUSDT,BNBUSDT,ONTUSDT,BCCUSDT,ADAUSDT,XRPUSDT,TUSDUSDT,TRXUSDT,LTCUSDT,ETCUSDT,IOTAUSDT,ICXUSDT,NEOUSDT,VENUSDT,XLMUSDT,QTUMUSDT"
symbols_dict = {'symbol':'BTCUSDT','name':'Bitcoin USD'},{'symbol':'EOSUSDT','name':'EOS USD'},{'symbol':'ETHUSDT','name':'Ethereum USD'},{'symbol':'BNBUSDT','name':'Binance Coin USD'},{'symbol':'ONTUSDT','name':'Ontology USD'},{'symbol':'BCCUSDT','name':'Bitcoin Cash USD'},{'symbol':'ADAUSDT','name':'Cardano USD'},{'symbol':'XRPUSDT','name':'Ripple USD'},{'symbol':'TUSDUSDT','name':'True USD'},{'symbol':'TRXUSDT','name':'TRON USD'},{'symbol':'LTCUSDT','name':'Litecoin USD'},{'symbol':'ETCUSDT','name':'Ethereum Classic USD'},{'symbol':'IOTAUSDT','name':'MIOTA USD'},{'symbol':'ICXUSDT','name':'ICON USD'},{'symbol':'NEOUSDT','name':'NEO USD'},{'symbol':'VENUSDT','name':'VeChain USD'},{'symbol':'XLMUSDT','name':'Stellar Lumens USD'},{'symbol':'QTUMUSDT','name':'Qtum USD'}

symbols_string = json.dumps(symbols_dict)
os.environ['SYMBOL_NAMES'] = symbols_string