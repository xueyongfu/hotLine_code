import pymysql
import pandas as pd
import numpy as np
import uuid


def create_headers(sqlserver):
    all_cols = ['uuid','任务编号', '工单12345类型', '回访总体满意度', 'SOLVINGNUM', '立案部门人口数', '区派主责部门人口数',
       '退单次数所有主责', '坐标X', '坐标Y', '处置单位诉求认定', '处置单位事实认定', '退单次数', '最后主责先行联系',
       '整体超期次数', '区派最后主责超期天数', '第一次派遣用时', '任务编号1', '案件状态名称', '发生地址', '问题来源名称',
       '渠道来源名称', '管理要点名称', '立案部门名称', '问题描述', '整体超时', '最后一次主责部门', '最后主责部门名',
       '外系统管理单号', '问题大类编号', '案件大类名', '问题小类编号', '案件小类名', '案件属性名', '问题子类编码',
       '案件子类名', '是否标准大小类', '处理结果', '街道编号', '街道名', '三级主责部门编码', '三级主责部门名称',
       '流程工单', '区派最后主责名称', '是否首个工作日', '回访结果', '完成情况', '特殊案件标识', '满意度E家园',
       '处理超时', '处置状态', '统计大类', '统计小类', '立案操作人', '核查监督员', '处理备注', '上报监督员',
       '上报监督员姓名', '反馈市事实认定', '反馈市诉求认定', '居村委', '路段', '业务类型名称', '回复形式名',
       '诉求认定说明', '事实认定说明', '回复内容', '倒数第二次回访满意度', '倒数第二次回访结果', '倒数第二次是否先行联系',
       '年月日时分秒立案时间', '年月日时分秒结案时间', '立案年份', '立案日期', '立案年月', '立案月份', '立案年月日',
       '立案时点', '一二三四级', 'xy']
    int_cols = ['工单12345类型', 'SOLVINGNUM', '退单次数', '退单次数所有主责', '最后一次主责部门', '问题大类编号', '问题小类编号', 
                '问题子类编码', '是否标准大小类', '处理结果', '街道编号', '三级主责部门编码', '立案时点',]
    float_cols = ['回访总体满意度', '立案部门人口数', '区派主责部门人口数', '坐标X', '坐标Y','整体超期次数', '区派最后主责超期天数',]
    date_cols = ['年月日时分秒立案时间', '年月日时分秒结案时间', '立案年份', '立案日期', '立案年月', '立案月份', '立案年月日',]
    
    sql = "create table if not exists 2017到2019城运热线数据"
    fields = []
    for col in all_cols:
        if col in int_cols:
            fields.append(f'{col} int')
        elif col in float_cols:
            fields.append(f'{col} float')
        else:
            fields.append(f'{col} varchar(10)')
    
    sql += ' ('+','.join(fields)+');'
    sqlserver.execute_sql(sql)

            
class sqlServer():
    def __init__(self,host,port,user,password,database):
        self.conn = pymysql.connect(host=host,port=port,user=user,password=password,database=database,charset='utf8')
        self.cursor = self.conn.cursor()

    def execute_sql(self, sql):
        self.cursor.execute(sql)

    def insert_data(self,sql):
        self.cursor.execute(sql)

    def commit(self):
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()


def main():
    src_data = '/home/xyf/桌面/A/HotLine/src/2017-2019城运三年热线数据/20190809.xlsx'

    host='172.18.1.77'; port=3306; user='root'; password='541807'; database='HotLine'
    sqlserver = sqlServer(host,port,user,password,database,)
    


if __name__ == '__main__':
    main()
