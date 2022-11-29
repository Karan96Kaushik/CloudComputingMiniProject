from flask import Flask, render_template, request
from helper import search


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
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')



if __name__ == '__main__':
    app.run(debug=True)
