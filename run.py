import os
from flask import Flask
from datetime import datetime
from flask_pymongo import PyMongo
import pandas as pd
from flask import render_template, url_for, request, flash, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from calculations import balance_prices_and_changes, create_pie_chart
from calculations import create_line_chart, calculate_users_rank
from calculations import fetch_wallet_coins_data, favorite_list_data
from calculations import not_favorite_list_data
from transactions import prepare_buy_object, prepare_sell_object
from transactions import insert_transaction_to_db, get_user_transactions

"""
app config
"""

app = Flask(__name__)

# MongoDB config
app.config["MONGO_DBNAME"] = 'cryptocoins_db'
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.secret_key = os.getenv("SECRET_KEY")
mongo = PyMongo(app)

"""
constants
"""

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
    

"""
Index Page
"""

@app.route('/')
@app.route('/index')
def index():
    # Check if user is logged in already in session
    if 'user' in session:
        user_in_db = users_coll.find_one({"username": session['user']})
        return render_template('index.html', user=user_in_db)
    # If user is not logged, redirect to index page
    else:
        return render_template("index.html")

"""
User Authentication, Log In and Log Out
"""

# Login page with login form
@app.route('/login', methods=['GET'])
def login():
	# Check if user is logged in already in session
	if 'user' in session:
		user_in_db = users_coll.find_one({"username": session['user']})
		if user_in_db:
			# If so redirect to user's profile
			flash("You are logged in already!")
			return redirect(url_for('profile', username=user_in_db['username']))
	elif 'user' not in session:
		# Otherwise render login page for user to log in again
		return render_template("login.html")

# Check user login data when form is submitted from login.html
@app.route('/user_auth', methods=['POST'])
def user_auth():
    form = request.form.to_dict()
    user_in_db = users_coll.find_one({'username': form['username']})
    # Check if username exists in database and password is correct
    if user_in_db:
        if check_password_hash(user_in_db['password'], form['password']):
            # Save username in session and confirm successful login
            session['user'] = form['username']
            flash('You logged in successfully!')
            return redirect(url_for('profile', username=user_in_db['username']))
        else:
            # Password or username incorrect
            flash('Invalid password or username')
            return redirect(url_for('login'))
    else:
        #User does not exist and sign up is requirec, redirect to signup.html
        flash('Please sign up first to create an account')
        return redirect(url_for('signup'))

# Log Out
@app.route('/logout')
def logout():
	# Clear the session before logout
	session.clear()
	flash('You have logged out!')
	return redirect(url_for('index'))

"""
Signing up
"""

@app.route('/signup', methods=['GET', 'POST'])
def signup():
	# Check if user is already logged in
	if 'user' in session:
		flash("You are logged in already!")
		return redirect(url_for('index'))
	if request.method == 'POST':
		form = request.form.to_dict()
		# Check if the two password entries match and if user already exists first 
		if form['password1'] == form['password2']:
			user = users_coll.find_one({"username" : form['username']})
			if user:
				flash(f"{form['username']} already exists! Please use a different username or log in again")
				return redirect(url_for('signup'))
			# If user does not exist register new user
			else:				
				# Hash password
				hash_pass = generate_password_hash(form['password1'])
				#Create new user with hashed password
				users_coll.insert_one(
					{
						'username': form['username'],
                        'password': hash_pass,
						'profile': {
                            'first_name': form['first_name'],
                            'last_name': form['last_name'],
                            'dob': pd.to_datetime(form['dob']),
                            'email_address': form['email_address'],
                            'date_joined': datetime.utcnow(),
                            'image': 'http://lorempixel.com/100/150/abstract/1/'+form['first_name']
                        },
                        'wallet': {
                            'total_coins':0,
                            'coins': {}
                        },
                        'cash':5000.00,
                        'cash_earned':0.00,
                        'favorites':""
					}
				)
				# Check if user was saved in database
				user_in_db = users_coll.find_one({"username": form['username']})
				if user_in_db:
					# Log user in and add user to session right away
					session['user'] = user_in_db['username']
					return redirect(url_for('profile', username=session['user']))
				else:
					flash("There was a problem saving your profile. Please try again.")
					return redirect(url_for('signup'))
		else:
			flash("Passwords do not match! Please try again")
			return redirect(url_for('signup'))
	return render_template("signup.html")


"""
User Profile
"""
# Profile Page
@app.route('/profile/<username>')
def profile(username): 
    if 'user' in session and session['user']==username:
        user_in_db = users_coll.find_one({"username": username})
        string_list=[]
        for n in range(10):
            string_list.append(str(n))
        user_image_url=user_in_db['profile']['image']
        user_image=user_image_url[39:][0]
        user_image_number=str(int(user_image)-1)
        return render_template('profile.html', username=username, user=user_in_db, list=string_list, user_image=user_image_number)
    else:
        flash("You must log in first to see this page")
        return redirect(url_for('index'))

# Editing profile and saving changes
@app.route('/save-profile-changes/<username>', methods=['POST'])
def save_profile_changes(username):
    form = request.form.to_dict()
    user_in_db = users_coll.find_one({"username": username})
    profile_image_url = user_in_db['profile']['image']
    name_count = len(user_in_db['profile']['first_name'])
    base_profile_image_url = profile_image_url[:-name_count]
    users_coll.update_one({'username': username}, {'$set': {
        'profile.first_name': form['first_name'],
        'profile.last_name': form['last_name'],
        'profile.email_address': form['email_address'],
        'profile.dob': pd.to_datetime(form['dob']),
        'profile.image': base_profile_image_url+form['first_name']
        }})
    updated_user_in_db = users_coll.find_one({"username": username})
    flash("Changes have been saved to your profile")
    return redirect(url_for('profile', username=username))

