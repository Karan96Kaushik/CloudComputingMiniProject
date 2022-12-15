import requests
import hashlib
import json
from bson import json_util

def search(query):
    url = f"https://api.tfl.gov.uk/BikePoint/Search?query={query}"
    print('search test')
    return requests.get(url).json()

def encry(password):
    password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return password

def parse_json(data):
    return json.loads(json_util.dumps(data))


