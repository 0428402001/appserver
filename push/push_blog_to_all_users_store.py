# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from array import array
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


APPID = "mI93rjjWyH92Xw8Z6cCW69"
APPKEY = "13OsRER7KL654tKicPB2J"
MASTERSECRET = "vJbIT9iRrt81h6mUClYpR1"

def pushAPN(device_token, subject, tokens, blog_id, app_name):
    DEVICETOKEN =  device_token
    push = IGeTui(HOST, APPKEY, MASTERSECRET)

    template = TransmissionTemplate()

    apn = APNPayload()

    apn = APNPayload()
    apn.badge = 1
    #apn.sound = "test1.wav"
    apn.contentAvailable = 1
    apn.category = "ACTIONABLE"



    #alertMsg = SimpleAlertMsg()
    #alertMsg.alertMsg = subject 


    alertMsg = DictionaryAlertMsg()
    pay_dict = {'id':blog_id}
    #alertMsg.body =  "shappy"
    alertMsg.body = pay_dict 
    #alertMsg.body = 'body'
    #alertMsg.actionLocKey = 'actionLockey'
    alertMsg.locKey = subject 
    alertMsg.locArgs=['loc-args']
    alertMsg.launchImage = 'launchImage'
    alertMsg.title = 'Title'
    alertMsg.titleLocArgs = ['TitleLocArg']
    alertMsg.titleLocKey = app_name 
    #alertMsg.titleLocKey = 'collegedaily'


   # apn.alertMsg = alertMsg
   # apn.badge = 1
   # apn.addCustomMsg("null", "null")

    apn.alertMsg=alertMsg

    template.setApnInfo(apn)


    # 单个用户推送接口
  #  message = IGtSingleMessage()
  #  message.data = template
  #  ret = push.pushAPNMessageToSingle(APPID, DEVICETOKEN, message)
  #  print "444444", message
  #  print "55555", device_token
  #  print "66666", subject
  #  print ret

    # 多个用户推送接口
    message = IGtListMessage()
    message.data = template
    contentId = push.getAPNContentId(APPID, message)
    deviceTokenList = tokens
#     deviceTokenList = []
#     deviceTokenList.append(DEVICETOKEN)
    ret = push.pushAPNMessageToList(APPID, contentId, deviceTokenList)

if __name__ == "__main__":
    device_token = "657bb070074e0dd17126281c4ecc334d61c1be4b3785110fb28ace77e5a98fff" 
    device_token_1 = "657bb070074e0dd17126281c4ecc334d61c1be4b3785110fb28ace77e5a98fff" 
    device_token_2 = "e0c0abb12ba0ff86542234d9df737b5eb3e148e57bebf3ae58eef016edea64ba" 
    tokens_str = sys.argv[1]
    blog_id = sys.argv[2]
    subject = sys.argv[3]
    app_name = sys.argv[4] 
    tokens = tokens_str.split('&&')
    selected_tokens = [i  for i in tokens if len(i)== 64]
    selected_tokens = set(selected_tokens)
    selected_tokens = list(selected_tokens)
    pushAPN(device_token, subject, selected_tokens, blog_id, app_name)
