# This file is used only for testing code during development process

import os, json, globalVal
from globalVal import test_function
from datetime import datetime
from flask import Flask, render_template, redirect, request, url_for, jsonify
from flask_pymongo import PyMongo
from iexfinance.stocks import Stock, get_historical_data, get_historical_intraday
## NEW
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF, renderPM


CRYPTO_SYMBOLS=os.getenv('CRYPTO_SYMBOLS').split(",")
SYMBOL_NAMES=json.loads(os.getenv('SYMBOL_NAMES'))

# Use 'pandas' output-format for viewing data in the command line, example:
# date = datetime(2019, 5, 10)
# intraday= (get_historical_intraday("AAPL", date, output_format='pandas'))


test_dict = {'symbol': 'BTCUSDT', 'name': 'Bitcoin USD', 'short-symbol': 'BTC'}, {'symbol': 'EOSUSDT', 'name': 'EOS USD', 'short-symbol': 'EOS'}, {'symbol': 'ETHUSDT', 'name': 'Ethereum USD', 'short-symbol': 'ETH'}, {'symbol': 'BNBUSDT', 'name': 'Binance Coin USD', 'short-symbol': 'BNB'}, {'symbol': 'ONTUSDT', 'name': 'Ontology USD', 'short-symbol': 'ONT'}, {'symbol': 'BCCUSDT', 'name': 'Bitcoin Cash USD', 'short-symbol': 'BCC'}, {'symbol': 'ADAUSDT', 'name': 'Cardano USD', 'short-symbol': 'ADA'}, {'symbol': 'XRPUSDT', 'name': 'Ripple USD', 'short-symbol': 'XRP'}, {'symbol': 'TUSDUSDT', 'name': 'True USD', 'short-symbol': 'TUSD'}, {'symbol': 'TRXUSDT', 'name': 'TRON USD', 'short-symbol': 'TRX'}, {'symbol': 'LTCUSDT', 'name': 'Litecoin USD', 'short-symbol': 'LTC'}, {'symbol': 'ETCUSDT', 'name': 'Ethereum Classic USD', 'short-symbol': 'ETC'}, {'symbol': 'IOTAUSDT', 'name': 'MIOTA USD', 'short-symbol': 'IOTA'}, {'symbol': 'ICXUSDT', 'name': 'ICON USD', 'short-symbol': 'ICX'}, {'symbol': 'NEOUSDT', 'name': 'NEO USD', 'short-symbol': 'NEO'}, {'symbol': 'VENUSDT', 'name': 'VeChain USD', 'short-symbol': 'VEN'}, {'symbol': 'XLMUSDT', 'name': 'Stellar Lumens USD', 'short-symbol': 'XLM'}, {'symbol': 'QTUMUSDT', 'name': 'Qtum USD', 'short-symbol': 'QTUM'}

""" batch = Stock(CRYPTO_SYMBOLS)
quote_batch_data= batch.get_quote()

for coin_name, coin_info in quote_batch_data.items():
    for elem in SYMBOL_NAMES:
        if coin_name == elem['symbol']:
            coin_info['name'] = elem['name']"""

""" 
Create PNG files for icons of every cryptocoin like this:

for name in SYMBOL_NAMES:
    print(name['short-symbol'].lower())
    drawing = svg2rlg("./node_modules/cryptocurrency-icons/svg/color/"+name['short-symbol'].lower()+".svg")
    renderPM.drawToFile(drawing, name['short-symbol'].lower()+".png", fmt="PNG") 

new_list = ['XLM','QTUM']
for name in new_list:
    drawing = svg2rlg("./node_modules/cryptocurrency-icons/svg/color/"+name.lower()+".svg")
    renderPM.drawToFile(drawing, name.lower()+".png", fmt="PNG")

"""

print(test_function(5,10))