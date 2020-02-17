import requests
import time
import os

_url = 'http://127.0.0.1' + ':8006'
_headers = {'Content-Type': 'application/x-www-form-urlencoded'}

def sent_data():
    data = {'type':'pos_ner', 'sentence':'中国今天是个好天气', 'orderId':'4434385932'}
    res = requests.post(_url, data, headers=_headers, verify=False)
    print(res.content.decode())

if __name__ == '__main__':
    sent_data()

