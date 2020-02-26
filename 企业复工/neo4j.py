import requests
import re
import collections
import copy
import json
import pandas as pd
import numpy as np
from py2neo import Graph, Node, Relationship, cypher, Path, NodeSelector
# from address_format import address_info


graph = Graph("http://localhost:7474", username="neo4j", password="neo4j")
# graph = Graph("http://172.18.1.77:7474", username="neo4j", password="neo4j")
selector = NodeSelector(graph)


def isNone(data):
    if data is np.nan:
        return True
    else:
        return False


def save_to_neo4j(data,columns):
    for index,row in data.iterrows():
        # if index > 5:
        #     break

        province= row['g1a']
        if isNone(province):
            continue
        province_node = selector.select(labels='省份',name=province).first()
        if province_node is None:
            province_node = Node('省份',name=province)
            graph.merge(province_node)

        city = row['G1bn']
        if isNone(city):
            continue
        city_node = selector.select(labels='城市',name=city).first()
        if city_node is None:
            city_node = Node('城市',name=city)
            graph.merge(city_node)

        province_city_rel = graph.match_one(start_node=province_node,rel_type='下辖',end_node=city_node)
        if province_city_rel is None:
            province_city_rel = Relationship(province_node,'下辖',city_node)
            graph.merge(province_city_rel)

        # 企业节点
        company = row['id002']
        if isNone(company):
            continue
        ## 企业具体开复工问题
        detail_dificulity = [column for column in columns if '111' in str(column)]
        detail_content = []
        for head in detail_dificulity:
            content = row[head]
            if not isNone(content):
                detail_content.append(str(content))
        all_difficulities = '&'.join(set(detail_content))

        ## 政策需求与具体建议
        detail_suggest = [column for column in columns if '222' in str(column)]
        detail_content = []
        for head in detail_suggest:
            content = row[head]
            if not isNone(content):
                detail_content.append(str(content))
        all_suggests = '&'.join(set(detail_content))

        company_node = selector.select(labels='公司',name=company).first()
        if company_node is None:
            company_node =Node('公司',name=company,dificulities=all_difficulities,suggests=all_suggests)
            graph.merge(company_node)

        # 企业与城市关系
        city_company_rel = graph.match_one(start_node=city_node,rel_type='地方包含',end_node=company_node)
        if city_company_rel is None:
            city_company_rel = Relationship(city_node,'地方包含',company_node)
            graph.merge(city_company_rel)

        # 规模
        scale = row['g4']
        if not isNone(scale):
            scale_node = selector.select(labels='规模',name=scale).first()
            if scale_node is None:
                scale_node = Node('规模',name=scale)
                graph.merge(scale_node)

            # 企业与规模
            company_scale_rel = graph.match_one(start_node=company_node,rel_type='企业规模',end_node=scale_node)
            if company_scale_rel is None:
                company_scale_rel = Relationship(company_node,'企业规模',scale_node)
            graph.merge(company_scale_rel)

        # 行业
        industry = row['g3']
        if not isNone(industry):
            industry_node = selector.select(labels='行业', name=industry).first()
            if industry_node is None:
                industry_node = Node('行业',name=industry)
                graph.merge(industry_node)

            # 企业与行业
            company_industry_rel = graph.match_one(start_node=company_node,rel_type='企业行业',end_node=industry_node)
            if company_industry_rel is None:
                company_industry_rel = Relationship(company_node,'企业行业',industry_node)
                graph.merge(company_industry_rel)

        # 复工
        returnWork = row['g5']
        if not isNone(returnWork):
            returnWork_node = selector.select(labels='复工状态', name=returnWork).first()
            if returnWork_node is None:
                returnWork_node = Node('复工状态', name=returnWork)
                graph.merge(returnWork_node)

            # 企业与复工
            degree = row['g6']
            company_returnWork_rel = graph.match_one(start_node=company_node, rel_type='企业复工状态', end_node=returnWork_node)
            if company_returnWork_rel is None:
                if isNone(degree):
                    company_returnWork_rel = Relationship(company_node, '企业复工状态', returnWork_node)
                else:
                    company_returnWork_rel = Relationship(company_node, '企业复工状态', returnWork_node, difficulty_degree=degree)
                graph.merge(company_returnWork_rel)

        # 政策与建议
        policySuggestions = [column for column in columns if '999' in str(column)]
        for ps in policySuggestions:
            posu = row[ps]
            if not isNone(posu):
                posu_node = selector.select(labels='政策建议',name=posu).first()
                if posu_node is None:
                    posu_node = Node('政策建议',name=posu)
                    graph.merge(posu_node)

                company_posu_rel = graph.match_one(start_node=company_node,rel_type='企业政策建议',end_node=posu_node)
                if company_posu_rel is None:
                    company_posu_rel = Relationship(company_node,'企业政策建议',posu_node)
                    graph.merge(company_posu_rel)

        # 开工问题
        startWork = [column for column in columns if '888' in str(column)]
        for sw in startWork:
            stwo = row[sw]
            if not isNone(stwo):
                stwo_node = selector.select(labels='开工问题', name=stwo).first()
                if stwo_node is None:
                    stwo_node = Node('开工问题', name=stwo)
                    graph.merge(stwo_node)

                company_stwo_rel = graph.match_one(start_node=company_node, rel_type='企业开工问题', end_node=stwo_node)
                if company_stwo_rel is None:
                    company_stwo_rel = Relationship(company_node, '企业开工问题', stwo_node)
                    graph.merge(company_stwo_rel)


        # raise Exception('1111')



def main():
    file_path = './三期企业问题征集(1).xlsx'
    data = pd.read_excel(file_path,sheet_name=3)
    columns = data.columns
    save_to_neo4j(data,columns)


if __name__ == '__main__':
    main()
