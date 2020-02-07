import requests
import json

OrphaNumber = 558
url = "http://127.0.0.1:9200/product1/_search?q=fields.OrphaNumber={}&pretty".format(OrphaNumber)
response = requests.get(url, timeout=None).text

response = json.loads(response)

print(response)

print(response["hits"]["hits"][0]["_source"])
