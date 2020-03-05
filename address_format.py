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


def get_detailed_addr(src_address):
    regex = {'town': '.{1,4}镇|.{1,4}街道', 'village': '.{1,4}村', 'abode': '.{1,4}宅',
             'road_1': '.{2,4}路|.{2,3}大道', 'road_2': '.{2,4}路|.{2,3}大道', 'lane': '\d{1,4}弄',
             'group': '\d{1,4}组','number': '\d{1,4}号', 'detail_address': '.*'}

    # 指定区
    fulldistrict = '浦东新区'
    subdistrict = '浦东'

    # 处理区描述不全问题
    if re.match(fulldistrict, src_address):
        src_address = re.sub('^' + fulldistrict, '', src_address)
    elif re.match(subdistrict + '.{0,1}路|' + subdistrict + '大道', src_address):
        pass
    elif re.match(subdistrict, src_address):
        src_address = re.sub('^' + subdistrict, '', src_address)

    # 将括号内容放入detail_address
    detail_address = re.findall('（(.*)）', src_address)
    detail_address = '' if detail_address == [] else detail_address[0]

    src_address = re.sub('（.*）', '', src_address)
    for key in regex:
        if key == 'detail_address':
            break
        addr = re.match(regex[key], src_address)
        if addr:
            end_position = re.match(regex[key], src_address).end()
            src_address = src_address[end_position:]

    detail_address = src_address + detail_address
    return detail_address


def addr_format(address, town):
    # 加载自动以词典
    init_jieba()

    formated_addr = {'街道': town}
    ws = posseg.lcut(address)
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

    # 获取详细地址
    detailed_addr = get_detailed_addr(address)
    formated_addr['详细地址'] = detailed_addr

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


if __name__ == '__main__':
    result = addr_format('外环线内过沪南公路入口200米','大场镇')
    print(result)



