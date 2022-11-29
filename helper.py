import requests

#bike_url = "https://api.tfl.gov.uk/BikePoint/Search?query={keyword}"


def search(query):
    url = f"https://api.tfl.gov.uk/BikePoint/Search?query={query}"
    return requests.get(url).json()
