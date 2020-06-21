import os
from flask import Flask
import unittest
import pandas as pd
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from calculations import updated_price_coins

# MongoDB config
app = Flask(__name__)
app.config["MONGO_DBNAME"] = 'cryptocoins_db'
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.secret_key = os.getenv("SECRET_KEY")
mongo = PyMongo(app)

CRYPTOCOIN_OBJECT = mongo.db.cryptocoins.find()
CRYPTOCOINS_LIST = []
CRYPTO_SYMBOLS = []

for coin in CRYPTOCOIN_OBJECT:
    CRYPTO_SYMBOLS.append(coin['symbol_long'])
    CRYPTOCOINS_LIST.append(coin)

"""
Collections
"""

users_coll = mongo.db.users
transactions_coll = mongo.db.transactions

# Empty Wallet User example
empty_user = users_coll.find_one({'username':'anthony'})


class EmptyObjectsTestCase(unittest.TestCase):

   def testUpdatedPrices(self):
       result = updated_price_coins(empty_user['wallet'])
       self.assertEqual(result, {})

if __name__ == '__main__':
    app.run(host=os.getenv("IP","0.0.0.0"),
        port=int(os.getenv("PORT","5000")),
        debug=True)