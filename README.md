# CloudComputingMiniProject

## Group 9 Bike station searching

The search for bicycle stations comes from the external TFL API and the user can access the information by entering the location. 
app has two different accounts with different roles, 'admin' and 'user'. The user can save the results of a search by logging in and then the admin can manage all the account information.
Each type of account is encrypted with a password using SHA-256 at the time of registration. The data will be stored in the ().

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
## 2. External APIs

Bike searching uses an API from the TFL service to convert complex JSON data into tables by using script that are easy for users to understand. 
In the table, we will show ('Bike_id', 'CommonName', 'Lat', 'Lon') which get from the API. 
```
def search(query):
    url = f"https://api.tfl.gov.uk/BikePoint/Search?query={query}"
    return requests.get(url).json()

<script>
    let keyword="";
    function search(node) {
        keyword = node.parentNode.querySelector('.keyword').value;
        document.getElementById("searchBox").classList.add("hide");
        document.getElementById("searchResults").classList.remove("hide");
        if (keyword) {
            document.getElementById("keyword").value = keyword;
            fetch(`/search?query=${keyword}`).then(res => res.json()).then(data => {
                renderResults(data);
            })
        }
    }

    function renderResults(data) {
        if (data.length === 0) {
            document.getElementById("tableResults").innerHTML = `<tr><td colspan="4" class="text-center">No results found</td></tr>`;
        } else {
            const tableResults = document.querySelector('#tableResults');
            tableResults.innerHTML = '';
            data.forEach((item) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                <form action='/save_records' method='POST'>
                    
                    <input name='bike_id' value=${item.id}>
                    <input name='bike_name' value=${item.commonName}>
                    <input name='bike_lat' value=${item.lat}>
                    <input name='bike_lon' value=${item.lon}>
                    <button name="save">
                        Save
                    </button>
                </form>
                `;
                tableResults.appendChild(tr);
            })
        }
    }
</script>
```





## 3. Cloud Database

## 4. Option2

### 4.1 Https

### 4.2 Hash-based authentication

All password will be hash before saving into database whatever in update info or create account.

```
def encry(password):
    password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return password

update account information
password = encry(password)
app.database['user_info'].update_one({"user name":username},[{"$set":{"password":password}}])

create new account
password = encry(password)
app.database['user_info'].insert_one({ "user name": email, "password": password,"role": "user" })
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







