import requests
import re
import collections
import copy
import json
import jieba
import jieba.posseg as posseg


class addrFormat:
    jieba.load_userdict('address/dict.txt')
    jieba.load_userdict('address/dict_new.txt')
    
    @staticmethod
    def tokenize(address):
        return jieba.lcut(address)

    @staticmethod
    def addr_format(src_address, town):
        formated_addr = {'street':town,'village':'', 'road':'', 'crossroads':'', 'lane':'',
                        'number':'','bridge':'','subway':'','detail_address':''}
        ws = posseg.lcut(src_address)
        roads = []
        for w in ws:
            if w.flag == 'street':
                formated_addr['street'] = w.word
            elif w.flag == 'village':
                formated_addr['village'] += w.word
            elif w.flag == 'road':
                roads.append(w.word)
            elif w.flag == 'bridge':
                formated_addr['bridge'] += w.word
            elif w.flag == 'subway':
                formated_addr['subway'] += w.word

        if len(roads) > 1:
            formated_addr['crossroads'] = '|'.join(roads)
        elif len(roads) == 1:
            formated_addr['road'] = roads[0]

        if re.search('\d{1,4}弄', src_address):
            formated_addr['lane'] = re.search('\d{1,4}弄', src_address).group()
        if re.search('\d{1,5}号',src_address):
            formated_addr['number'] = re.search('\d{1,4}号', src_address).group()
        return formated_addr


def get_entity_and_coordinate(address):
    url = 'https://restapi.amap.com/v3/geocode/geo?address='+address+'&city=上海&output=\
                                                          json&key=70b7dffc87bb3e31cec115148fb4cd81'
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
    url = 'https://restapi.amap.com/v3/geocode/regeo?output=json&location='+coordinate+'&radius='+radius+\
                                                        '&key=70b7dffc87bb3e31cec115148fb4cd81&radius=10&extensions=all'
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
    #   print(address_info('浦东新区宣桥镇南六公路399弄艺泰安邦小区'))
    addrFormat.addr_format('浦东新区汇豪路71弄冠郡酒店','大场镇')