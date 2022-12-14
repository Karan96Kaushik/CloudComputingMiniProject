from flask import Flask, render_template, request, redirect, session, jsonify
from helper import search, encry
from dotenv import dotenv_values
from pymongo import MongoClient


config = dotenv_values(".env")

def startup_db_client():
    app.mongodb_client = MongoClient(config["ATLAS_URI"])
    app.database = app.mongodb_client[config["DB_NAME"]]
    print("Connected to the MongoDB database!")
    #app.database['user_info'].insert_one({"user name": "admin@gmail.com", "password": encry("admin"), "role":"admin"})
    #app.database['user_info'].update_one({"user name":'1@1.com'},[{"$set":{"user name":"username","password":"password"}}])

app = Flask(__name__)
app.secret_key = 'assdggrvbsesg'

@app.route('/')
def index():
	return render_template('index.html')

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
		return render_template('search.html',info=info)


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
		user = app.database['user_info'].find_one({"user name":email})
		if user:
			if encry(password) == user['password']:
				session['username'] = user['user name']
				session['role'] = user['role']
				session.permanent = True
				if session.get('role') == 'admin':
					return redirect('/admin' )
				return redirect('/')
			else:
				return redirect('/signup')
		return render_template('login.html')

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
		email_exist = app.database['user_info'].find_one({ "user name": email})
		if email_exist:
			msg='email is existed!'
			return render_template('signup.html',msg=msg)
		else:
			password = request.form.get('password')
			password = encry(password)
			app.database['user_info'].insert_one({ "user name": email, "password": password,"role": "user" })
			return redirect('/')

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
			userinfo.append((user['_id'],user['user name'],user['password']))
		return render_template('admin_page.html',userinfo=userinfo)

	if request.method=='POST':
		username = request.form.get('username')
		if username:
			app.database['user_info'].delete_one({"user name":username})
			print('success')
		return redirect('/admin')


@app.route('/admin/update', methods=['POST'])
def update():
	if request.method=='POST':
		username = request.form.get('username')
		password = request.form.get('password')
		password = encry(password)
		app.database['user_info'].update_one({"user name":username},[{"$set":{"password":password}}])
		return redirect('/admin')


if __name__ == '__main__':
	startup_db_client()
	app.run(debug=True)
