# -*- coding: utf-8 -*- 
# @Time : 2019/7/31 下午2:15 
# @Site :  
# @File : DatabaseInit.py
import os, sys
import pymysql

current_path = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(current_path)[0]
sys.path.append(rootPath)

from settings import MYSQL_CONFIG, CREATE_TABLE_SQL, INSERT_SQL
from auxiliary.AccessLog import Logger
logger = Logger().logger

class DatabaseInit:

    def __init__(self):
        # MySQL配置
        mysql_config = {
            'host': MYSQL_CONFIG["host"],
            'user': MYSQL_CONFIG["user"],
            'password': MYSQL_CONFIG["password"],
            'database': MYSQL_CONFIG["database"],
            'port': MYSQL_CONFIG["port"],
            'charset': MYSQL_CONFIG["charset"]
        }
        self.mysql_conn = pymysql.connect(**mysql_config)
        self.conn_cursor = self.mysql_conn.cursor(cursor=pymysql.cursors.DictCursor)

    def init_table(self, table_name):
        flag = self.conn_cursor.execute("show tables like '{}';".format(table_name))  # 判断表是否已存在
        if not flag:  # 不存在则创建
            try:
                self.conn_cursor.execute(CREATE_TABLE_SQL.format(table_name))
                logger.info('创建关联表 {} 成功'.format(table_name))
                return True
            except Exception as e:
                logger.info('创建关联表 {} 失败，请检查错误,error:{}'.format(table_name, str(e)))
                return None
        else: # 已存在则直接返回True
            return True

    def insert_data(self, table_name, info_list):
        insert_data = []
        if info_list:
            for info_dic in info_list:
                insert_data.append('","'.join([
                    info_dic["u_listingId"],
                    pymysql.escape_string(info_dic["u_primaryImage_id"]),
                    pymysql.escape_string(info_dic["u_primaryImage_url"]),
                    str(info_dic["m_id"]),
                    pymysql.escape_string(info_dic["m_image_url"]),
                    str(info_dic["score"]),
                    str(info_dic["cont_sign"]),
                ]))
            insert_sql = INSERT_SQL.format(table=table_name, values='"),("'.join(insert_data))
            try:
                self.conn_cursor.execute(insert_sql)
                self.mysql_conn.commit()
                logger.info('商品详情数据入库成功,meesho_id:%s',str(info_dic["m_id"]))
            except Exception as e:
                self.mysql_conn.rollback()  # 出错回滚
                logger.info('商品详情数据入库失败,错误信息:%s', str(e))
        else:
            logger.info('数据不存在')

    def __del__(self):
        # 关闭mysql数据库链接
        self.conn_cursor.close()
        self.mysql_conn.close()



