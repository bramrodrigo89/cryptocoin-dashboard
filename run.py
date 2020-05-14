import os
if os.path.exists('env.py'):
    import env
from flask import Flask, render_template, redirect, request, url_for, jsonify
from flask_pymongo import PyMongo
from iexfinance.stocks import Stock

app = Flask(__name__)
app.config["MONGO_DBNAME"] = 'cryptocoins_db'
app.config["MONGO_URI"]=os.getenv("MONGO_URI")
mongo = PyMongo(app)

@app.route('/')
@app.route('/home')
def say_hello():
    return render_template("index.html", users=mongo.db.users.find())

@app.route('/stock/<symbol>')
def get_quote(symbol):
    stock = Stock(symbol)
    quote_data= stock.get_quote()
    return render_template("quote.html", quote=quote_data)

@app.route('/crypto/<symbol>')
def get_crypto_quote(symbol):
    stock = Stock(symbol)
    quote_data= stock.get_quote()
    return render_template("crypto.html", data=quote_data)


if __name__ == '__main__':
    app.run(host=os.getenv("IP","0.0.0.0"),
        port=int(os.getenv("PORT","5000")),
        debug=True)