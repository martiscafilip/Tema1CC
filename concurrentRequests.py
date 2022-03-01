import time
from threading import Thread
import requests

def myfunc():
    url = "http://localhost:8080/metrics"
    for i in range(4):
        response = requests.request("GET", url)
        print(response.text)

for i in range(4):
    t = Thread(target=myfunc)
    t.start()
