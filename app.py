from flask import Flask, render_template, request, redirect, session, jsonify, make_response
from helper import search, encry
from dotenv import dotenv_values
from pymongo import MongoClient
import hashlib

config = dotenv_values(".env")

def startup_db_client():
	app.mongodb_client = MongoClient(config["ATLAS_URI"])
	app.database = app.mongodb_client[config["DB_NAME"]]
	print("Connected to the MongoDB database!")

app = Flask(__name__)
app.secret_key = 'assdggrvbsesg'

@app.route('/')
def index():
	response = make_response(render_template('index.html'),200)
	return response

@app.route('/search', methods=['GET','POST'])
def search_loc():
	if request.method == 'POST':
		info=[]
		query = request.form.get('loc')
		results =  search(query)
		for result in results:
			commonName = result['commonName']
			info_exist = app.database['save_records'].find_one({"commonName":commonName})
			if info_exist:
				info.append((info_exist['id'],info_exist['commonName'],info_exist['lat'],info_exist['lon']))
			else:
				info.append((result['id'],result['commonName'],result['lat'],result['lon']))
				app.database['save_records'].insert_one(result)
		response = make_response(render_template('search.html',info=info),500)
		return response	

@app.route('/profile/add', methods=['POST'])
def save_user_record():
	user = session.get('username')
	if user:
		id = request.form.get('id')
		exist = app.database['personal_records'].find_one({"user":user,"record['id']":id})
		#exist = exist['record']['id']
		#print(exist)
		if exist:
			msg = "You've added!"
			return redirect('/profile',msg=msg)
		else:
			record_id = app.database['save_records'].find_one({"id":id})
			app.database['personal_records'].insert_one({"user":user,"record":record_id})
			info = getInfo(user)
			return render_template('profiles.html',info=info)
	else:
		return redirect('/login')

@app.route('/profile')
def profile():
	user = session.get('username')
	info = []
	if user:
		info = getInfo(user)
		return render_template('profiles.html',info=info)

def getInfo(user):
	info = []
	profiles = app.database['personal_records'].find({"user":user})
	for profile in profiles:
		record = profile['record']
		info.append((record['id'],record['commonName'],record['lat'],record['lon']))
	return info

@app.route('/profile/delete',methods=['POST'])
def delete_user_record():
	user = session.get('username')
	if user:
		id = request.form.get('id')
		record_id = app.database['personal_records'].find_one({"id":id})
		app.database['personal_records'].delete_one({"record['id']":record_id})
		info = getInfo(user)
		return render_template('profiles.html',info=info)
	else:
		return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		email = request.form.get('email')
		password = request.form.get('password')
		user = app.database['user_info'].find_one({"username":email})
		if user:
			if encry(password) == user['password']:
				session['username'] = user['username']
				session['role'] = user['role']
				session.permanent = True
				print(session['role'])
				if session.get('role') == 'admin':
					return redirect('/admin')
				return redirect('/')
			else:
				msg = "Invalid password"
				print(msg)
				response = make_response(redirect('/login'),401)
				return response
		else :
			msg = "user not found"
			print(msg)
			response = make_response(redirect('/login'),401)
			return response

	if request.method == 'GET':
		return render_template('login.html')

@app.context_processor
def context():
	user = session.get('username')
	if user:
		return {'login':user}
	return {}


@app.route('/signup', methods=['GET', 'POST'])
def signup():
	if request.method == 'POST':
		email = request.form.get('email')
		email_exist = app.database['user_info'].find_one({"username":email})
		if email_exist:
			msg='email already existed!'
			print(msg)
			return render_template('signup.html',msg=msg)
		else:
			password = request.form.get('password')
			password2 = request.form.get('password2')
			# password2 = input("please re-enter your password: ") #double check password
			if password == password2:
				msg = 'Signup success'
				print(msg)
				password = encry(password)
				app.database['user_info'].insert_one({ "username": email, "password": password,"role": "user" })
				return render_template('login.html',msg=msg)
			else:
				msg = 'please check your password'
				print(msg)
				response = make_response(render_template('signup.html',msg=msg),201)
				return response

	if request.method == 'GET':
		return render_template('signup.html')

@app.route('/logout')
def logout():
	session.clear()
	return redirect('/')

@app.route('/admin', methods=['GET','POST'])
def adminControl():
	if request.method=='GET':
		if session.get('role') != 'admin':
			return redirect('/')
		users = app.database['user_info'].find({"role": "user"})
		userinfo = []
		for user in users:			
			userinfo.append((user['_id'],user['username'],user['password']))
		return render_template('admin_page.html',userinfo=userinfo)

	if request.method=='POST':
		username = request.form.get('username')
		if username:
			app.database['user_info'].delete_one({"username":username})
			print('success')
		return redirect('/admin')


@app.route('/admin/update', methods=['POST'])
def update():
	if request.method=='POST':
		username = request.form.get('username')
		password = request.form.get('password')
		password = encry(password)
		app.database['user_info'].update_one({"username":username},[{"$set":{"password":password}}])
		return redirect('/admin')


if __name__ == '__main__':
	startup_db_client()
	app.run(debug=True)
