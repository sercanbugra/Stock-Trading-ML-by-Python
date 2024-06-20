
from urllib.request import urlopen, Request
from urllib.parse import quote
from urllib.error import HTTPError
import certifi
import json

# List of user agents to rotate
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0'
]

def get_jsonparsed_data(url):
    response = urlopen(url, cafile=certifi.where())
    data = response.read().decode("utf-8")
    return json.loads(data)

url = ("https://financialmodelingprep.com/api/v4/price-target?symbol=AAPL&apikey=kav2CM8L77M1SsR9YfmbqHKz2ZanyXZx")
print(get_jsonparsed_data(url))



# kav2CM8L77M1SsR9YfmbqHKz2ZanyXZx