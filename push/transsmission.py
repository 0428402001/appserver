def TransmissionTemplateDemo():
    template = TransmissionTemplate()
    template.transmissionType = 1
    template.appId = APPID
    template.appKey = APPKEY
    template.transmissionContent = '������͸������'
    template = TransmissionTemplate()
    #����APNS��Ϣ
    apnpayload = APNPayload()
    apnpayload.badge = 4
    apnpayload.sound = "test1.wav"
    apnpayload.contentAvailable = 1
    apnpayload.category = "ACTIONABLE"

    #��������������
    alertMsg = SimpleAlertMsg()
    alertMsg.alertMsg = "alertMsg";
    #�ֵ�������������
    #alertMsg = DictionaryAlertMsg()
    #alertMsg.body = 'body'
    #alertMsg.actionLocKey = 'actionLockey'
    #alertMsg.locKey = 'lockey'
    #alertMsg.locArgs=['loc-args']
    #alertMsg.launchImage = 'launchImage'
    # IOS8.2���ϰ汾֧��
    #alertMsg.title = 'Title'
    #alertMsg.titleLocArgs = ['TitleLocArg']
    #alertMsg.titleLocKey = 'TitleLocKey'

    #���������ֵ�����AlertMsg�ͼ�����AlertMsg����֮һ
    apnpayload.alertMsg=alertMsg

    template.setApnInfo(apnpayload)

    return template