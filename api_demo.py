import urllib.request
api_key = '9f0216be33fc340939350523f2e6d36f'
url = f"https://api.nomics.com/v1/currencies/ticker?key={api_key}&ids=BTC&interval=1d,30d&convert=EUR"
print(urllib.request.urlopen(url).read())
