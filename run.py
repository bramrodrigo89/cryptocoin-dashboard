import os
if os.path.exists('env.py'):
    import env
from flask import Flask, render_template, redirect, request, url_for
from flask_pymongo import PyMongo


app = Flask(__name__)
app.config["MONGO_DBNAME"] = 'cryptocoins_db'
app.config['MONGO_URI']=os.getenv("MONGO_URI")

mongo = PyMongo(app)

@app.route('/')
@app.route('/home')
def say_hello():
    print(mongo.db.users.find())
    return render_template("index.html", users=mongo.db.users.find())

if __name__ == '__main__':
    app.run(host=os.getenv("IP","0.0.0.0"),
        port=int(os.getenv("PORT","5000")),
        debug=True)