# Update profile image
@app.route('/update-profile-image/<username>', methods=['POST'])
def update_profile_image(username):
    form=request.form.to_dict()
    user_in_db = users_coll.find_one({"username": username})
    profile_image_url = user_in_db['profile']['image']
    name_count = len(user_in_db['profile']['first_name'])
    base_profile_image_url = profile_image_url[:-name_count-2]
    selected_image=str(int(form['image_number'])+1)
    new_image_url=base_profile_image_url+selected_image+'/'+user_in_db['profile']['first_name']
    users_coll.update_one({'username': username}, {'$set': {
        'profile.image': new_image_url
        }})
    flash("Changes have been saved to your profile")
    return redirect(url_for('profile', username=username))

# Delete Profile
@app.route('/delete-profile/<username>')
def delete_profile(username):
    user_data = users_coll.find_one({'username': username})
    user_id=user_data['_id']
    transactions_coll.remove({'user_id': user_id})
    users_coll.remove({'username': username},{'justOne': True})
    session.clear()
    flash('Your profile has been deleted')
    return redirect(url_for('index'))

"""
User Dashboard
"""
        
@app.route('/user/<username>/dashboard')
def show_user_dashboard(username):
    if 'user' in session and session['user']==username:
        user_data = users_coll.find_one({'username': session['user']})
        user_id=user_data['_id']
        data=balance_prices_and_changes(user_data['wallet'],user_data['cash'])
        balance_data, updated_prices, updated_changes = data[0], data[1], data[2]
        wallet_coins_data=fetch_wallet_coins_data(updated_prices, updated_changes, user_data['wallet'],CRYPTOCOINS_LIST)
        pie_data = create_pie_chart(updated_prices,user_data,CRYPTOCOINS_LIST)
        favorites = favorite_list_data(user_data,wallet_coins_data,CRYPTOCOINS_LIST)
        not_favorites = not_favorite_list_data(user_data,CRYPTOCOINS_LIST)
        # user_transactions = transactions_coll.find({'user_id': ObjectId(user_id)}).sort([("date", -1)]).limit(5)
        user_transactions_list = get_user_transactions(user_id, transactions_coll)
        rank, count = calculate_users_rank(user_data,users_coll)
        return render_template("dashboard.html", user=user_data, balance=balance_data, plot=pie_data, wallet_coins=wallet_coins_data , rank=rank, count=count, favorites=favorites, not_favorites=not_favorites, transactions=user_transactions_list)
    else:
        flash("You must log in first to see this page")
        return redirect(url_for('index'))
# Check first if username is in session

"""
Adding or removing coins to favorite list
"""
# Remove coins from favorite list
@app.route('/remove-fav/<username>/<symbol>')
def remove_favorite(username, symbol):
    user_data=users_coll.find_one({'username':username})
    favorites_list=user_data['favorites'].split(",")
    favorites_list.remove(symbol)
    updated_favorites_list=(','.join(favorites_list))
    users_coll.update_one({'username':username},{'$set':{"favorites":updated_favorites_list}})
    return redirect(url_for('show_user_dashboard',username=username))

# Add coins to favorite list
@app.route('/add-fav/<username>/<symbol>')
def add_favorite(username, symbol):
    user_data=users_coll.find_one({'username':username})
    favorites_list=user_data['favorites'].split(",")
    if favorites_list[0]=='':
        favorites_list.append(symbol)
        favorites_list.pop(0)
        updated_favorites_list=(''.join(favorites_list))
    else:
        favorites_list.append(symbol)
        updated_favorites_list=(','.join(favorites_list))
    users_coll.update_one({'username':username},{'$set':{"favorites":updated_favorites_list}})
    return redirect(url_for('show_user_dashboard',username=username))

"""
Transactions
"""

# Buy new coins to wallet
@app.route('/buy-coins/<username>', methods=['POST'])
def buy_coins(username):
    submitted_form = request.form.to_dict()
    user_data=users_coll.find_one({'username':username})
    new_doc = prepare_buy_object(submitted_form,user_data)
    insert_transaction_to_db(users_coll, transactions_coll, new_doc,user_data)
    return redirect(url_for('show_user_dashboard',username=username))

# Sell existing coins from wallet
@app.route('/sell-coins/<username>', methods=['POST'])
def sell_coins(username):
    submitted_form = request.form.to_dict()
    user_data=users_coll.find_one({'username':username})
    new_doc = prepare_sell_object(submitted_form,user_data)
    insert_transaction_to_db(users_coll, transactions_coll, new_doc, user_data)
    return redirect(url_for('show_user_dashboard',username=username))

# Add additional funds to wallet
@app.route('/add-funds/<username>', methods=['POST'])
def add_funds(username):
    form = request.form.to_dict()
    added_funds=form['amount']
    added_funds_float=float(added_funds.replace(',',''))
    user_db=users_coll.find_one({'username':username})
    user_cash=user_db['cash']
    new_total_cash=user_cash+added_funds_float
    users_coll.update_one({'username':username},{'$set':{"cash":new_total_cash}})
    message='You have succesfully added US$ '+added_funds+' to your wallet'
    flash(message)
    return redirect(url_for('show_user_dashboard',username=username))

""" 
Chart line for crypto wallet performance 
Not displayed directly on Dashboard to reduce API Calls
"""

@app.route('/line-chart/<username>')
def line_chart(username):
    user_data=users_coll.find_one({'username':username})
    chart_data = create_line_chart(user_data)
    return render_template('chart.html', data=chart_data, user=user_data)


if __name__ == '__main__':
    app.run(host=os.getenv("IP","0.0.0.0"),
        port=int(os.getenv("PORT","5000")),
        debug=True)