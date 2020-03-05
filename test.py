
import os
import re
import pandas as pd
import collections
import numpy as np
pd.set_option('display.max_columns', None)

import requests
import json


'''
函数功能：根据传入的比较模糊的地址获取精确的结构化地址
函数实现流程：利用百度地图api的正地理编码可以获取该位置的经纬度
           接着使用经纬度采用逆地址编码获取结构化地址
'''

def get_formatted_address(address):
    # 根据百度地图api接口获取正地址编码也就是经纬度
    url1 = 'http://api.map.baidu.com/geocoding/v3/?address=' + address +\
           '&output=json&ak=70b7dffc87bb3e31cec115148fb4cd81&callback=showLocation'

    # 获取经纬度
    resp1 = requests.get(url1)
    resp1_str = resp1.text
    resp1_str = resp1_str.replace('showLocation&&showLocation', '')
    resp1_str = resp1_str[1:-1]
    resp1_json = json.loads(resp1_str)
    location = resp1_json.get('result').get('location')

    # 根据经纬度获取结构化地址
    lng = location.get('lng')
    lat = location.get('lat')
    url2 = 'http://api.map.baidu.com/reverse_geocoding/v3/?ak=70b7dffc87bb3e31cec115148fb4cd81&\
            output=json&coordtype=wgs84ll&location=' + str(lat) + ',' + str(lng) + ''
    resp2 = requests.get(url2)

    resp2_json = json.loads(resp2.text)
    # 提取结构化地址
    formattted_address = resp2_json.get('result').get('formatted_address')
    return formattted_address


if __name__ == '__main__':
    # 使用这个函数例如传入一个地址 网安大厦，当然传入的地址也不能太模糊了
    formattted_address = get_formatted_address('清华大学')
    print(formattted_address)