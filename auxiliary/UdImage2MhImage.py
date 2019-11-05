# -*- coding: utf-8 -*- 
# @Time : 2019/7/30 下午6:11 
# @Site :  
# @File : UdImage2MhImage.py
import base64
import urllib
from urllib.parse import urlencode
from urllib.request import urlopen
import os, sys
import json
import re

current_path = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(current_path)[0]
sys.path.append(rootPath)

from settings import MEESHO_ROOT_IMAGE_URL
from settings import REDIS_CLIENT

from auxiliary.AccessLog import Logger

logger = Logger().logger


# 以图搜图
class Image2Image:

    def __init__(self):
        self.access_token = 'token'
        self.product_search_api = 'https://aip.baidubce.com/rest/2.0/image-classify/v1/realtime_search/product/search'  # 商品图片-检索

    def access_token(self, client_id, client_secret):
        '''
        :https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}
        :param client_id: client_id 为官网获取的API Key ,
        :param client_secret: client_secret 为官网获取的Secret Key
        :return:
        '''
        host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}'.format(
            client_id=client_id, client_secret=client_secret)
        request = urllib.request.Request(host)
        request.add_header('Content-Type', 'application/json; charset=UTF-8')
        response = urllib.request.urlopen(request)
        content = eval(response.read().decode())
        if content:
            access_token = content['access_token']
            return access_token
        else:
            return None

    def product_search(self, meesho_id):
        '''
        :https://aip.baidubce.com/rest/2.0/image-classify/v1/realtime_search/product/search
        :param image_url: 商品图片搜索，用于匹配的图片URL
        :return:
        '''
        meesho_image_url = MEESHO_ROOT_IMAGE_URL.format(product_id=meesho_id)
        try:
            f = urlopen(meesho_image_url, timeout=100)
            img = base64.b64encode(f.read())
            # 参数
            params = {"image": img}
            params = urllib.parse.urlencode(params)
            # 商品检索
            request_url = self.product_search_api + "?access_token=" + self.access_token
            request = urllib.request.Request(url=request_url, data=params.encode(encoding='UTF8'))
            request.add_header('Content-Type', 'application/x-www-form-urlencoded')
            response = urlopen(url=request, timeout=60)
            content = response.read()
            if content:
                content_dict = json.loads(content.decode('utf-8'))  # 转化为字典
                # print(content_dict)
                info_list = []
                for result in content_dict['result'][:6:]:  # 取得分最高的结果
                    brief = json.loads(result['brief'])
                    primaryImage_url = "https://udaan.azureedge.net/products/" + re.search(r'products/(.*?)/',
                                                                                           brief['id']).group(1).strip()
                    info_list.append(
                        {
                            "u_listingId": brief['name'],
                            "u_primaryImage_id": brief['id'],
                            "u_primaryImage_url": primaryImage_url,
                            "m_id": meesho_id,
                            "m_image_url": meesho_image_url,
                            "score": result['score'],
                            "cont_sign": result['cont_sign']
                        }
                    )
                return info_list
        except Exception as e:
            REDIS_CLIENT.lpush("unknow_error_meesho_id", str(meesho_id))  # 出错的加入到队列中
            logger.error("商品检索失败,meesho_id:{},error:{}".format(str(meesho_id), str(e)))

    def item_exists(self, image_url):
        f = urlopen(url=image_url, timeout=60)  # 下载图片可能超时
        img = base64.b64encode(f.read())
        # 参数
        params = {"image": img}
        params = urllib.parse.urlencode(params)
        # 上传至百度
        request_url = self.product_search_api + "?access_token=" + self.access_token
        request = urllib.request.Request(url=request_url, data=params.encode(encoding='UTF8'))
        request.add_header('Content-Type', 'application/x-www-form-urlencoded')
        response = urlopen(url=request, timeout=25)  # 超时时间20秒
        content = response.read()
        if content:
            content_dict = json.loads(content.decode('utf-8'))
            for i in content_dict['result'][:6:]:  # 取得分最高前6条
                logger.info(i)

# if __name__ == "__main__":
#     Image2Image().product_search('589453')

# image_url = 'https://udaan.azureedge.net/products/7nmfba1h3qc67615n5cb.jpg'
# image_url = 'https://udaan.azureedge.net/products/nps18bz3ezyyn0lau3mq.jpg'
# image_url = 'https://udaan.azureedge.net/products/hrt7tzck0dht9696yr0z.jpg'
# image_url = 'https://udaan.azureedge.net/products/2tpgh3p42qju9wu1bqgk.jpg'
# image_url = 'https://udaan.azureedge.net/products/jcdmebvbospsyt39747z.PNG'
# Image2Image().item_exists(image_url)
