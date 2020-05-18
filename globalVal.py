import os
import json

os.environ['CRYPTO_SYMBOLS'] = "BTCUSDT,EOSUSDT,ETHUSDT,BNBUSDT,ONTUSDT,BCCUSDT,ADAUSDT,XRPUSDT,TUSDUSDT,TRXUSDT,LTCUSDT,ETCUSDT,IOTAUSDT,ICXUSDT,NEOUSDT,VENUSDT,XLMUSDT,QTUMUSDT"
symbols_dict = {'symbol': 'BTCUSDT', 'name': 'Bitcoin USD', 'short-symbol': 'BTC'}, {'symbol': 'EOSUSDT', 'name': 'EOS USD', 'short-symbol': 'EOS'}, {'symbol': 'ETHUSDT', 'name': 'Ethereum USD', 'short-symbol': 'ETH'}, {'symbol': 'BNBUSDT', 'name': 'Binance Coin USD', 'short-symbol': 'BNB'}, {'symbol': 'ONTUSDT', 'name': 'Ontology USD', 'short-symbol': 'ONT'}, {'symbol': 'BCCUSDT', 'name': 'Bitcoin Cash USD', 'short-symbol': 'BCC'}, {'symbol': 'ADAUSDT', 'name': 'Cardano USD', 'short-symbol': 'ADA'}, {'symbol': 'XRPUSDT', 'name': 'Ripple USD', 'short-symbol': 'XRP'}, {'symbol': 'TUSDUSDT', 'name': 'True USD', 'short-symbol': 'TUSD'}, {'symbol': 'TRXUSDT', 'name': 'TRON USD', 'short-symbol': 'TRX'}, {'symbol': 'LTCUSDT', 'name': 'Litecoin USD', 'short-symbol': 'LTC'}, {'symbol': 'ETCUSDT', 'name': 'Ethereum Classic USD', 'short-symbol': 'ETC'}, {'symbol': 'IOTAUSDT', 'name': 'MIOTA USD', 'short-symbol': 'IOTA'}, {'symbol': 'ICXUSDT', 'name': 'ICON USD', 'short-symbol': 'ICX'}, {'symbol': 'NEOUSDT', 'name': 'NEO USD', 'short-symbol': 'NEO'}, {'symbol': 'VENUSDT', 'name': 'VeChain USD', 'short-symbol': 'VEN'}, {'symbol': 'XLMUSDT', 'name': 'Stellar Lumens USD', 'short-symbol': 'XLM'}, {'symbol': 'QTUMUSDT', 'name': 'Qtum USD', 'short-symbol': 'QTUM'}
symbols_string = json.dumps(symbols_dict)
os.environ['SYMBOL_NAMES'] = symbols_string

def test_function(a,b):
    result = float(a)+float(b)
    return result