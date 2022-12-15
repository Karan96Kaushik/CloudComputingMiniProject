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
		print("1")
		return render_template('signup.html')
```
### Read

```
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
```


### Update
```
@app.route('/admin/update', methods=['POST'])
def update():

	if request.method=='POST':
		username = request.form.get('username')
		password = request.form.get('password')
		password = encry(password)
		app.database['user_info'].update_one({"user name":username},[{"$set":{"password":password}}])
		return redirect('/admin')
```
### Delete
```
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
```
## 2. External APIs

Bike searching uses an API from the TFL service to convert complex JSON data into tables by using script that are easy for users to understand. 
In the table, we will show ('Bike_id', 'CommonName', 'Lat', 'Lon') which get from the API. 

```
def search(query):
    url = f"https://api.tfl.gov.uk/BikePoint/Search?query={query}"
    return requests.get(url).json()
    
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
```







