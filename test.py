# This file is used only for testing code during development process

import os, json, globalVal
from datetime import datetime
from flask import Flask, render_template, redirect, request, url_for, jsonify
from flask_pymongo import PyMongo
from iexfinance.stocks import Stock, get_historical_data, get_historical_intraday


date = datetime(2019, 5, 10)
print(get_historical_intraday("AAPL", date, output_format='pandas'))
