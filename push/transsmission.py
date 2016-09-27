def TransmissionTemplateDemo():
    template = TransmissionTemplate()
    template.transmissionType = 1
    template.appId = APPID
    template.appKey = APPKEY
    template.transmissionContent = '请填入透传内容'
    template = TransmissionTemplate()
    #设置APNS信息
    apnpayload = APNPayload()
    apnpayload.badge = 4
    apnpayload.sound = "test1.wav"
    apnpayload.contentAvailable = 1
    apnpayload.category = "ACTIONABLE"

    #简单类型如下设置
    alertMsg = SimpleAlertMsg()
    alertMsg.alertMsg = "alertMsg";
    #字典类型如下设置
    #alertMsg = DictionaryAlertMsg()
    #alertMsg.body = 'body'
    #alertMsg.actionLocKey = 'actionLockey'
    #alertMsg.locKey = 'lockey'
    #alertMsg.locArgs=['loc-args']
    #alertMsg.launchImage = 'launchImage'
    # IOS8.2以上版本支持
    #alertMsg.title = 'Title'
    #alertMsg.titleLocArgs = ['TitleLocArg']
    #alertMsg.titleLocKey = 'TitleLocKey'

    #可以设置字典类型AlertMsg和简单类型AlertMsg其中之一
    apnpayload.alertMsg=alertMsg

    template.setApnInfo(apnpayload)

    return template