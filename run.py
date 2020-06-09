import os, json, locale
import numpy as np
import plotly
import plotly.graph_objs as go
from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager
from flask import render_template, url_for, request, flash, redirect
from form import Login
from werkzeug.urls import url_parse
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_user, logout_user, login_required
from pymongo.mongo_client import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
from iexfinance.stocks import Stock, get_historical_data
from calculations import updated_price_coins, value_change_coins, balance_prices_and_changes, create_plot, fetch_wallet_coins_data, favorite_list_data, not_favorite_list_data
from transactions import prepare_buy_object, prepare_sell_object, insert_transaction_to_db

app = Flask(__name__)
app.config["MONGO_DBNAME"] = 'cryptocoins_db'
app.config["MONGO_URI"]=os.getenv("MONGO_URI")
app.secret_key = 'some_secret'
mongo = PyMongo(app)
login = LoginManager(app)
login.login_view = 'login'

CRYPTOCOIN_OBJECT=mongo.db.cryptocoins.find()
CRYPTOCOINS_LIST=[]
CRYPTO_SYMBOLS=[]

for coin in CRYPTOCOIN_OBJECT:
    CRYPTO_SYMBOLS.append(coin['symbol_long'])
    CRYPTOCOINS_LIST.append(coin)

class User:
    def __init__(self, username):
        self.username = username

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.username

    @staticmethod
    def check_password(password_hash, password):
        return check_password_hash(password_hash, password)

    @login.user_loader
    def load_user(username):
        u = mongo.db.users.find_one({"username": username})
        if not u:
            return None
        return User(username=u['userame'])

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('show_user_dashboard',username=username))
        form = Login()
        if form.validate_on_submit():
            user = mongo.db.users.find_one({"username": form.username.data})
            if user and User.check_password(user['password'], form.password.data):
                user_obj = User(username=user['userame'])
                login_user(user_obj)
                next_page = request.args.get('next')
                if not next_page or url_parse(next_page).netloc != '':
                    next_page = url_for('show_user_dashboard', username=user['username'])
                return redirect(next_page)
            else:
                flash("Invalid username or password")
        return render_template('login.html', title='Sign In', form=form)
    
    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('login'))
    
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/user/<username>/dashboard')
def show_user_dashboard(username):
    user_data=mongo.db.users.find_one({'username':username})
    user_id=user_data['_id']
    data=balance_prices_and_changes(user_data['wallet'],user_data['cash'])
    balance_data, updated_prices, updated_changes = data[0], data[1], data[2]
    wallet_coins_data=fetch_wallet_coins_data(updated_prices, updated_changes, user_data['wallet'],CRYPTOCOINS_LIST)
    pie_data = create_plot(updated_prices,user_data)
    favorites = favorite_list_data(user_data,wallet_coins_data,CRYPTOCOINS_LIST)
    not_favorites = not_favorite_list_data(user_data,CRYPTOCOINS_LIST)
    user_transactions = mongo.db.transactions.find({'user_id': ObjectId(user_id)}).sort([("date", -1)]).limit(5)
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

@app.route('/buy-coins/<username>', methods=['POST'])
def buy_coins(username):
    submitted_form = request.form.to_dict()
    user_data=mongo.db.users.find_one({'username':username})
    new_doc = prepare_buy_object(submitted_form,user_data)
    insert_transaction_to_db(mongo, new_doc,user_data)
    return redirect(url_for('show_user_dashboard',username=username))

@app.route('/sell-coins/<username>', methods=['POST'])
def sell_coins(username):
    submitted_form = request.form.to_dict()
    user_data=mongo.db.users.find_one({'username':username})
    new_doc = prepare_sell_object(submitted_form,user_data)
    insert_transaction_to_db(mongo, new_doc,user_data)
    return redirect(url_for('show_user_dashboard',username=username))

if __name__ == '__main__':
    app.run(host=os.getenv("IP","0.0.0.0"),
        port=int(os.getenv("PORT","5000")),
        debug=True)