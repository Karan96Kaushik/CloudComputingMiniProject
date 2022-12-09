from flask import Flask, render_template, request
from helper import search
from dotenv import dotenv_values
from pymongo import MongoClient

config = dotenv_values(".env")

def startup_db_client():
	app.mongodb_client = MongoClient(config["ATLAS_URI"])
	app.database = app.mongodb_client[config["DB_NAME"]]
	print("Connected to the MongoDB database!")
	app.database['Users'].insert_one({"name": "karan"})

app = Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/search')
def search_v1():
	query = request.args.get('query')
	return search(query)

@app.route('/login')
def login():

	if request.method == 'POST':
		app.database['Users'].insert_one(request.form)
		return True

	if request.method == 'GET':
		return render_template('login.html')

@app.route('/signup')
def signup():

	if request.method == 'POST':
		data = request.form
		app.database['Users'].insert_one(request.form)
		return True

	if request.method == 'GET':
		return render_template('signup.html')


if __name__ == '__main__':
	startup_db_client()
	app.run(debug=True)
