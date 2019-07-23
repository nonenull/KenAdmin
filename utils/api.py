# coding=utf-8
import requests
import logging

logger = logging.getLogger(__name__)

def getIPLocation(ip):
    try:
        url = "http://ip.taobao.com/service/getIpInfo.php?ip="
        responseData = requests.get(url + ip).json()
        dictData = responseData['data']
        if dictData["county_id"] == 'local':
            areaInfo = '内网IP'
        else:
            areaInfo = dictData["region"] + dictData["city"] + dictData["isp"]
        return areaInfo
    except Exception as e:
        logger.warning('getIPLocation 发生意外：', e)
        return "服务器无法获取地区"
