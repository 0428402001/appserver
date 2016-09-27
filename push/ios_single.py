# -*- coding: utf-8 -*-
from array import array
import sys
__author__ = 'wei'

from igt_push import *
from igetui.template import *
from igetui.template.igt_base_template import *
from igetui.template.igt_transmission_template import *
from igetui.template.igt_link_template import *
from igetui.template.igt_notification_template import *
from igetui.template.igt_notypopload_template import *
from igetui.template.igt_apn_template import *
from igetui.igt_message import *
from igetui.igt_target import *
from igetui.template import *
from BatchImpl import *
from payload.APNPayload import *

# http的域名
HOST = 'http://sdk.open.api.igexin.com/apiex.htm';
#https的域名
# HOST = 'https://api.getui.com/apiex.htm';

#采用"Python SDK 快速入门"， "第二步 获取访问凭证 "中获得的应用配置
CID = "请输入用户唯一标识号"


APPKEY = "13OsRER7KL654tKicPB2J"
APPID = "mI93rjjWyH92Xw8Z6cCW69"
MASTERSECRET = "vJbIT9iRrt81h6mUClYpR1"
CID = "3b739cf40e7f9108d7b8eb6105ac4020342579e4b5f5544c9ca2934ca0d2bb05"
#DEVICETOKEN = "54a3d02b2bbf6906646f7959ec7512ef8ef064f9ed05c468c676228df59fb098"
DEVICETOKEN = "3b739cf40e7f9108d7b8eb6105ac4020342579e4b5f5544c9ca2934ca0d2bb05"

def pushAPN(device_token, subject):
    DEVICETOKEN =  device_token

    push = IGeTui(HOST, APPKEY, MASTERSECRET)
    message = IGtSingleMessage()

    template = TransmissionTemplate()
    apn = APNPayload();
    alertMsg = SimpleAlertMsg()
    alertMsg.alertMsg = subject 
    #alertMsg.alertMsg = "Happy Children's Day "
    apn.alertMsg = alertMsg
    apn.badge = 1
    apn.addCustomMsg("null", "null")


    payload_dict = {'id':900}
    apn.payload = payload_dict 


    template.setApnInfo(apn)


    # 单个用户推送接口
    message.data = template
    ret = push.pushAPNMessageToSingle(APPID, DEVICETOKEN, message)
    print "444444", message
    print "55555", device_token
    print "66666", subject
    print ret

    # 多个用户推送接口
#     message = IGtListMessage()
#     message.data = template
#     contentId = push.getAPNContentId(APPID, message)
#     deviceTokenList = []
#     deviceTokenList.append(DEVICETOKEN)
#     ret = push.pushAPNMessageToList(APPID, contentId, deviceTokenList)
#     print ret
if __name__ == "__main__":
    device_token = sys.argv[1]
    subject = sys.argv[2]
    pushAPN(device_token, subject)
