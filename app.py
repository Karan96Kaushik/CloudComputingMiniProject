from flask import Flask, render_template, request, redirect, session, jsonify, make_response
from helper import search, encry, parse_json
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

def getInfo(user):
	info = []
	profiles = app.database['personal_records'].find({"user":user})
	if profiles != None:
		for profile in profiles:
			record = profile['record']
			if record == None: continue
			record = parse_json(record)
			del record['_id']
			info.append(record)
			# info.append((record['id'],record['commonName'],record['lat'],record['lon']))
	return info

@app.route('/')
def index():
	response = make_response(render_template('index.html'),200)
	return response

@app.route('/search', methods=['GET'])
def search_loc():
	if request.method == 'GET':
		info=[]
		query = request.args.get('loc')
		results =  search(query)
		for result in results:

			del result["$type"]
			del result["additionalProperties"]
			del result["children"]
			del result["childrenUrls"]
			del result["url"]
			del result["placeType"]

			info.append(result)

			commonName = result['commonName']
			info_exist = app.database['save_records'].find_one({"commonName":commonName})
			print(info_exist)
			if info_exist:
				pass
			else:
				app.database['save_records'].insert_one(result)

		resp = jsonify(results=info)
		resp.status_code = 200
		return resp

@app.route('/profile', methods=['GET'])
def profile():
	user = session.get('username')
	info = []
	print(user)
	if user:
		info = getInfo(user)
		resp = jsonify(saved_points=info)
		resp.status_code = 200
		return resp
	else:
		msg="Please login"
		resp = jsonify(msg=msg)
		resp.status_code = 401
		return resp

@app.route('/profile', methods=['POST'])
def save_user_record():
	user = session.get('username')
	if user:
		id = request.form.get('id')
		exist = app.database['personal_records'].find_one({"user":user,'record.id':id})
		print(exist, id)
		if exist:
			resp = jsonify(msg="Duplicate entry")
			resp.status_code = 400
			return resp
		else:
			record_id = app.database['save_records'].find_one({"id":id})
			if record_id == None: 
				resp = jsonify(msg="Bikepoint not found, please search and try again")
				resp.status_code = 400
				return resp

			app.database['personal_records'].insert_one({"user":user,"record":record_id})
			resp = jsonify(msg="Added")
			resp.status_code = 201
			return resp
	else:
		resp = jsonify(msg="Please login")
		resp.status_code = 401
		return resp

@app.route('/profile',methods=['DELETE'])
def delete_user_record():
	user = session.get('username')
	if user:
		id = request.form.get('id')
		record_id = app.database['personal_records'].find_one({"id":id})
		app.database['personal_records'].delete_one({"id":id})
		
		resp = jsonify(msg="Deleted")
		resp.status_code = 204
		return resp

	else:
		resp = jsonify(msg="Please login")
		resp.status_code = 401
		return resp

@app.route('/login', methods=['GET'])
def login():
	if request.method == 'GET':

		email = request.args.get('email')
		password = request.args.get('password')
		print(email, password)
		user = app.database['user_info'].find_one({"username":email})
		user = parse_json(user)
		print(user)
		if user:
			if encry(password) == user['password']:
				session['username'] = user['username']
				session['role'] = user['role']
				session.permanent = True

				if session.get('role') == 'admin':
					resp = jsonify(admin=True, user=user)
					resp.status_code = 200
					return resp

				resp = jsonify(user=user)
				resp.status_code = 200
				return resp
			else:
				msg = "Invalid password"
				resp = jsonify(msg=msg)
				resp.status_code = 403
				return resp
		else :
			msg = "User not found"
			resp = jsonify(msg=msg)
			resp.status_code = 404
			return resp

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
			msg='Email already existed'
			resp = jsonify(msg=msg)
			resp.status_code = 400
			return resp
		else:
			password = request.form.get('password')
			password2 = request.form.get('password2')
			# password2 = input("please re-enter your password: ") #double check password
			if password == password2:
				password = encry(password)
				app.database['user_info'].insert_one({ "username": email, "password": password,"role": "user" })
				
				msg = 'Signup success'
				resp = jsonify(msg=msg)
				resp.status_code = 201
				return resp

			else:
				msg = 'Please check your password'
				resp = jsonify(msg=msg)
				resp.status_code = 400
				return resp

@app.route('/logout')
def logout():
	session.clear()
	msg = 'Logout success'
	resp = jsonify(msg=msg)
	resp.status_code = 200
	return resp

@app.route('/admin', methods=['GET', 'POST', 'PUT'])
def adminControl():
	if request.method=='GET':
		if session.get('role') != 'admin':
			msg = 'Unauthorized'
			resp = jsonify(msg=msg)
			resp.status_code = 401
			return resp

		users = app.database['user_info'].find({"role": "user"})
		userinfo = []
		for user in users:		
			del user['password']	
			userinfo.append(user)

		resp = jsonify(users=userinfo)
		resp.status_code = 200
		return resp

	if request.method=='POST':
		if session.get('role') != 'admin':
			msg = 'Unauthorized'
			resp = jsonify(msg=msg)
			resp.status_code = 401
			return resp

		username = request.form.get('username')
		if username:
			app.database['user_info'].delete_one({"username":username})

		msg = 'User deleted'
		resp = jsonify(msg=msg)
		resp.status_code = 204
		return resp

	if request.method=='PUT':
		username = request.form.get('username')
		password = request.form.get('password')
		password = encry(password)
		app.database['user_info'].update_one({"username":username},[{"$set":{"password":password}}])
		
		msg = 'User updated'
		resp = jsonify(msg=msg)
		resp.status_code = 200
		return resp


if __name__ == '__main__':
	startup_db_client()
	app.run(debug=True)
