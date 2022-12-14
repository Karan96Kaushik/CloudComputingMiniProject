import requests
import hashlib

def search(query):
    url = f"https://api.tfl.gov.uk/BikePoint/Search?query={query}"
    print('search test')
    return requests.get(url).json()

def encry(password):
    password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return password



