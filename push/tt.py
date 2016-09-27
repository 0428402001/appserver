# -*- coding: utf-8 -*-
#
from igt_push import *
from igetui.template import *
from igetui.template.igt_base_template import *
from igetui.template.igt_transmission_template import *
from igetui.template.igt_link_template import *
from igetui.template.igt_notification_template import *
from igetui.template.igt_notypopload_template import *
from igetui.igt_message import *
from igetui.igt_target import *
from igetui.template import *

#采用"Python SDK 快速入门"， "第二步 获取访问凭证 "中获得的应用配置
APPKEY = "Mjv706pTKt5cTcjtqaToz8"
APPID = "JroCkPGgpF6LzFQqqoWlhA"
MASTERSECRET = "uIBtmad7RK706cy5MKdfp3"
CID = "e560b884d8d9bf5bc5a0f9da545a11f3"
HOST = 'http://sdk.open.api.igexin.com/apiex.htm'

def pushMessageToApp():
    push = IGeTui(HOST, APPKEY, MASTERSECRET)
    #push = IGeTui("",APPKEY,MASTERSECRET)#此方式可通过获取服务端地址列表判断最快域名后进行消息推送，每10分钟检查一次最快域名
    #消息模版： 
    #NotificationTemplate：通知透传功能模板  

    template = TransmissionTemplateDemo()
    #定义"AppMessage"，设置是否离线，离线有效时间，推送模板，推送速度等
    message = IGtAppMessage()
    message .setSpeed(100)#设置消息推送速度，单位为条/秒，例如填写100，则为100条/秒。仅支持对指定应用群推接口。
    message.data = template
    message.pushNetWorkType = 1#设置是否根据WIFI推送消息，1为wifi推送，0为不限制推送
    message.isOffline = True
    message.offlineExpireTime = 1000 * 3600 * 12
    message.appIdList.extend([APPID])
    message.phoneTypeList.extend(["ANDROID", "IOS"])
    message.provinceList.extend(["浙江", "上海","北京"])
    message.tagList.extend(["开心"])
    ret = push.pushMessageToApp(message)
    print ret

#通知透传模板动作内容
def TransmissionTemplateDemo():
    template = TransmissionTemplate()
    template.transmissionType = 1
    template.appId = APPID
    template.appKey = APPKEY
    template.transmissionContent = '请输入您要透传内容'
#    iOS setAPNInfo
#    apnpayload = APNPayload()
#     apnpayload.badge = 4
#     apnpayload.sound = "sound"
#     apnpayload.addCustomMsg("payload", "payload")
# #     apnpayload.contentAvailable = 1
# #     apnpayload.category = "ACTIONABLE"
#               
#     alertMsg = DictionaryAlertMsg()
#     alertMsg.body = 'body'
#     alertMsg.actionLocKey = 'actionLockey'
#     alertMsg.locKey = 'lockey'
#     alertMsg.locArgs=['locArgs']
#     alertMsg.launchImage = 'launchImage'
#     # IOS8.2以上版本支持
# #     alertMsg.title = 'Title'
# #     alertMsg.titleLocArgs = ['TitleLocArg']
# #     alertMsg.titleLocKey = 'TitleLocKey'
#     apnpayload.alertMsg=alertMsg
#     template.setApnInfo(apnpayload)

    # 设置通知定时展示时间，结束时间与开始时间相差需大于6分钟，消息推送后，客户端将在指定时间差内展示消息（误差6分钟）
    #begin = "2015-03-04 17:40:22";
    #end = "2015-03-04 17:47:24";
    #template.setDuration(begin, end)

    return template

pushMessageToApp()
