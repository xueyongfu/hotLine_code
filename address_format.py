import requests
import re
import os
import json
import jieba
import jieba.posseg as posseg


def init_jieba():
    current_path = os.path.abspath(__file__)
    father_path = os.path.dirname(current_path)
    jieba.load_userdict(os.path.join(father_path,'address/dict.txt'))
    jieba.load_userdict(os.path.join(father_path,'address/dict_new.txt'))


def addr_format(address, town):
    # 加载自动以词典
    init_jieba()

    ws = posseg.lcut(address)
    formated_addr = {'街道':town}
    roads = []
    for w in ws:
        # 多个村,只保留一个最后一个
        if w.flag == 'village':
            formated_addr['村'] = w.word
        elif w.flag == 'road':
            # 可能多条路,表示路口
            roads.append(w.word)

    if len(roads) > 1:
        formated_addr['交叉路口'] = '|'.join(roads)
    elif len(roads) == 1:
        formated_addr['路'] = roads[0]

    if re.search('\d{1,4}弄', address):
        formated_addr['弄'] = re.search('\d{1,4}弄', address).group()
    if re.search('\d{1,5}号',address):
        formated_addr['号'] = re.search('\d{1,4}号', address).group()

    results = {}
    results['header'] = list(formated_addr.keys())
    results['address'] = list(formated_addr.values())
    return results


def get_entity_and_coordinate(address):
    url = 'https://restapi.amap.com/v3/geocode/geo?address='+address+'&city=\
           上海&output=json&key=70b7dffc87bb3e31cec115148fb4cd81'
    response = requests.get(url).content.decode()
    response = json.loads(response)
    
    formatted_address = response['geocodes'][0]['formatted_address']
    level = response['geocodes'][0]['level']
    coordinate = response['geocodes'][0]['location']
    if level == '兴趣点':
        entity = re.findall('上海市浦东新区(.*)', formatted_address)[0]
        return entity,coordinate
    else:
        return None,coordinate


def get_poi(coordinate, entity): 
    radius = '20'
    url = 'https://restapi.amap.com/v3/geocode/regeo?output=json&location='+coordinate+\
          '&radius='+radius+'&key=70b7dffc87bb3e31cec115148fb4cd81&radius=10&extensions=all'
    response = requests.get(url).content.decode()
    response = json.loads(response)
    pois = response['regeocode']['pois']

    if (entity is not None) & (pois != []):
        for i, poi in enumerate(pois):
            # 重合的词大于二,就认为名字重合
            if len(set(poi['name']).intersection(set(entity))) > 2:
                addr_type = poi['type']
                return addr_type
    #通过实体中的关键字进行类别判定
    addr_type = get_type_by_keyword(entity)
    return addr_type 


def address_info(address):
    # address = address_clean(address)
    # entity, coordinate = get_entity_and_coordinate(address)
    # addr_type = get_poi(coordinate, entity)
    formated_address = get_formated_addr(address)
    
    data = dict()
    data['formated_address'] = formated_address
    # data['entity'] = entity if entity else ''
    # data['addr_type'] = addr_type
    return data  


if __name__ == '__main__':
    result = addr_format('浦东新区高桥镇镇南村西浜头178号','大场镇')
    print(result)

