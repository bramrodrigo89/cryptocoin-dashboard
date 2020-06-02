import os, json, locale
import pandas as pd
import numpy as np
import plotly
import plotly.graph_objs as go #Pie Chart
from flask import Flask, render_template, redirect, request, url_for, jsonify
from flask_pymongo import PyMongo
from pymongo.mongo_client import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
from iexfinance.stocks import Stock, get_historical_data

def prepare_buy_object(form_object,user_data):
    document_object = {}
    document_object["user_id"]=user_data["_id"]
    document_object["symbol"]=form_object["submit-buy-coin-symbol"]
    document_object["name"]=form_object["submit-buy-coin-name"]
    document_object["type"]="purchase"
    now = datetime.utcnow()
    document_object["date"]=datetime.utcnow()
    document_object["ticker"]=float(form_object["ticket-entry-number"])
    document_object["price"]=float(form_object["submit-buy-coin-bid-price"].replace('US$ ',''))
    return document_object

def insert_transaction_to_db(mongo,new_doc,user_data):
    user_id=user_data['_id']
    transactions=mongo.db.transactions
    inserted_doc=transactions.insert_one(new_doc)
    new_coin=new_doc['symbol']
    new_ticker=new_doc['ticker']
    latest_id= inserted_doc.inserted_id
    latest_transaction=mongo.db.transactions.find_one({'_id': latest_id})
    user_wallet=user_data['wallet']
    current_coins_number=float(user_wallet['total_coins'])
    user_coins=user_wallet['coins']
    if new_coin in user_coins:
        mongo.db.users.update(
            { '_id' : ObjectId(user_id) },
            { '$push' : { 'wallet.coins.'+new_coin+'.transactions' : latest_transaction }
        })
        current_ticker=float(user_coins[new_coin]['total_ticker'])
        mongo.db.users.update(
            { '_id' : ObjectId(user_id) },
            { '$set' : { 'wallet.coins.'+new_coin+'.total_ticker' : current_ticker + new_ticker }
        })
        return
    else:
        mongo.db.users.update(
            { '_id' : ObjectId(user_id) },
            { '$set' : { 'wallet.coins.'+new_coin : { 'symbol':new_coin, 'total_ticker' : new_doc['ticker'], 'transactions': [latest_transaction] }}
            })
        mongo.db.users.update(
            { '_id' : ObjectId(user_id) },
            { '$set' : { 'wallet.total_coins' : current_coins_number+1 }
            })
        return
