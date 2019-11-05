# -*- coding: utf-8 -*- 
# @Time : 2019/7/26 下午2:43 
# @Site :  
# @File : Image2BaiduApi.py
import base64
import urllib
from urllib.parse import urlencode
from urllib.request import urlopen
import os, sys
import json

current_path = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(current_path)[0]
sys.path.append(rootPath)

from auxiliary.AccessLog import Logger
from settings import LOG_PATH, REDIS_CLIENT

logger = Logger().logger


# 上传百度类
class Imgae2Baidu:

    def __init__(self):
        self.access_token = 'token'
        self.product_api = "https://aip.baidubce.com/rest/2.0/image-classify/v1/realtime_search/product/add"  # 商品检索入库

    def get_access_token(self, client_id, client_secret):
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

    def product2baidu(self, listingId, id, image_url):
        '''
        :https://aip.baidubce.com/rest/2.0/image-classify/v1/realtime_search/product/add
        :param image_url: 图片url
        :param name : brief listingId 标识
        :param id : brief id 标识,primaryImageAsset id
        :return: 商品检索入库
        '''
        # image 编码
        try:
            f = urlopen(url=image_url, timeout=100)  # 下载图片可能超时
            img = base64.b64encode(f.read())
            # 参数
            params = {
                "brief": '{\"name\":\"' + listingId + '\",\"id\":\"' + id + '\"}',
                "image": img,
                "tags": "1,1"
            }
            params = urllib.parse.urlencode(params)
            # 上传至百度
            request_url = self.product_api + "?access_token=" + self.access_token
            request = urllib.request.Request(url=request_url, data=params.encode(encoding='UTF8'))
            request.add_header('Content-Type', 'application/x-www-form-urlencoded')
            # redis val
            val = listingId + '&' + id + '&' + image_url
            response = urlopen(url=request, timeout=60)  # 超时时间20秒
            content = response.read()
            if content:
                content_dict = json.loads(content.decode('utf-8'))  # 转化为字典
                # 出错情况
                if content_dict.__contains__("error_code"):
                    # 处理第一种情况，图片已存在的
                    if content_dict['error_code'] == 216681:
                        REDIS_CLIENT.lpush('image_already_existed', val)
                        logger.info("image_url:{},image_already_existed:{}".format(image_url, str(content_dict)))
                    # 处理第二种情况，图片格式错误的，现阶段我们支持的图片格式为：PNG、JPG、JPEG、BMP，修改图片格式后再重新上传。
                    elif content_dict['error_code'] == 216201:
                        REDIS_CLIENT.lpush('image_format_error', val)  # 加入到image_format_error队列
                        logger.error("image_url:{},image_format_error:{}".format(image_url, str(content_dict)))
                    # 处理第三种情况，上传的图片大小错误，现阶段我们支持的图片大小为：base64编码后小于4M，分辨率不高于4096*4096，重新上传图片
                    elif content_dict['error_code'] == 216202:
                        REDIS_CLIENT.lpush('image_size_error', val)  # 加入到image_size_error队列
                        logger.error("image_url:{},image_size_error:{}".format(image_url, str(content_dict)))
                    # 模型提取不到有效的图片特征,模型不知道应该以哪一个主体为识别目标，就处理不了了。请更换图片
                    elif content_dict['error_code'] == 216203:
                        REDIS_CLIENT.lpush('image_feature_error', val)  # 加入到image_feature_error队列
                        logger.error("image_url:{},image_feature_error:{}".format(image_url, str(content_dict)))
                    # url格式非法，建议更换图片地址;
                    elif content_dict['error_code'] == 282111:
                        REDIS_CLIENT.lpush('url_format_illegal', val)  # 加入到url_format_illegal队列
                        logger.error("image_url:{},url_format_illegal:{}".format(image_url, str(content_dict)))
                    # url下载超时，请检查url对应的图床
                    elif content_dict['error_code'] == 282112:
                        REDIS_CLIENT.lpush('url_download_timeout', val)  # 加入到url_download_timeout队列
                        logger.error("image_url:{},url_download_timeout:{}".format(image_url, str(content_dict)))
                    # URL返回无效参数，一般是图片URL抓图失败
                    elif content_dict['error_code'] == 282113:
                        REDIS_CLIENT.lpush('url_response_invalid', val)  # 加入到url_response_invalid队列
                        logger.error("image_url:{},url_response_invalid:{}".format(image_url, str(content_dict)))
                    # 图片URL长度超过1024字节或为0
                    elif content_dict['error_code'] == 282114:
                        REDIS_CLIENT.lpush('url_size_error', val)  # 加入到url_size_error队列
                        logger.error("image_url:{},url_size_error:{}".format(image_url, str(content_dict)))
                    # 其他所有类型的错误，都加入到统一的unknown_error队列
                    else:
                        REDIS_CLIENT.lpush('unknown_error', val)  # 加入到unknown_error队列
                        logger.error("image_url:{},unknown_error:{}".format(image_url, str(content_dict)))
                else:
                    # 没有错误码，则上传成功
                    logger.info("image_url:{},success:{}".format(image_url, str(content_dict)))
            else:
                # 如果出错没有返回，加入到出错队列
                REDIS_CLIENT.lpush('unknown_error', val)
        except Exception as e:
            val = listingId + '&' + id + '&' + image_url
            REDIS_CLIENT.lpush('unknown_error', val)
            logger.error("image_url:{},unknown_error:{}".format(image_url, str(e)))

# if __name__ == "__main__":
# object_info = REDIS_CLIENT.lpop('upload_to_baidu')
# if object_info:
#     object_infos = object_info.decode().split('&')
#     print(object_infos)
#     listingid, id, url = object_infos[0], object_infos[1], object_infos[2]
#     Imgae2Baidu().product2baidu(listingid, id, url)
