import requests

def search(query):
    url = f"https://api.tfl.gov.uk/BikePoint/Search?query={query}"
    return requests.get(url).json()
