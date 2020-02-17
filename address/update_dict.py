import re
import pandas as pd
import numpy as np


def format_addr(src_address):
    fulldistrict = '浦东新区'
    subdistrict = '浦东'
    
    # 处理区描述不全问题
    if re.match(fulldistrict, src_address):
        src_address = re.sub('^'+fulldistrict, '', src_address)
    
    if re.match(subdistrict, src_address):
        if not re.match(subdistrict+'.{0,1}路|'+subdistrict+'大道', src_address):
            src_address = re.sub('^'+subdistrict, '', src_address)

    #将括号内容删除
    src_address = re.sub('（.*）','', src_address)

    regex = {'street':'.{1,4}镇|.{1,4}街道','village':'.{1,4}村|.{1,4}宅', 'road':'.{2,4}路|.{2,3}大道', 
             'lane':'\d{1,4}弄','number':'\d{1,4}号','detail_address':''}
    start_position = 0
    end_position = 0
    formated_address = {}
    for key in regex:
        if key == 'detail_address':
            formated_address[key] = src_address[start_position:]
            break
        
        addr = re.match(regex[key], src_address)
        if not addr:
            continue

        formated_address[key] = addr.group()
        start_position = re.match(regex[key], src_address).start()
        end_position = re.match(regex[key], src_address).end()
        src_address = src_address[end_position:]
    return formated_address

def get_new_address_byone(src_address):
    formated_address = format_addr(src_address)
    street = None
    road = None
    if formated_address.get('lane') or formated_address.get('number'):
        street = formated_address.get('street')
        road = formated_address.get('road')
    return street, road


def src_address():
    with open('address/dict.txt','r') as f:
        streets = []
        roads = []
        for line in f:
            w,f,ns = line.split()
            if ns == 'street':
                streets.append(w)
            elif ns == 'road':
                roads.append(w)
    return streets, roads


def save_new_address(streets, roads):
    with open('address/dict_new.txt','a') as f:
        for street in set(streets):
            f.write(street+' 99999 street'+'\n')
        for road in set(roads):
            f.write(road+' 99999 road'+'\n')


def get_new_address(path):
    src_streets, src_roads = src_address()
    new_streets, new_roads = [], []

    df = pd.read_excel(path)
    for index, row in df.iterrows():
        address = row['发生地址']
        if address is np.nan or not isinstance(address, str):
            continue
        new_street, new_road = get_new_address_byone(address)
        if new_street and new_street not in src_streets:
            new_streets.append(new_street)
        if new_road and new_road not in src_roads:
            new_roads.append(new_road)
    
    save_new_address(new_streets, new_roads)


if __name__ == '__main__':
    path = '/home/xyf/桌面/A/HotLine/src/2017-2019城运三年热线数据/20190809.xlsx'
    get_new_address(path)

    # get_new_address_byone(np.nan)
    
