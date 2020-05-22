import os, json, locale
import pandas as pd
import numpy as np
import plotly
import plotly.graph_objs as go #Pie Chart
from datetime import datetime
from flask import Flask, render_template, redirect, request, url_for, jsonify
from flask_pymongo import PyMongo
from iexfinance.stocks import Stock, get_historical_data
from calculations import updated_price_coins, value_change_coins, calculate_balance_and_change, create_plot

app = Flask(__name__)

app.config["MONGO_DBNAME"] = 'cryptocoins_db'
app.config["MONGO_URI"]=os.getenv("MONGO_URI")
mongo = PyMongo(app)

cryptocoin_objects=mongo.db.cryptocoins.find()
CRYPTOCOINS_LIST=[]
CRYPTO_SYMBOLS=[]

for coin in cryptocoin_objects:
    CRYPTO_SYMBOLS.append(coin['symbol_long'])
    CRYPTOCOINS_LIST.append(coin)

@app.route('/')
@app.route('/user/<user>/dashboard')
def show_user_dashboard():
    user_data=mongo.db.users.find_one({'username':'bramrodrigo89'})
    cryptobatch = Stock(CRYPTO_SYMBOLS)
    quote_batch_data= cryptobatch.get_quote()
    for coin_name, coin_info in quote_batch_data.items():
        for elem in CRYPTOCOINS_LIST:
            if coin_name == elem['symbol_long']:
                coin_info['name'] = elem['name']

    pie_data = create_plot(user_data)
    balance_data=calculate_balance_and_change(user_data['wallet'],user_data['cash'])
    return render_template("dashboard.html", user=user_data, balance=balance_data, plot=pie_data, data=quote_batch_data)


if __name__ == '__main__':
    app.run(host=os.getenv("IP","0.0.0.0"),
        port=int(os.getenv("PORT","5000")),
        debug=True)