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

#����"Python SDK ��������"�� "�ڶ��� ��ȡ����ƾ֤ "�л�õ�Ӧ������
APPKEY = "Mjv706pTKt5cTcjtqaToz8"
APPID = "JroCkPGgpF6LzFQqqoWlhA"
MASTERSECRET = "uIBtmad7RK706cy5MKdfp3"
CID = "e560b884d8d9bf5bc5a0f9da545a11f3"
HOST = 'http://sdk.open.api.igexin.com/apiex.htm'

def pushMessageToApp():
    push = IGeTui(HOST, APPKEY, MASTERSECRET)
    #push = IGeTui("",APPKEY,MASTERSECRET)#�˷�ʽ��ͨ����ȡ����˵�ַ�б��ж���������������Ϣ���ͣ�ÿ10���Ӽ��һ���������
    #��Ϣģ�棺 
    #NotificationTemplate��֪ͨ͸������ģ��  

    template = TransmissionTemplateDemo()
    #����"AppMessage"�������Ƿ����ߣ�������Чʱ�䣬����ģ�壬�����ٶȵ�
    message = IGtAppMessage()
    message .setSpeed(100)#������Ϣ�����ٶȣ���λΪ��/�룬������д100����Ϊ100��/�롣��֧�ֶ�ָ��Ӧ��Ⱥ�ƽӿڡ�
    message.data = template
    message.pushNetWorkType = 1#�����Ƿ����WIFI������Ϣ��1Ϊwifi���ͣ�0Ϊ����������
    message.isOffline = True
    message.offlineExpireTime = 1000 * 3600 * 12
    message.appIdList.extend([APPID])
    message.phoneTypeList.extend(["ANDROID", "IOS"])
    message.provinceList.extend(["�㽭", "�Ϻ�","����"])
    message.tagList.extend(["����"])
    ret = push.pushMessageToApp(message)
    print ret

#֪ͨ͸��ģ�嶯������
def TransmissionTemplateDemo():
    template = TransmissionTemplate()
    template.transmissionType = 1
    template.appId = APPID
    template.appKey = APPKEY
    template.transmissionContent = '��������Ҫ͸������'
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
#     # IOS8.2���ϰ汾֧��
# #     alertMsg.title = 'Title'
# #     alertMsg.titleLocArgs = ['TitleLocArg']
# #     alertMsg.titleLocKey = 'TitleLocKey'
#     apnpayload.alertMsg=alertMsg
#     template.setApnInfo(apnpayload)

    # ����֪ͨ��ʱչʾʱ�䣬����ʱ���뿪ʼʱ����������6���ӣ���Ϣ���ͺ󣬿ͻ��˽���ָ��ʱ�����չʾ��Ϣ�����6���ӣ�
    #begin = "2015-03-04 17:40:22";
    #end = "2015-03-04 17:47:24";
    #template.setDuration(begin, end)

    return template

pushMessageToApp()
