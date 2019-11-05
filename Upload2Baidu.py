# -*- coding: utf-8 -*- 
# @Time : 2019/7/26 下午5:40 
# @Site :  
# @File : Upload2Baidu.py
import os, sys
import random
import time
from multiprocessing.pool import Pool

current_path = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(current_path)[0]
sys.path.append(rootPath)

from auxiliary.Image2BaiduApi import Imgae2Baidu
from settings import REDIS_CLIENT
from auxiliary.AccessLog import Logger

logger = Logger().logger


# task func
def start_task(listingid, id, url):
    Imgae2Baidu().product2baidu(listingid, id, url)


if __name__ == "__main__":
    t1 = time.time()
    while True:
        baidu_length = REDIS_CLIENT.llen('upload_to_baidu')
        logger.info('开始上传图片至Baidu,总计剩余 {} 张图片待上传'.format(str(baidu_length)))
        if baidu_length != 0:
            po = Pool(5) #开启5个进程
            for i in range(5):  # 一次取5张图片上传
                object_info = REDIS_CLIENT.rpop('upload_to_baidu')
                if object_info:
                    object_infos = object_info.decode().split('&')
                    listingid, id, url = object_infos[0], object_infos[1], object_infos[2]
                    po.apply_async(start_task, args=(listingid, id, url))
                else:
                    continue
            time.sleep(random.random() * 2)
            po.close()
            po.join()
        else:
            logger.info('全部图片上传完成')
            break
    t2 = time.time()
    logger.info('全部图片上传完成,总耗时:{} s'.format(str(t2 - t1)))
