# -*- coding: utf-8 -*- 
# @Time : 2019/7/26 下午2:50 
# @Site :  
# @File : QueryImageUrl.py
# 查询数据库中的clothing图片
import os, sys

current_path = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(current_path)[0]
sys.path.append(rootPath)

from settings import REDIS_CLIENT, LIST_COLLECTION, LISTING_DB, UPLOAD_CATEGORIES


class QueryImageUrl:
    '''
    查询数据库中所有商品的主图 primaryImageAsset image url
    '''

    def __init__(self):
        self.collection = LISTING_DB['listings_info']
        self.org_collection = LISTING_DB['orgs_info']

    def orgId_with_categories(self):
        '''
        :return: 将需查询品类的店铺id加入到集合
        '''
        org_datas = self.org_collection.find({}, {"sellingPrefs.sellingCategories": 1, "orgId": 1})
        orgId_with_categories_set = set()
        for org in org_datas:
            for category in org['sellingPrefs']['sellingCategories']:
                if category in UPLOAD_CATEGORIES:
                    orgId_with_categories_set.add(org['orgId'])
        return orgId_with_categories_set

    def generate_image_url_set(self):
        '''
        :param orgId: 根据orgId ，查询该店铺下的商品的商品图,并加入到set中
        :return: 返回存放image url 的集合长度
        '''
        orgId_with_categories = self.orgId_with_categories()
        for orgId in orgId_with_categories:
            listing_datas = self.collection.find({'orgId': orgId})
            for listing_info in listing_datas:
                listingId = listing_info['listingId']
                if listing_info['primaryImageAsset']:  # 存在主图则直接获取主图中的信息
                    primaryImage_id = listing_info['primaryImageAsset']['id']
                    primaryImage_uri = listing_info['primaryImageAsset']['original']['uri']
                    key_value = str(listingId) + '&' + str(primaryImage_id) + '&' + str(primaryImage_uri)
                    REDIS_CLIENT.lpush('upload_to_baidu', key_value)  # 加入到队列
                else:  # 不存在则判断获取相关图
                    if listing_info['listingOrSalesUnitImageAssets']:
                        primaryImage_id = listing_info['listingOrSalesUnitImageAssets'][0]['id']
                        primaryImage_uri = listing_info['listingOrSalesUnitImageAssets'][0]['original']['uri']
                        key_value = str(listingId) + '&' + str(primaryImage_id) + '&' + str(primaryImage_uri)
                        REDIS_CLIENT.lpush('upload_to_baidu', key_value)  # 加入到队列
                    else:
                        pass

# 初始化队列
# if __name__ == "__main__":
#     QueryImageUrl().generate_image_url_set() # listings_info
#     for coll in LIST_COLLECTION:
#         data_cursor = LISTING_DB[coll].find({})
#         for data in data_cursor:
#             listingId = data['listingId']
#             if data['primaryImageAsset']:  # 存在主图则直接获取主图中的信息
#                 primaryImage_id = data['primaryImageAsset']['id']
#                 primaryImage_uri = data['primaryImageAsset']['original']['uri']
#                 key_value = str(listingId) + '&' + str(primaryImage_id) + '&' + str(primaryImage_uri)
#                 REDIS_CLIENT.lpush('upload_to_baidu', key_value)
#             else:  # 不存在则判断获取相关图
#                 if data['listingOrSalesUnitImageAssets']:
#                     primaryImage_id = data['listingOrSalesUnitImageAssets'][0]['id']
#                     primaryImage_uri = data['listingOrSalesUnitImageAssets'][0]['original']['uri']
#                     key_value = str(listingId) + '&' + str(primaryImage_id) + '&' + str(primaryImage_uri)
#                     REDIS_CLIENT.lpush('upload_to_baidu', key_value)
#                 else:
#                     continue
