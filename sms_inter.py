#!/usr/local/bin/python
#-*- coding:utf-8 -*-
# Author: jacky
# Time: 14-2-22 下午11:48
# Desc: 短信http接口的python代码调用示例
import httplib
import urllib
import random

#服务地址
host = "222.73.117.140"

#端口号
port = 8044



#查账户信息的URI
balance_get_uri = "/bi"

#智能匹配模版短信接口的URI
sms_send_uri = "/mt"

un = 'I2094194'

pw = 'LJmys8ZVuqdef3'

dc=15
tf=3
rf=1


def get_user_balance():
    """
    取账户余额
    """
    conn = httplib.HTTPConnection(host, port=port)
    conn.request('GET', balance_get_uri + "?un=" + un + "&pw=" + pw)
    response = conn.getresponse()
    response_str = response.read()
    conn.close()
    return response_str

def send_sms(text, mobile):
    """
    能用接口发短信
    """
    params = urllib.urlencode({'un': un, 'pw' : pw, 'sm': text, 'da':mobile, 'dc' : dc, 'tf' : tf,'rf':rf })
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    conn = httplib.HTTPConnection(host, port=port, timeout=30)
    conn.request("POST", sms_send_uri, params, headers)
    response = conn.getresponse()
    response_str = response.read()
    conn.close()
    return response_str 

if __name__ == '__main__':

    mobile = "8618600299256"
    text = "【北美留学生日报】您的验证码为"+str(random.randint(1000,9999))
    #text = '您的验证码为1234'
    #text = text.encode("UTF-8")
    #查账户余额
    print(get_user_balance())

    #调用智能匹配模版接口发短信
    res = send_sms(text, mobile)
    print res
