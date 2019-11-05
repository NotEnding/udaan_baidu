# -*- coding: utf-8 -*-
# @Time : 2019/7/31 下午6:22
# @Site :  
# @File : SearchFromBaidu.py
import os, sys
import random
import time
from multiprocessing.pool import Pool

import xlrd

current_path = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(current_path)[0]
sys.path.append(rootPath)

from auxiliary.DatabaseInit import DatabaseInit
from auxiliary.UdImage2MhImage import Image2Image
from settings import REDIS_CLIENT, MEESHO_FILE_PATH

from auxiliary.AccessLog import Logger

logger = Logger().logger


# 生成meesho_id list
def init_meesho(file_path):
    workbook = xlrd.open_workbook(file_path)
    sheet1 = workbook.sheet_by_name('Sheet1')
    rowNum = 75561  # 行
    colNum = 6  # 列
    messho_id_list = []
    for i in range(1, rowNum):
        messho_id = int(sheet1.cell_value(i, 0))
        messho_id_list.append(messho_id)
        REDIS_CLIENT.rpush("meesho_sku_id_lists", messho_id)
        logger.info("meesho_id:{},添加到队列成功".format(str(messho_id)))


def query_func(meesho_id):
    info_list = Image2Image().product_search(meesho_id)
    is_table_exist = DatabaseInit().init_table('udaan_meesho_relationships')
    if is_table_exist:
        DatabaseInit().insert_data('udaan_meesho_relationships', info_list)
    else:
        logger.error('创建数据库表失败,请检查')


if __name__ == "__main__":
    # init_meesho(MEESHO_FILE_PATH) # 初始化，生成meesho id lists
    t1 = time.time()
    while True:
        queue_length = REDIS_CLIENT.llen('meesho_sku_id_lists')
        logger.info('开始进行meesho图片检索,当前剩余 {} 张图片待检索'.format(str(queue_length)))
        if queue_length != 0:
            po = Pool(5)
            for i in range(5):
                meesho_id = REDIS_CLIENT.rpop("meesho_sku_id_lists")
                if meesho_id:
                    meesho_id = str(meesho_id.decode())
                    po.apply_async(query_func, args=(meesho_id,))
                else:
                    continue
            time.sleep(random.random() * 2)
            po.close()
            po.join()
        else:
            logger.info('全部meesho商品检索完毕,退出任务')
            break
    t2 = time.time()
    logger.info('全部meesho图片检索完成,总耗时:{} s'.format(str(t2 - t1)))
