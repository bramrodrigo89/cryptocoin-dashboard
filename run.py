import os, json, locale
import pandas as pd
import numpy as np
import plotly
import plotly.graph_objs as go #Pie Chart
from datetime import datetime
from flask import Flask, render_template, redirect, request, url_for, jsonify
from flask_pymongo import PyMongo
from iexfinance.stocks import Stock, get_historical_data
from calculations import updated_price_coins, value_change_coins, balance_prices_and_changes, create_plot, fetch_wallet_coins_data, favorite_list_data

app = Flask(__name__)

app.config["MONGO_DBNAME"] = 'cryptocoins_db'
app.config["MONGO_URI"]=os.getenv("MONGO_URI")
mongo = PyMongo(app)

CRYPTOCOIN_OBJECT=mongo.db.cryptocoins.find()
CRYPTOCOINS_LIST=[]
CRYPTO_SYMBOLS=[]

for coin in CRYPTOCOIN_OBJECT:
    CRYPTO_SYMBOLS.append(coin['symbol_long'])
    CRYPTOCOINS_LIST.append(coin)

@app.route('/')
@app.route('/user/<username>/dashboard')
def show_user_dashboard(username):
    user_data=mongo.db.users.find_one({'username':username})
    data=balance_prices_and_changes(user_data['wallet'],user_data['cash'])
    balance_data, updated_prices, updated_changes = data[0], data[1], data[2]
    wallet_coins_data=fetch_wallet_coins_data(updated_prices, updated_changes, user_data['wallet'],CRYPTOCOINS_LIST)
    pie_data = create_plot(updated_prices,user_data)
    favorites_data=favorite_list_data(user_data,wallet_coins_data,CRYPTOCOINS_LIST)
    return render_template("dashboard.html", user=user_data, balance=balance_data, plot=pie_data, wallet_coins=wallet_coins_data ,favorites=favorites_data)

@app.route('/remove-fav/<username>/<symbol>')
def remove_favorite(username, symbol):
    user_data=mongo.db.users.find_one({'username':username})
    favorites_list=user_data['favorites'].split(",")
    favorites_list.remove(symbol)
    updated_favorites_list=(','.join(favorites_list))
    mongo.db.users.update( {'username': username}, {'favorites':updated_favorites_list})
    return redirect(url_for('show_user_dashboard',username=username))

if __name__ == '__main__':
    app.run(host=os.getenv("IP","0.0.0.0"),
        port=int(os.getenv("PORT","5000")),
        debug=True)