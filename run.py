import os, json, globalVal
from datetime import datetime
from flask import Flask, render_template, redirect, request, url_for, jsonify
from flask_pymongo import PyMongo
from iexfinance.stocks import Stock, get_historical_data

app = Flask(__name__)
app.config["MONGO_DBNAME"] = 'cryptocoins_db'
app.config["MONGO_URI"]=os.getenv("MONGO_URI")
CRYPTO_SYMBOLS=os.getenv('CRYPTO_SYMBOLS').split(",")
SYMBOL_NAMES=json.loads(os.getenv('SYMBOL_NAMES'))

mongo = PyMongo(app)

@app.route('/')
@app.route('/home')
def say_hello():
    batch = Stock(CRYPTO_SYMBOLS)
    quote_batch_data= batch.get_quote()
    return render_template("crypto.html", users=mongo.db.users.find(), data=quote_batch_data)

@app.route('/crypto/<symbol>')
def get_crypto_quote(symbol):
    stock = Stock(symbol)
    quote_data= stock.get_quote()
    return render_template("crypto.html", data=quote_data)


if __name__ == '__main__':
    app.run(host=os.getenv("IP","0.0.0.0"),
        port=int(os.getenv("PORT","5000")),
        debug=True)