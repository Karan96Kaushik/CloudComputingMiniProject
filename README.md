# Cloud Computing Mini Project

## Group 9 Members:
Karan Kaushik
Li, Hao
Luo, Yupeng
Yang, Ruixuan

## Group 9 Bike station searching

The search for bicycle stations comes from the external TFL API and the user can access the information by entering the location. 
app has two different accounts with different roles, 'admin' and 'user'. The user can save the results of a search by logging in and then the admin can manage all the account information.
Each type of account is encrypted with a password using SHA-256 at the time of registration.

## 1. Dynamically REST API(CRUD)

In order to provides a sufficient set of the services, we implemented 4 APIs 
so that the user can create the new account, read the search result, 
update the account information and delete saved results.

### Create
```
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
```
### Read

```
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


def getInfo(user):
	info = []
	profiles = app.database['personal_records'].find({"user":user})
	for profile in profiles:
		record = profile['record']
		info.append((record['id'],record['commonName'],record['lat'],record['lon']))
	return info
```


### Update
```
@app.route('/admin', methods=['GET', 'POST', 'PUT'])
def adminControl():
	if request.method=='PUT':
		username = request.form.get('username')
		password = request.form.get('password')
		password = encry(password)
		app.database['user_info'].update_one({"username":username},[{"$set":{"password":password}}])
		
		msg = 'User updated'
		resp = jsonify(msg=msg)
		resp.status_code = 200
		return resp

```
### Delete
```
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

```
## 2. External APIs

Bike searching uses an API from the TFL service to convert complex JSON data into tables by using script that are easy for users to understand. 
In the table, we will show ('Bike_id', 'CommonName', 'Lat', 'Lon') which get from the API. 

```

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

```



## 3. Cloud Database

The Application uses MongoDB Atlas for the database. Atlas is a cloud database hosted by MongoDB itself. 
Further, we use MongoDB Compass as the client side application to view and manage the data manually.   

## 4. Option2

### 4.1 HTTPS

The website `cloud.bayonetbaron.tech` is served over https, using SSL encryption. We're using a certificate issued by Let's Encrypt certificate authority generated using certbot application.  
All requests sent to the server over port 80 (HTTP) are automatically redirected to 443 (HTTPS) by NGINX proxy.

### 4.2 Hash-based authentication

All password will be hash before saving into database whatever in update info or create account. Hashing is done via SHA256 algorithm using the following 

```
def encry(password):
    password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return password
```


### 4.3 Implement user accounts and access management

Different role account can do different job. In this case, 'Admin' can access /admin to manage all account information. However, 'User' cannot access to the admin page.

```

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

```







