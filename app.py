from flask import Flask, render_template, request, redirect, session
from helper import search
from dotenv import dotenv_values
from pymongo import MongoClient
import hashlib

config = dotenv_values(".env")

def startup_db_client():
    app.mongodb_client = MongoClient(config["ATLAS_URI"])
    app.database = app.mongodb_client[config["DB_NAME"]]
    print("Connected to the MongoDB database!")

app = Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/search')
def search_v1():
	query = request.args.get('query')
	return search(query)


@app.route('/login',methods =['GET','POST'])
def login():
	if request.method == 'POST':
		email = request.form.get('email')
		password = request.form.get('password')
		user = app.databse['userinfo'].find_one({"username":email})
		if user:
			if encry(password) == user['password']:
				session['username'] = user['username']
				session['role'] = user['role']
				print(session['role'])
				if session.get('role') == 'admin':
					return redirect('/admin')
				return redirect('/')
			else:
				return redirect('/signup')
		return render_template('login.html')
	if request.method == 'GET':
		return render_template('login.html')



@app.route('/signup')
def signup():
	if request.method == 'POST':
		email = request.form.get('email')
		email_exist = app.database['user_info'].find_one({"user name":email})
		if email_exist:
			msg='email already existed!'
			return render_template('signup.html',msg=msg)
		else:
			password = request.form.get('password')
			password2 = input("please re-enter your password: ") #double check password
			if password == password2:
				msg = 'Signup success'
				password = encry(password)
				app.database['user_info'].insert_one({ "user name": email, "password": password,"role": "user" })
			return render_template('signup.html')
	else:
			msg = 'please check your password'
			return render_template('signup.html')
if request.method == 'GET':
	print('1')
		return render_template('signup.html')



if __name__ == '__main__':
	startup_db_client()
	app.run(debug=True)
