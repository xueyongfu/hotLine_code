import requests
import re
import collections
import copy
import json
import pandas as pd
import numpy as np
from py2neo import Graph, Node, Relationship, cypher, Path, NodeSelector
from address_format import address_info


# graph = Graph("http://localhost:7474", username="neo4j", password="neo4j")
graph = Graph("http://172.18.1.77:7474", username="neo4j", password="neo4j")
selector = NodeSelector(graph)


def get_tail_node(head_node, tail_node_type, tail_node_name):
    rel_type = 'subordinate'
    # rel_type = '下辖'   #示例图谱需要
    if not head_node:
        head_node = selector.select(tail_node_type, name=tail_node_name).first()
        if not head_node:
            graph.create(Node(tail_node_type, name=tail_node_name))
        return head_node
    else:
        tail_node = None
        head_tail_rels = graph.match(start_node=head_node, rel_type=rel_type)
        for rel in head_tail_rels:
            if rel.end_node()['name'] == tail_node_name:
                tail_node = rel.end_node()
                break
        if not tail_node:
            tail_node = Node(tail_node_type, name=tail_node_name)
            head_tail_rel = Relationship(head_node, rel_type, tail_node)
            graph.create(head_tail_rel)
        return tail_node


def get_mount_node(addr_layers):
    head_node = None
    for key in addr_layers:
        head_node = get_tail_node(head_node, key, addr_layers[key])
    return head_node


def get_address_subject(row,columns):
    '''返回有序的地址字典, 以及地址,违法主体合并字典'''
    raw_address = [row[c] for c in columns if '地址' in c ]
    raw_address = [addr for addr in raw_address if not pd.isnull(addr)]
    if raw_address != []:
        # 调用接口,获取结构化地址
        formated_addr = address_info(raw_address[0])['formated_address']
    else:
        formated_addr = collections.OrderedDict()

    address_subject = copy.deepcopy(formated_addr)
    illegal_subject = [row[c] for c in columns if '违法主体' in c if not pd.isnull(row[c])]
    if illegal_subject != []:
        address_subject['illegal_subject'] = illegal_subject[0]

    return formated_addr,address_subject


def update_rel(start_node,end_node,rel_type,attribute):
    rels = list(graph.match(start_node=start_node,rel_type=rel_type,end_node=end_node))
    if rels == []:
        rel = Relationship(start_node,rel_type,end_node)
        rel['actions_set'] = json.dumps({attribute:1},ensure_ascii=False)
        graph.create(rel)
    else:
        attrs_dict = json.loads(rels[0]['actions_set'])
        attrs_dict[attribute] = attrs_dict.get(attribute,0)+1
        rels[0]['actions_set'] = json.dumps(attrs_dict,ensure_ascii=False)
        graph.push(rels[0])


def assert_and_create_node(lable, name):
    if '5级事项' in lable:
        lable = 'level_5_matter'
    elif '4级事项' in lable:
        lable = 'level_4_matter'

    node = selector.select(lable,name=name).first()
    if not node:
        node = Node(lable,name=name)
        graph.create(node)
    return node


def save_to_neo4j(row, columns):
    formated_addr, address_subject = get_address_subject(row, columns)
    #获取关联事理图谱的地址根节点
    formated_addr_mount_node = get_mount_node(formated_addr)
    #获取关联事理图谱的违法主体的根节点
    address_subject_mount_node = get_mount_node(address_subject)

    #每三列一组
    for i in range(int(len(columns)/3)):
        subcolumns = columns[i*3:(i+1)*3]

        #判断该行中的三列是否为空,要求三元组全不为空
        if pd.isnull(row[subcolumns[0]]) or pd.isnull(row[subcolumns[1]]) or pd.isnull(row[subcolumns[2]]):
            continue

        #关系属性值
        attribute = row[subcolumns[1]]
        #关系类型
        rel_type = 'actions'
        # rel_type = attribute   #示例图谱需要

        if '地址' in subcolumns[0] and '违法主体' in subcolumns[2]:
            continue
        elif '地址' in subcolumns[0]:
            start_node = formated_addr_mount_node
            end_node = assert_and_create_node(subcolumns[2],row[subcolumns[2]])
            update_rel(start_node,end_node,rel_type,attribute)
        elif '违法主体' in subcolumns[0]:
            start_node = address_subject_mount_node
            end_node = assert_and_create_node(subcolumns[2],row[subcolumns[2]])
            update_rel(start_node,end_node,rel_type,attribute)
        else:
            start_node = assert_and_create_node(subcolumns[0],row[subcolumns[0]])
            end_node = assert_and_create_node(subcolumns[2],row[subcolumns[2]])
            update_rel(start_node,end_node,rel_type,attribute)


def main():
    file_path = 'data/元素抽取模板-扩大化.xlsx'
    data = pd.read_excel(file_path)
    columns = list(data.columns)
    for index, row in data.iterrows():
        save_to_neo4j(row, columns)


if __name__ == '__main__':
    main()

