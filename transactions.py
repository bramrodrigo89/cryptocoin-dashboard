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
    # datetime object containing current date and time
    
    return document_object
