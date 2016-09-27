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

# http������
HOST = 'http://sdk.open.api.igexin.com/apiex.htm';
#https������
# HOST = 'https://api.getui.com/apiex.htm';

#����"Python SDK ��������"�� "�ڶ��� ��ȡ����ƾ֤ "�л�õ�Ӧ������


APPID = "mI93rjjWyH92Xw8Z6cCW69"
APPKEY = "13OsRER7KL654tKicPB2J"
MASTERSECRET = "vJbIT9iRrt81h6mUClYpR1"

def pushAPN( subject,  blog_id, app_name):

    push = IGeTui(HOST, APPKEY, MASTERSECRET)

    template = TransmissionTemplate()
    template.transmissionType = 1
    template.appId = APPID
    template.appKey = APPKEY


    apn = APNPayload()
    apn.badge = 1
    apn.contentAvailable = 1
    apn.category = "ACTIONABLE"


    alertMsg = DictionaryAlertMsg()
    pay_dict = {'id':blog_id}
    alertMsg.body = pay_dict 
    alertMsg.locKey = subject 
    alertMsg.locArgs=['loc-args']
    alertMsg.launchImage = 'launchImage'
    #alertMsg.title = 'Title'
    alertMsg.title = app_name
    alertMsg.titleLocArgs = ['TitleLocArg']
    alertMsg.titleLocKey = app_name 


    apn.alertMsg=alertMsg
    template.setApnInfo(apn)


    message = IGtAppMessage()
    message .setSpeed(100)#������Ϣ�����ٶȣ���λΪ��/�룬������д100����Ϊ100��/�롣��֧�ֶ�ָ��Ӧ��Ⱥ�ƽӿڡ�
    message.data = template
    message.pushNetWorkType = 1#�����Ƿ����WIFI������Ϣ��1Ϊwifi���ͣ�0Ϊ����������
    message.isOffline = True



    message.offlineExpireTime = 1000 * 3600 * 12
    message.appIdList.extend([APPID])
    message.phoneTypeList.extend(["ANDROID", "IOS"])
    #message.provinceList.extend(["�㽭", "�Ϻ�","����"])
    #message.tagList.extend(["����"])
    ret = push.pushMessageToApp(message)
    print ret


if __name__ == "__main__":
    blog_id = sys.argv[1]
    subject = sys.argv[2]
    app_name = sys.argv[3] 
    pushAPN( subject, blog_id, app_name)
