__author__ = 'temp'
# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from urlparse import urljoin
import qiniu as QiniuClass


class Qiniu(object):
    def __init__(self, app=None):
        self.init_app(app)

    def init_app(self, app):
        self._access_key = 'UxO-Y9yMc9OZj1s-gnN5zfv6gf3wUfG8XEAjrdVa'#app.config.get('QINIU_ACCESS_KEY', '')
        self._secret_key = 'Ex9ROiR3x6TfyZPVOG8Pk6snNeESZq0Zp9BEmIQR'#app.config.get('QINIU_SECRET_KEY', '')
        self._bucket_name = 'appimg'#app.config.get('QINIU_BUCKET_NAME', '')
        domain = 'o6y4guqxy.bkt.clouddn.com'#app.config.get('QINIU_BUCKET_DOMAIN')
        if not domain:
            self._base_url = 'http://' + self._bucket_name + '.qiniudn.com'
        else:
            self._base_url = 'http://' + domain

    def save(self, data, filename=None):
        auth = QiniuClass.Auth(self._access_key, self._secret_key)
        token = auth.upload_token(self._bucket_name)
        return QiniuClass.put_data(token, filename, data)

    def delete(self, filename):
        auth = QiniuClass.Auth(self._access_key, self._secret_key)
        bucket = QiniuClass.BucketManager(auth)
        return bucket.delete(self._bucket_name, filename)

    def url(self, filename):
        return urljoin(self._base_url, filename)


qiniu_store = Qiniu()
ret, info = qiniu_store.save("asgjajgs", "1wded.jpg")
print qiniu_store.url("asgjajgs")