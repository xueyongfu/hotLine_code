import requests
import time
import os

# _url = 'http://127.0.0.1'
_url = 'http://1.202.226.229'
_headers = {'Content-Type': 'application/x-www-form-urlencoded'}

def pos_ner_server():
    data = {'sentence':'中国今天是个好天气', 'orderId':'4434385932'}
    res = requests.post(_url+':6060', data, headers=_headers, verify=False)
    print(res.content.decode())

def address_format_server():
    data = {'sentence':'中国今天是个好天气', 'orderId':'4434385932','town':'大场镇'}
    res = requests.post(_url+':6061', data, headers=_headers, verify=False)
    print(res.content.decode())


if __name__ == '__main__':
    pos_ner_server()
    address_format_server()

