import os, json, locale
import pandas as pd
import numpy as np
import plotly
import plotly.graph_objs as go #Pie Chart
from datetime import datetime
from flask import Flask, render_template, redirect, request, url_for, jsonify, send_from_directory
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from iexfinance.stocks import Stock, get_historical_data
from calculations import updated_price_coins, value_change_coins, balance_prices_and_changes, create_plot, fetch_wallet_coins_data, favorite_list_data, not_favorite_list_data

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
@app.route('/favicon.ico') 
def favicon(): 
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    
@app.route('/')
@app.route('/user/<username>/dashboard')
def show_user_dashboard(username):
    user_data=mongo.db.users.find_one({'username':username})
    user_id=user_data['_id']
    data=balance_prices_and_changes(user_data['wallet'],user_data['cash'])
    balance_data, updated_prices, updated_changes = data[0], data[1], data[2]
    wallet_coins_data=fetch_wallet_coins_data(updated_prices, updated_changes, user_data['wallet'],CRYPTOCOINS_LIST)
    pie_data = create_plot(updated_prices,user_data)
    favorites=favorite_list_data(user_data,wallet_coins_data,CRYPTOCOINS_LIST)
    not_favorites = not_favorite_list_data(user_data,CRYPTOCOINS_LIST)
    user_transactions=mongo.db.transactions.find({'user_id': ObjectId(user_id)}).limit(5)
    return render_template("dashboard.html", user=user_data, balance=balance_data, plot=pie_data, wallet_coins=wallet_coins_data ,favorites=favorites, not_favorites=not_favorites, transactions=user_transactions)

@app.route('/remove-fav/<username>/<symbol>')
def remove_favorite(username, symbol):
    user_data=mongo.db.users.find_one({'username':username})
    favorites_list=user_data['favorites'].split(",")
    favorites_list.remove(symbol)
    updated_favorites_list=(','.join(favorites_list))
    mongo.db.users.update({'username':username},{'$set':{"favorites":updated_favorites_list}},multi=False)
    return redirect(url_for('show_user_dashboard',username=username))

@app.route('/add-fav/<username>/<symbol>')
def add_favorite(username, symbol):
    user_data=mongo.db.users.find_one({'username':username})
    favorites_list=user_data['favorites'].split(",")
    favorites_list.append(symbol)
    updated_favorites_list=(','.join(favorites_list))
    mongo.db.users.update({'username':username},{'$set':{"favorites":updated_favorites_list}},multi=False)
    return redirect(url_for('show_user_dashboard',username=username))

@app.route('/buy-new-coin/<username>', methods=['POST'])
def buy_coins(username):
    result = request.form.to_dict()
    return redirect(url_for('show_user_dashboard',username=username))
    #task_collection=mongo.db.tasks
    #task_collection.insert_one(request.form.to_dict())
    #return redirect(url_for('get_tasks'))

if __name__ == '__main__':
    app.run(host=os.getenv("IP","0.0.0.0"),
        port=int(os.getenv("PORT","5000")),
        debug=True)