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

# http������
HOST = 'http://sdk.open.api.igexin.com/apiex.htm';
#https������
# HOST = 'https://api.getui.com/apiex.htm';

#����"Python SDK ��������"�� "�ڶ��� ��ȡ����ƾ֤ "�л�õ�Ӧ������
CID = "�������û�Ψһ��ʶ��"


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

    apn = APNPayload()
    #alertMsg = SimpleAlertMsg()
    #alertMsg.alertMsg = subject 



    alertMsg = DictionaryAlertMsg()
    alertMsg.body = 'body'
    alertMsg.actionLocKey = 'actionLockey'
    alertMsg.locKey = 'lockey'
    alertMsg.locArgs=['loc-args']
    alertMsg.launchImage = 'launchImage'
    alertMsg.title = 'Title'
    alertMsg.titleLocArgs = ['TitleLocArg']
    payload_dict = "/blog/900"
    #apn.payload = payload_dict 

    alertMsg.payloadMsg = payload_dict 

   # apn.alertMsg = alertMsg
   # apn.badge = 1
   # apn.addCustomMsg("null", "null")

    apn.alertMsg=alertMsg

    template.setApnInfo(apn)


    # �����û����ͽӿ�
    message.data = template
    ret = push.pushAPNMessageToSingle(APPID, DEVICETOKEN, message)
    print "444444", message
    print "55555", device_token
    print "66666", subject
    print ret

    # ����û����ͽӿ�
#     message = IGtListMessage()
#     message.data = template
#     contentId = push.getAPNContentId(APPID, message)
#     deviceTokenList = []
#     deviceTokenList.append(DEVICETOKEN)
#     ret = push.pushAPNMessageToList(APPID, contentId, deviceTokenList)
#     print ret
if __name__ == "__main__":
    #device_token = "212fbfe1ba13d292ae4235ccf6cf907b2641eb926138206e762fc4096942962d" 
    device_token = "6cb864681c777287d81d7375bace35371260b51100a3513a186161b13191f9c7" 
    subject = "used_to_test" 
    #device_token = sys.argv[1]
    #subject = sys.argv[2]
    pushAPN(device_token, subject)
