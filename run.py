import os, json, globalVal, locale
import pandas as pd
import numpy as np
import plotly
import plotly.graph_objs as go

from datetime import datetime
from flask import Flask, render_template, redirect, request, url_for, jsonify
from flask_pymongo import PyMongo
from iexfinance.stocks import Stock, get_historical_data
from calculations import updated_price_coins, value_change_coins, calculate_balance_and_change

app = Flask(__name__)

app.config["MONGO_DBNAME"] = 'cryptocoins_db'
app.config["MONGO_URI"]=os.getenv("MONGO_URI")
mongo = PyMongo(app)

CRYPTO_SYMBOLS=os.getenv('CRYPTO_SYMBOLS').split(",")
SYMBOL_NAMES=json.loads(os.getenv('SYMBOL_NAMES'))

def create_plot():
    N = 40
    x = np.linspace(0, 1, N)
    y = np.random.randn(N)
    df = pd.DataFrame({'x': x, 'y': y}) # creating a sample dataframe
    data = [
        go.Bar(
            x=df['x'], # assign x as the dataframe column 'x'
            y=df['y']
        )
    ]
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

@app.route('/')
@app.route('/user/<user>/dashboard')
def show_dashboard():
    user_data=mongo.db.users.find_one({'username':'bramrodrigo89'})
    cryptobatch = Stock(CRYPTO_SYMBOLS)
    quote_batch_data= cryptobatch.get_quote()

    bar = create_plot()

    for coin_name, coin_info in quote_batch_data.items():
        for elem in SYMBOL_NAMES:
            if coin_name == elem['symbol']:
                coin_info['name'] = elem['name']

    balance_data=calculate_balance_and_change(user_data['wallet'],user_data['cash'])
    return render_template("dashboard.html", user=user_data, balance=balance_data, plot=bar, data=quote_batch_data)


if __name__ == '__main__':
    app.run(host=os.getenv("IP","0.0.0.0"),
        port=int(os.getenv("PORT","5000")),
        debug=True)