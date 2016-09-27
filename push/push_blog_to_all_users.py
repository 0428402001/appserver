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
    message .setSpeed(100)#设置消息推送速度，单位为条/秒，例如填写100，则为100条/秒。仅支持对指定应用群推接口。
    message.data = template
    message.pushNetWorkType = 1#设置是否根据WIFI推送消息，1为wifi推送，0为不限制推送
    message.isOffline = True



    message.offlineExpireTime = 1000 * 3600 * 12
    message.appIdList.extend([APPID])
    message.phoneTypeList.extend(["ANDROID", "IOS"])
    #message.provinceList.extend(["浙江", "上海","北京"])
    #message.tagList.extend(["开心"])
    ret = push.pushMessageToApp(message)
    print ret


if __name__ == "__main__":
    blog_id = sys.argv[1]
    subject = sys.argv[2]
    app_name = sys.argv[3] 
    pushAPN( subject, blog_id, app_name)
