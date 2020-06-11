import os
from flask import Flask
from datetime import datetime
from flask_pymongo import PyMongo
from flask import render_template, url_for, request, flash, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from calculations import balance_prices_and_changes, create_plot
from calculations import fetch_wallet_coins_data, favorite_list_data
from calculations import not_favorite_list_data
from transactions import prepare_buy_object, prepare_sell_object
from transactions import insert_transaction_to_db

"""
app config
"""

app = Flask(__name__)

# MongoDB config
app.config["MONGO_DBNAME"] = 'cryptocoins_db'
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.secret_key = os.getenv("SECRET_KEY")
mongo = PyMongo(app)

# Login config
# login = LoginManager(app)
# login.login_view = 'login'

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
Index
"""

@app.route('/')
@app.route('/index')
def index():
    if 'user' in session:
        user_in_db = users_coll.find_one({"username": session['user']})
        return render_template('index.html', user=user_in_db)
    else:
        return render_template("index.html")

"""
User Authentication
"""

# Login
@app.route('/login', methods=['GET'])
def login():
	# Check if user is logged in already in session
	if 'user' in session:
		user_in_db = users_coll.find_one({"username": session['user']})
		if user_in_db:
			# If so redirect user to his profile
			flash("You are logged in already!")
			return redirect(url_for('profile', username=user_in_db['username'], user=user_in_db))
	elif 'user' not in session:
		# Render the login page for user to log in again
		return render_template("login.html")

# Check user login details from login form
@app.route('/user_auth', methods=['POST'])
def user_auth():
    form = request.form.to_dict()
    user_in_db = users_coll.find_one({'username': form['username']})
    # Check for user in database and if passwords match (hashed password, real password)
    if user_in_db:
        if check_password_hash(user_in_db['password'], form['password']):
            session['user'] = form['username']
            flash('You logged in successfully!')
            return redirect(url_for('profile',
                            username=user_in_db['username'], user=user_in_db))
        else:
            flash('Invalid password or username')
            return redirect(url_for('login'))
    else:
        flash('Please sign up first to create an account')
        return redirect(url_for('signup'))


# Profile Page
@app.route('/profile/<username>')
def profile(username): 
	# Check if user is logged in already
	if 'user' in session:
		user_in_db = users_coll.find_one({"username": username})
		return render_template('profile.html', username=user_in_db['username'], user=user_in_db)
	else:
		flash("You must log in first to see this page")
		return redirect(url_for('index'))

#Log Out
@app.route('/logout')
def logout():
	# Clear the session
	session.clear()
	flash('You have logged out!')
	return redirect(url_for('index'))

# Sign up
@app.route('/signup', methods=['GET', 'POST'])
def signup():
	# Check if user is not logged in already
	if 'user' in session:
		flash("You are logged in already!")
		return redirect(url_for('index'))
	if request.method == 'POST':
		form = request.form.to_dict()
		# Check if the two password entries match and check if user already exists first 
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
                            'dob': form['dob'],
                            #This is not working
                            # 'dob': { '$dateFromString': {'dateString': form['dob']} },
                            # 'dob': datetime.strptime(form['dob'],'%Y-%m-%d'),
                            'email_address': form['email_address'],
                            'date_joined': datetime.utcnow(),
                            'image': 'http://lorempixel.com/100/150/abstract/1/'+form['first_name']+'/'
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
				# Check if user is actualy saved
				user_in_db = users_coll.find_one({"username": form['username']})
				if user_in_db:
					# Log user in and add user to session right away
					session['user'] = user_in_db['username']
					return redirect(url_for('profile', user=user_in_db, username=session['user']))
				else:
					flash("There was a problem saving your profile. Please try again.")
					return redirect(url_for('signup'))
		else:
			flash("Passwords do not match! Please try again")
			return redirect(url_for('signup'))
	return render_template("signup.html")

"""
User Dashboard
"""
        
@app.route('/user/<username>/dashboard')
def show_user_dashboard(username):
    if 'user' in session:
        user_in_db = users_coll.find_one({"username": session['user']})
        user_data=users_coll.find_one({'username':username})
        user_id=user_data['_id']
        data=balance_prices_and_changes(user_data['wallet'],user_data['cash'])
        balance_data, updated_prices, updated_changes = data[0], data[1], data[2]
        wallet_coins_data=fetch_wallet_coins_data(updated_prices, updated_changes, user_data['wallet'],CRYPTOCOINS_LIST)
        pie_data = create_plot(updated_prices,user_data)
        favorites = favorite_list_data(user_data,wallet_coins_data,CRYPTOCOINS_LIST)
        not_favorites = not_favorite_list_data(user_data,CRYPTOCOINS_LIST)
        user_transactions = transactions_coll.find({'user_id': ObjectId(user_id)}).sort([("date", -1)]).limit(5)
        return render_template("dashboard.html", user=user_data, balance=balance_data, plot=pie_data, wallet_coins=wallet_coins_data ,favorites=favorites, not_favorites=not_favorites, transactions=user_transactions)
    else:
        flash("You must log in first to see this page")
        return redirect(url_for('index'))

"""
Adding or removing coins to favorite list
"""
#Remove coins from favorite list
@app.route('/remove-fav/<username>/<symbol>')
def remove_favorite(username, symbol):
    user_data=users_coll.find_one({'username':username})
    favorites_list=user_data['favorites'].split(",")
    favorites_list.remove(symbol)
    updated_favorites_list=(','.join(favorites_list))
    users_coll.update({'username':username},{'$set':{"favorites":updated_favorites_list}},multi=False)
    return redirect(url_for('show_user_dashboard',username=username))

#Add coins to favorite list
@app.route('/add-fav/<username>/<symbol>')
def add_favorite(username, symbol):
    user_data=users_coll.find_one({'username':username})
    favorites_list=user_data['favorites'].split(",")
    favorites_list.append(symbol)
    updated_favorites_list=(','.join(favorites_list))
    users_coll.update({'username':username},{'$set':{"favorites":updated_favorites_list}},multi=False)
    return redirect(url_for('show_user_dashboard',username=username))

"""
Transactions
"""

#Buy new coins to wallet
@app.route('/buy-coins/<username>', methods=['POST'])
def buy_coins(username):
    submitted_form = request.form.to_dict()
    user_data=users_coll.find_one({'username':username})
    new_doc = prepare_buy_object(submitted_form,user_data)
    insert_transaction_to_db(mongo, new_doc,user_data)
    return redirect(url_for('show_user_dashboard',username=username))

#Sell existing coins from wallet
@app.route('/sell-coins/<username>', methods=['POST'])
def sell_coins(username):
    submitted_form = request.form.to_dict()
    user_data=users_coll.find_one({'username':username})
    new_doc = prepare_sell_object(submitted_form,user_data)
    insert_transaction_to_db(mongo, new_doc,user_data)
    return redirect(url_for('show_user_dashboard',username=username))

if __name__ == '__main__':
    app.run(host=os.getenv("IP","0.0.0.0"),
        port=int(os.getenv("PORT","5000")),
        debug=True)