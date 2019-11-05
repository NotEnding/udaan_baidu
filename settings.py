#! /usr/bin/python
# -*- coding: utf-8 -*-
# @Time  : 2019/7/3 下午5:37
#################### mongo config ##########################
import os
import pymongo

MONGO_CLIENT = pymongo.MongoClient(
    host='127.0.0.1',
    port=27017,
    username='admin',
    password='123456',
    connect=False
)
LISTING_DB = MONGO_CLIENT['public_udaan']
################### redis config  #########################
import redis

# 创建redis连接池
REDIS_CONF = {
    "host": '127.0.0.1',
    "port": 6379,
    "password": 'qwer',
    "db": 0
}
REDIS_POOL = redis.ConnectionPool(**REDIS_CONF)
REDIS_CLIENT = redis.Redis(connection_pool=REDIS_POOL)
###################### mysql config #########################
MYSQL_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'rootroot',
    'database': 'product_relationships',
    'port': 3306,
    'charset': 'utf8'
}
############################## BASE DIR #########################################
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 获取项目所在目录

################### log path ##############################
LOG_PATH = BASE_DIR + '/udaan_baidu/log'

################### file path ############################
FILE_PATH = BASE_DIR + '/udaan_baidu/file/'

################## list_collection #######################
LIST_COLLECTION = ['best_seller_listings_info', 'fast_moving_listings_info', 'latest_arrival_listings_info']
################## 待查询的品类  ##########################
UPLOAD_CATEGORIES = ['clothing_men', 'clothing_ethnic', 'clothing_western', 'clothing_fabric',
                     'clothing_home_furnishing', 'clothing_women', 'clothing_kids',
                     'clothing_innerwear', 'fashion_accessories', 'footwear', 'home_and_kitchen', 'toy_and_babycare']

########################### baidu api infomation ###############################
CLIENT_ID = 'AlZYm4iCGHTt3Inu7imRIbrd'
CLIENT_SECRET = 'GUSWmiSbuDQLQyNleibgxMDy2Omsyjw2'

#################### meesho 图片URL ###############
MEESHO_ROOT_IMAGE_URL = 'http://meesho-supply-v2.s3-website-ap-southeast-1.amazonaws.com/images/products/{product_id}/1_512.jpg'

############################ 创建商品关联关系表 ###################################
CREATE_TABLE_SQL = """
create table {} (
    id               int(11)     not null auto_increment,
    u_listingId      varchar(45) not null comment 'udaan 商品id',
    u_primaryImage_id varchar(100) not null comment 'udaan 商品主图id',
    u_primaryImage_url varchar(100) comment 'udaan 商品主图url',
    m_id             varchar(45) not null comment 'meesho 商品id',
    m_image_url      varchar(100) comment 'meesho 商品图片url',
    score            float not null comment '图片匹配得分',
    cont_sign        text  not null comment '图片的签名信息',
    created_at       timestamp   NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '商品记录创建时间',
    update_at        timestamp   NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '商品更新时间',  
    PRIMARY KEY (id)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8;
"""

######################### 插入SQL语句  #######################################
INSERT_SQL = """
insert ignore into {table} (u_listingId,u_primaryImage_id,u_primaryImage_url,m_id,m_image_url,score,cont_sign) values ("{values}")
"""

########################### File path #########################
MEESHO_FILE_PATH = '/home/zhengke/桌面/Meesho热销品推荐.xlsx'
