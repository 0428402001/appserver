# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import re
import json
import os
import time
import subprocess
import redis

import tornado.httpclient
import tornado.web
import tornado.gen
import tornado.httpserver
import tornado.ioloop
import urlparse
from tornado.httpclient import HTTPError as clientHTTPError
from tornado.web import HTTPError
#from config import web_url, backend_netloc

from sqlalchemy import text
from sqlalchemy import and_ , or_, func, distinct


from sqlalchemy.orm import scoped_session, sessionmaker, Session, object_mapper
from sqlalchemy import create_engine

import dal

from models.app_blog_praise import  AppBlogPraise
from models.app_comment_praise import  AppCommentPraise
from models.app_comment_reply import  AppCommentReply
from models.app_devicetoken import AppDevicetoken
from models.app_favorate import AppFavorate
from models.app_info import AppInfo
from models.app_message import AppMessage 
from models.app_statistics import AppStatistics
from models.app_subscription import AppSubscription 
from models.auth_classify import AuthClassify 
from models.auth_group import AuthGroup 
from models.auth_group_permissions import AuthGroupPermissions
from models.auth_permission import AuthPermission
from models.content_activity import ContentActivity
from models.content_ad import ContentAd
from models.content_auth import ContentAuth
from models.content_auth_groups import ContentAuthGroups
from models.content_auth_user_permissions import ContentAuthUserPermissions 
from models.content_blog import ContentBlog 
from models.content_blog_authclassify import ContentBlogAuthclassify 
from models.content_blog_comment import ContentBlogComment
from models.content_blog_tagmany import ContentBlogTagmany 
from models.content_category import ContentCategory
from models.content_comment import ContentComment
from models.content_hotblog import ContentHotblog
from models.content_hotcate import ContentHotcate
from models.content_hotcomment import ContentHotcomment 
from models.content_hotquery import ContentHotquery 
from models.content_hottag import ContentHottag
from models.content_indexblog import ContentIndexblog
from models.content_subscribe import ContentSubscribe
from models.content_tag import ContentTag 


from models.base_orm import change_to_json
from models.base_orm import change_to_json_1
from models.base_orm import change_to_json_2

from business_logic import get_info
import business_logic

from tornado.httpclient import AsyncHTTPClient


from concurrent.futures import ThreadPoolExecutor


from redis_cache.redis_con_pool import conn_pool_hot_category 
from redis_cache.redis_con_pool import conn_pool_hot_blog 
from redis_cache.redis_con_pool import conn_pool_test

import database


engine = create_engine(database.DB_PATH, pool_size = 6, pool_recycle=3600, echo = False)
#engine = create_engine('mysql://root:yestem@localhost:3306/collapp?charset=utf8', pool_size = 5, pool_recycle=1, echo = False)
Session = sessionmaker()
Session.configure(bind=engine)




#conn_pool_0 = redis.ConnectionPool(host='localhost', port=6379, db=0)
#redis_r_0 = redis.Redis(connection_pool=conn_pool_0)

conn_pool_blog = redis.ConnectionPool(host='localhost', port=6379, db=0)
#redis_r_blog = redis.Redis(connection_pool=conn_pool_blog)

conn_pool_relate_blog = redis.ConnectionPool(host='localhost', port=6379, db=1)
#redis_r_relate_blog = redis.Redis(connection_pool=conn_pool_relate_blog)

conn_home_page_blog_index = redis.ConnectionPool(host='localhost', port=6379, db=2)
redis_home_page_blog_index = redis.Redis(connection_pool=conn_home_page_blog_index)



conn_home_page_blog = redis.ConnectionPool(host='localhost', port=6379, db=3)
redis_home_page_blog = redis.Redis(connection_pool=conn_home_page_blog)

redis_hot_category = redis.Redis(connection_pool=conn_pool_hot_category)  


redis_hot_blog = redis.Redis(connection_pool=conn_pool_hot_blog)  


def push_message_to_uid(to_uid, subject):
    cur_session = Session()
    clu = cur_session.query(AppDevicetoken.device_token).filter(AppDevicetoken.author_id == to_uid).order_by(AppDevicetoken.id.desc()).limit(1).all()
    if len(clu) == 0:
        pass
    else:
        token = clu[0].device_token
        mk = os.path.dirname(os.path.abspath("__file__"))
        ios_dir =  "%s%s"%(mk, "/push/ios_single.py")
        cmd = ["python",ios_dir, token, subject] 
        subprocess.Popen(cmd)



def change_to_int(page):
    try:
        page = page.encode('utf-8')
        page = float(page)
        page = int(page)
    except Exception, e:
        pass
    return page 


class OrigionHandler(tornado.web.RequestHandler):

    @property
    def image_base_url(self):
        return 'http://o6y4guqxy.bkt.clouddn.com/media'


    def param(self, argument_name):
        try:
            return self.get_argument(argument_name)
        except:
            return None

    def get_page_index(self):

        try:
            page = self.get_argument('page')
        except:
            page = 1
        page = change_to_int(page)
        try:
            per_page = self.get_argument('per_page')
        except:
            per_page = 20
        per_page = change_to_int(per_page)
        start_page = (page - 1)*per_page
        if start_page < 0:
            start_page = 0
        return [start_page, per_page]



class TestHandler(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r'/ting'

    def get(self, *args, **kwargs):
        self.write('ting')


class StartupImage(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/startup/image"

    @tornado.gen.coroutine
    def get(self, *args, **kwargs):

        cur_session = Session()
        clu = cur_session.query(AppInfo.value.label("url")).filter(AppInfo.key == "url_startup_image").all()
        json_res = change_to_json(clu)
        self.write(json_res)


class Config(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/config"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        cur_session = Session()
        clu = cur_session.query(AppInfo).all()
        json_res = change_to_json(clu)
        self.write(json_res)

class Activity(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/activity"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):

        cur_session = Session()
        clu = cur_session.query(ContentActivity).all()
        json_res = change_to_json(clu)
        self.write(json_res)


class Category(OrigionHandler):#problem
    @classmethod
    def url_pattern(cls):
        return r"/category"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        json_res = get_info(self.request, args, kwargs)
        self.write(json_res)



class CategoryHot(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/category/hot"

    @tornado.gen.coroutine
    def get(self, *args, **kwargs):

        uid = self.param("uid")

        redis_record = redis_hot_category.lrange('0', 0, -1)
        hot_category = []
        for item in redis_record:
            hot_category.append(eval(item))

        json_res = change_to_json_2(hot_category)


        if uid is None:
            self.write(json_res)
        else:
            clu = business_logic.check_if_category_subscred(uid, hot_category)

            json_res = change_to_json_2(clu)
            self.write(json_res)





class AD(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/ad"

    @tornado.gen.coroutine
    def get(self, *args, **kwargs):

        import logging
        def set_log(log_filename, log_message):
            logger=logging.getLogger()
            handler=logging.FileHandler(log_filename)
            logger.addHandler(handler)
            logger.setLevel(logging.NOTSET)
            logger.debug(log_message)
            # 如果没有此句话，则会将同一个message追加到不同的log中
            logger.removeHandler(handler)
        message = "AD\t%s\t%s"%(time.ctime(), self.request)
        set_log("/tmp/log", message)
        print "ADVERTISE\t%s\t%s"%(time.ctime(), self.request)
        json_res = get_info(self.request, args, kwargs)
        ad_list = json.loads(json_res)
        for i in ad_list:
            i['url'] = "http://app.collegedaily.cn/adsta?url=%s"%i["url"]
        json_res = change_to_json_2(ad_list)
        self.write(json_res)




class CategorySubscription(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/category/subscription"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        uid =  self.param("uid")
        json_res = get_info(self.request, args, kwargs)
        self.write(json_res)

    @tornado.gen.coroutine
    def post(self, *args, **kwargs):

        func_type = self.param('type')
        uid = self.param('uid')
        category_id = self.param('category_id')

        if func_type == 'remove':
            cur_session = Session()
            cur_session.query(AppSubscription).filter(and_(AppSubscription.author_id == uid, AppSubscription.category_id == category_id)).delete()
            try:
                cur_session.commit()
            except Exception, e:
                cur_session.rollback()
                print self.url_pattern(), e
            finally:
                cur_session.close()
            clu = {'resutl':1, 'error':'/category/subscription remove success'}
        elif func_type == 'add':

            cur_session = Session()
            app_sub =AppSubscription(author_id = uid, category_id = category_id)
            cur_session.add(app_sub)
            try:
                cur_session.commit()
            except Exception, e:
                cur_session.rollback()
                print self.url_pattern(), e
            finally:
                cur_session.close()
            clu = {'resutl':1, 'error':'/category/subscription add success'}
        else:
            clu = {'resutl':0, 'error':'wrong parameter.'}
        json_res = change_to_json_2(clu)
        self.write(json_res)









class CategorySubscriptionstate(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/category/subscription_state"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):

        cur_session = Session()
        uid = self.param('uid')
        category_id = self.param('category_id')
        clu = cur_session.query(AppSubscription).filter(text("app_subscription.author_id = :uid and app_subscription.category_id = :category_id")).params(uid = uid, category_id = category_id).all()
        json_res = change_to_json(clu)
        self.write(json_res)

class UpdateImage(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/update/image"
    @tornado.gen.coroutine
    def post(self, *args, **kwargs):
        if self.request.files:
            time_samp = time.strftime('%Y-%m-%d-%H:%M:%S')
            img = self.request.files['img'][0]
            imgname = img['filename']
            filepath = os.path.join('/var/www/html/media',time_samp+imgname)
            with open(filepath,'wb+') as up:
                up.write(img['body'])
            head_url = 'http://o6y4guqxy.bkt.clouddn.com/media/'+time_samp+imgname
            clu = {'head_url':head_url}
            json_res = change_to_json_2(clu)
            self.write(json_res)

class UserRegister(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/user/register"
    @tornado.gen.coroutine
    def post(self,*args,**kwargs):
        cur_session = Session()
        head = self.param("headImage")
        nickname = self.param('nickname')
        sex = self.param('sex')
        device_token = self.param("device_token")
        phone = self.param('phone')
        last_login = time.strftime('%Y-%m-%d %H:%M:%S')
        date_joined = last_login

        email = self.param("email")
        if email is None:
            email = ''
        password = self.param('password')
        if password is None:
            password = ''

        check_result = cur_session.query(ContentAuth.id).filter(ContentAuth.phone == phone).all()
        if len(check_result) == 0:
            content_auth_imp = ContentAuth(email = email, password = password, username = nickname, last_login = last_login, date_joined = date_joined, head = head, nickname = nickname, regist_from = 0)
            cur_session.add(content_auth_imp)
            try:
                cur_session.flush()
                cur_session.commit()
            except Exception, e:
                cur_session.rollback()
                print "USER/LOGIN_login_problem\t%s\t%s"%(phone. e)
            finally:
                pass
            return_uid = content_auth_imp.id

            cur_session.close()

        else:
            return_uid = check_result[0].id
            cur_session.query(ContentAuth).filter(ContentAuth.id == return_uid).update({ContentAuth.last_login: last_login})
            try:
                cur_session.flush()
                cur_session.commit()
            except Exception, e:
                cur_session.rollback()
                print self.url_pattern(), e
            finally:
                pass
                cur_session.close()
        print "login_in_succed"

        #regist device token
        if device_token  is not None:
            print device_token
            print return_uid
            dt = time.strftime('%Y-%m-%d %H:%M:%S')
            def datetime_timestamp(dt):
                time.strptime(dt, '%Y-%m-%d %H:%M:%S')
                s = time.mktime(time.strptime(dt, '%Y-%m-%d %H:%M:%S'))
                return int(s)
            d = datetime_timestamp(dt)
            app_dev_clu = cur_session.query(AppDevicetoken).filter(and_(AppDevicetoken.author_id == return_uid)).all()
            if len(app_dev_clu) == 0:
                pass
                cur_session.add(AppDevicetoken(author_id = return_uid, device_token = device_token, update_dateline = d))
                try:
                    cur_session.flush()
                    cur_session.commit()
                except Exception, e:
                    cur_session.rollback()
                    print self.url_pattern(), e
                finally:
                    cur_session.close()
            else:
                pass
                cur_session.query(AppDevicetoken).filter(and_(AppDevicetoken.author_id == return_uid)).update({AppDevicetoken.update_dateline: d, AppDevicetoken.device_token:device_token})
                try:
                    cur_session.flush()
                    cur_session.commit()
                except Exception, e:
                    cur_session.rollback()
                    print self.url_pattern(), e
                finally:
                    cur_session.close()
        clu = {'uid':return_uid}
        clu_json = change_to_json_2(clu)
        self.write(clu_json)



class UserLogin(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/user/login"
    @tornado.gen.coroutine
    def get(self,*args,**kwargs):
        cur_session = Session()
        phone =  self.param("phone")
        return_data = cur_session.query(ContentAuth.id).filter(text("content_auth.phone = :phone")).params(phone = phone).all()
        clu = {'uid':return_data[0].id}
        json_res = change_to_json_2(clu)
        self.write(json_res)

class UserProfile(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/user/profile"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        cur_session = Session()
        clu = cur_session.query(ContentAuth.id, ContentAuth.nickname, ContentAuth.sign,ContentAuth.head,ContentAuth.school,ContentAuth.grade,AuthClassify.name.label("identity")).join(AuthClassify, ContentAuth.identity == AuthClassify.id).filter(text("content_auth.id = :uid")).params(uid = uid).all()
        json_res = change_to_json(clu)
        self.write(json_res)

    @tornado.gen.coroutine
    def post(self, *args, **kwargs):

        cur_session = Session()
        sns_uid = self.param('sns_uid')
        sns_type = self.param('sns_type')
        sns_nickname = self.param('sns_nickname')
        sns_head = self.param("sns_headImage")
        device_token = self.param("device_token")
        last_login = time.strftime('%Y-%m-%d %H:%M:%S')
        date_joined = last_login
        email = self.param("email")
        
        if email is None:
            email = ''
        password = self.param('password')
        if password is None:
            password = ''

        print 'sns_uid\t%s\tsun_nickname\t%s\tsns_head\t%s\tdevice_token\t%s\temail\t%s\tpassword\t%s\tsns_type\t%s'%(sns_uid, sns_nickname, sns_head, device_token, email, password, sns_type)


        check_result = cur_session.query(ContentAuth.id).filter(ContentAuth.sns_uid == sns_uid).all()

        return_uid = -1
        if len(check_result) == 0:
            content_auth_imp = ContentAuth(email = email, password = password, username = sns_nickname, last_login = last_login, date_joined = date_joined, head = sns_head, nickname = sns_nickname, regist_from = 1, sns_type = sns_type, sns_uid = sns_uid)
            cur_session.add(content_auth_imp)
            try:
                cur_session.flush()
                cur_session.commit()
            except Exception, e:
                cur_session.rollback()
                print "USER/PROFILE_login_problem\t%s\t%s"%(sns_uid. e)
            finally:
                pass
            return_uid = content_auth_imp.id

            cur_session.close()

        else:
            return_uid = check_result[0].id
            cur_session.query(ContentAuth).filter(ContentAuth.id == return_uid).update({ContentAuth.last_login: last_login})
            try:
                cur_session.flush()
                cur_session.commit()
            except Exception, e:
                cur_session.rollback()
                print self.url_pattern(), e
            finally:
                pass
                cur_session.close()
        print "login_in_succed"

        #regist device token
        if device_token  is not None:
            print device_token
            print return_uid
            dt = time.strftime('%Y-%m-%d %H:%M:%S')
            def datetime_timestamp(dt):
                time.strptime(dt, '%Y-%m-%d %H:%M:%S')
                s = time.mktime(time.strptime(dt, '%Y-%m-%d %H:%M:%S'))
                return int(s)
            d = datetime_timestamp(dt)
            app_dev_clu = cur_session.query(AppDevicetoken).filter(and_(AppDevicetoken.author_id == return_uid)).all()
            if len(app_dev_clu) == 0:
                pass
                cur_session.add(AppDevicetoken(author_id = return_uid, device_token = device_token, update_dateline = d))
                try:
                    cur_session.flush()
                    cur_session.commit()
                except Exception, e:
                    cur_session.rollback()
                    print self.url_pattern(), e
                finally:
                    cur_session.close()
            else:
                pass
                cur_session.query(AppDevicetoken).filter(and_(AppDevicetoken.author_id == return_uid)).update({AppDevicetoken.update_dateline: d, AppDevicetoken.device_token:device_token})
                try:
                    cur_session.flush()
                    cur_session.commit()
                except Exception, e:
                    cur_session.rollback()
                    print self.url_pattern(), e
                finally:
                    cur_session.close()
        clu = {'uid':return_uid}
        clu_json = change_to_json_2(clu)
        self.write(clu_json)



class UpdateToken(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/update/token"
    @tornado.gen.coroutine
    def post(self, *args, **kwargs):
        cur_session = Session()
        uid = self.param('user_uid')
        device_token = self.param("device_token")

        dt = time.strftime('%Y-%m-%d %H:%M:%S')
        def datetime_timestamp(dt):
            time.strptime(dt, '%Y-%m-%d %H:%M:%S')
            s = time.mktime(time.strptime(dt, '%Y-%m-%d %H:%M:%S'))
            return int(s)
        d = datetime_timestamp(dt)
        clu = cur_session.query(AppDevicetoken.id).filter(and_(AppDevicetoken.author_id == uid)).order_by(AppDevicetoken.id.desc()).limit(1).all()
        if clu:
            device_id = clu[0].id
            cur_session.query(AppDevicetoken).filter(AppDevicetoken.id == device_id).update({AppDevicetoken.update_dateline: d, AppDevicetoken.device_token:device_token})
            try:
                cur_session.flush()
                cur_session.commit()
            except Exception, e:
                cur_session.rollback()
                print self.url_pattern(), e
            finally:
                cur_session.close()
        else:
            pass
        self.write('token_updated')




    



class UserClassify(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/user/classify"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):

        cur_session = Session()
        clu = cur_session.query(AuthClassify).order_by(AuthClassify.id)
        json_res = change_to_json(clu)
        self.write(json_res)


class MenuInfo(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/menu/info"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        cur_session = Session()
        t_di = {}
        uid = self.param("uid")
        clu = cur_session.query(AppMessage.id).filter(and_(AppMessage.is_read == "0", AppMessage.message_to == uid))
        json_res = change_to_json(clu)
        clu = json.loads(json_res)
        t_di["unread_messages"] = clu

        clu = cur_session.query(ContentBlog.id).filter(ContentBlog.praise_count > "2")
        json_res = change_to_json(clu)
        clu = json.loads(json_res)
        t_di["new_blogs"] = clu

        json_res = json.dumps(t_di)
        self.write(json_res)


class QueryHot(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/query/hot"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        json_res = get_info(self.request, args, kwargs)
        self.write(json_res)



class BlogHot(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/blog/hot"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        json_res = get_info(self.request, args, kwargs)
        self.write(json_res)


class BlogIndex(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/blog/index"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        redis_record = redis_home_page_blog_index.lrange('0', 0, -1)
        blog_index_s = [] 
        for item in redis_record:
            blog_index_s.append(eval(item))
        json_res = change_to_json_2(blog_index_s)
        #json_res = get_info(self.request, args, kwargs)
        self.write(json_res)




class Blog(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/blog"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        p = self.get_page_index() 
        p_start = p[0]
        p_end = p[0] + p[1] -1
        record = redis_home_page_blog.lrange('0', p_start, p_end)
        blog_s = []
        for item in record:
            blog_s.append(eval(item))
        json_res = change_to_json_2(blog_s)

        #json_res = get_info(self.request, args, kwargs)

        self.write(json_res)


class BlogCategory(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/blog/category/(\d*)"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        json_res = get_info(self.request, args, kwargs)
        self.write(json_res)




class BlogFavorateUID(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/blog/favorate/(\d*)"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        json_res = get_info(self.request, args, kwargs)
        self.write(json_res)





class BlogPraise(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/blog/praise"


    @tornado.gen.coroutine
    def post(self, *args, **kwargs):
        func_type = self.param('type')
        uid = self.param('uid')
        blog_id = self.param('blog_id')

        cur_session = Session()
        if func_type == 'remove':
            cur_session.query(AppBlogPraise).filter(and_(AppBlogPraise.author_id == uid, AppBlogPraise.blog_id == blog_id)).delete()
            cur_session.query(ContentBlog).filter(ContentBlog.id == blog_id).update({ContentBlog.praise_count : ContentBlog.praise_count - 1})
            try:
                cur_session.flush()
                cur_session.commit()
            except Exception, e:
                cur_session.rollback()

            finally:
                cur_session.close()
            clu = {'resutl':1, 'error':'/blog/praise remove success'}
        elif func_type == 'add':
            cur_session.add(AppBlogPraise(author_id = uid, blog_id = blog_id))
            cur_session.query(ContentBlog).filter(ContentBlog.id == blog_id).update({ContentBlog.praise_count : ContentBlog.praise_count + 1})
            try:
                cur_session.flush()
                cur_session.commit()
            except Exception, e:
                cur_session.rollback()
            finally:
                cur_session.close()
            clu = {'resutl':1, 'error':'/blog/praise add success'}
        else:
            clu = {'resutl':0, 'error':'wrong parameter.'}
        json_res = change_to_json_2(clu)
        self.write(json_res)






class BlogFavorate(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/blog/favorate"
    @tornado.gen.coroutine
    def post(self, *args, **kwargs):
        func_type = self.param('type')
        uid = self.param('uid')
        blog_id = self.param('blog_id')
        cur_session = Session()
        if func_type == 'remove':
            cur_session.query(AppFavorate).filter(and_(AppFavorate.author_id == uid, AppFavorate.blog_id == blog_id)).delete()
            try:
                cur_session.flush()
                cur_session.commit()
            except Exception, e:
                cur_session.rollback()
                print self.url_pattern(), e
            finally:
                cur_session.close()
            clu = {'resutl':1, 'error':'/blog/favorate remove success'}
        elif func_type == 'add':

            if_exit_clu = cur_session.query(AppFavorate).filter(and_(AppFavorate.author_id == uid, AppFavorate.blog_id == blog_id)).all()
            if len(if_exit_clu) == 0:
                cur_session.add(AppFavorate(author_id = uid, blog_id = blog_id))

                try:
                    cur_session.flush()
                    cur_session.commit()
                except Exception, e:
                    cur_session.rollback()
                    print self.url_pattern(), e
                finally:
                    cur_session.close()

            else:
                pass
            clu = {'resutl':1, 'error':'/blog/favorate add success'}
        else:
            clu = {'resutl':0, 'error':'wrong parameter.'}
        json_res = change_to_json_2(clu)
        self.write(json_res)


class BlogQuery(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/blog/query/(.*)"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        json_res = get_info(self.request, args, kwargs)
        self.write(json_res)


class TagBlog(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/tag/(\d*)"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        blog_id = args[0]
        cur_session = Session()
        clu = cur_session.query(ContentTag.id.label('id'), ContentTag.name.label('name')).join(ContentBlogTagmany, ContentTag.id == ContentBlogTagmany.tag_id).filter(ContentBlogTagmany.blog_id == blog_id).all()
        json_res = change_to_json_1(clu)
        self.write(json_res)






class BlogTag(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/blog/tag/(\d*)"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        tag_id = args[0]
        cur_session = Session()
        clu = cur_session.query(ContentBlog.id, ContentBlog.title, func.replace(ContentBlog.cover,'covers', '%s/covers'%self.image_base_url).label("cover"), func.replace(ContentBlog.thumb, 'thumb/', '%s/thumb/'%self.image_base_url).label("thumb"),ContentBlog.date,ContentBlog.abstract,ContentBlog.category_id, ContentCategory.name.label("category_name"), ContentBlog.tag_id, ContentTag.name.label("tag_name"), ContentBlog.is_out, ContentBlog.is_big, ContentBlog.index_pic, ContentBlog.source, ContentBlog.source_url).join(ContentCategory, ContentBlog.category_id == ContentCategory.id).join(ContentTag, ContentBlog.tag_id == ContentTag.id).filter(text("content_blog.tag_id = :tag_id")).params(tag_id =  tag_id).all()
        json_res = change_to_json_1(clu)
        self.write(json_res)


class BlogID(OrigionHandler):#problem
    @classmethod
    def url_pattern(cls):
        return r"/blog/(\d{1,})"
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):#need
        json_res = get_info(self.request, args, kwargs)
        self.write(json_res)
        self.finish()



class CommentHot(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/comment/hot/(\d*)"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        blog_id = args[0]
        cur_session = Session()
        clu = cur_session.query(ContentBlogComment.id,  ContentComment.content, ContentComment.author_id, ContentComment.aauthor, ContentComment.time).join(ContentComment, ContentBlogComment.comment_id == ContentComment.id).filter(text("content_blog_comment.blog_id = :blog_id")).params(blog_id =  blog_id).all()
        json_res = change_to_json(clu)
        self.write(json_res)



class CommentBlog(OrigionHandler):#problem
    @classmethod
    def url_pattern(cls):
        return r"/comment/(\d*)"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        print self.request
        p = self.get_page_index() 
        uid = self.param('uid')
        blog_id = args[0]
        cur_session = Session()
        comments = cur_session.query(ContentBlogComment.comment_id,  ContentComment.content, ContentComment.author_id, ContentAuth.nickname, ContentComment.praise_count, ContentComment.time, func.replace(ContentAuth.head, 'covers/', '%s/covers'%self.image_base_url).label('head')).join(ContentComment, ContentBlogComment.comment_id == ContentComment.id).join(ContentAuth, ContentComment.author_id == ContentAuth.id).filter(text("content_blog_comment.blog_id = :blog_id and content_comment.visible = 1")).params(blog_id =  blog_id).order_by(ContentComment.id.desc()).offset(p[0]).limit(p[1]).all()
        json_res = change_to_json_1(comments)
        if uid is not None:
            comments = json.loads(json_res)
            for index in xrange(len(comments)):
                comment_id = comments[index]['comment_id']
                comment_praise = cur_session.query(AppCommentPraise.id).filter(and_(AppCommentPraise.comment_id ==  comment_id, AppCommentPraise.author_id == uid)).all()
                if len(comment_praise) == 0:
                    comments[index]['praise_state'] = 0 
                else:
                    comments[index]['praise_state'] = 1 
            json_res = change_to_json_2(comments)
        json_res = "[]"
        self.write(json_res)


class Comment(OrigionHandler):#problem
    @classmethod
    def url_pattern(cls):
        return r"/comment"

    @tornado.gen.coroutine
    def post(self, *args, **kwargs):
        blog_id = self.param('blog_id')
        content = self.param('content')
        uid = self.param('uid')
        ip = self.request.remote_ip 
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')
        content_comment_imp = ContentComment(content =content , author_id =uid , aauthor =ip , time = current_time)
        cur_session = Session()
        cur_session.add(content_comment_imp)
        try:
            cur_session.commit()
            comment_id = content_comment_imp.id
        except Exception, e:
            cur_session.rollback()
            print self.url_pattern(), e
        finally:
            cur_session.close()

        cur_session.add(ContentBlogComment(blog_id =blog_id , comment_id = comment_id))
        try:
            cur_session.flush()
            cur_session.commit()
        except Exception, e:
            cur_session.rollback()
            print self.url_pattern(), e
        finally:
            cur_session.close()
        res = {'result':"1", "error":"/comment add success"}
        res_json = json.dumps(res)
        self.write(res_json)



class CommentPraiseCommentID(OrigionHandler):#problem
    @classmethod
    def url_pattern(cls):
        return r"/comment/praise/(\d*)"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        comment_id = args[0]
        p = self.get_page_index() 
        message_id = self.param('message_id') 
        try:
            message_id = message_id.encode('utf-8')
        except:
            pass
        try:
            message_id = int(message_id)
        except:
            pass

        json_res = get_info(self.request, args, kwargs)
        cur_session = Session()
        cur_session.query(AppMessage).filter(AppMessage.id == message_id).update({AppMessage.is_read:1})
        try:
            cur_session.flush()
            cur_session.commit()
        except Exception, e:
            cur_session.rollback()
            print self.url_pattern(), e

        finally:
            cur_session.close()
        self.write(json_res)


    @tornado.gen.coroutine
    def post(self, *args, **kwargs):
        pass



class CommentPraise(OrigionHandler):#problem
    @classmethod
    def url_pattern(cls):
        return r"/comment/praise"
    @tornado.gen.coroutine
    def post(self, *args, **kwargs):
        praise_type = self.param("type") 
        uid = self.param("uid")
        nickname = self.param('nickname')
        blog_id = self.param('blog_id')
        comment_id = self.param("comment_id")
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')

        cur_session = Session()
        if praise_type == 'add':
            cur_session.add(AppCommentPraise(author_id = uid, comment_id = comment_id))
            cur_session.query(ContentComment).filter(ContentComment.id ==  comment_id).update({ContentComment.praise_count : ContentComment.praise_count + 1})
            try:
                cur_session.flush()
                cur_session.commit()
            except Exception, e:
                cur_session.rollback()
            finally:
                cur_session.close()
            old_comment = cur_session.query(ContentComment.author_id, ContentComment.content, ContentComment.praise_count).filter(ContentComment.id == comment_id)
            to_uid = old_comment[0].author_id
            content = old_comment[0].content
            praise_count = old_comment[0].praise_count
            abstr_content = content[:100]
            if praise_count > 1:
                subject = "%s 等 %s 人赞了您的评论：%s"%(nickname, praise_count, abstr_content)
            else:
                subject = '%s赞了您的评论： %s'%(nickname, abstr_content)
            cur_session.merge(AppMessage(message_from = uid, message_to = to_uid, subject = subject, date = current_time, message_type = 2, blog_id = blog_id, comment_id = comment_id)) 

            try:
                cur_session.flush()
                cur_session.commit()
            except Exception, e:
                cur_session.rollback()
                print self.url_pattern(), e
            finally:
                cur_session.close()

            push_message_to_uid(to_uid, subject)
            clu = {'resutl':1, 'error':'/comment/praise add success'}

        elif praise_type == 'remove':
            cur_session.query(AppCommentPraise).filter(and_(AppCommentPraise.author_id == uid, AppCommentPraise.comment_id == comment_id)).deletee()
            cur_session.query(ContentComment).filter(ContentComment.id ==  comment_id).update({ContentComment.praise_count : ContentComment.praise_count - 1})
            try:
                cur_session.flush()
                cur_session.commit()
            except Exception, e:
                cur_session.rollback()
                print self.url_pattern(), e
            finally:
                cur_session.close()
            clu = {'resutl':1, 'error':'/comment/praise remove success'}
        else:
            clu = {'resutl':0, 'error':'wrong parameter.'}
        json_res = change_to_json_2(clu)
        self.write(json_res)


class CommentReplyComment_id(OrigionHandler):#problem
    @classmethod
    def url_pattern(cls):
        return r"/comment/reply/(\d*)"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        json_res = get_info(self.request, args, kwargs)
        message_id = self.param('message_id')
        cur_session = Session()
        cur_session.query(AppMessage).filter(AppMessage.id == message_id).update({AppMessage.is_read: 1})
        try:
            cur_session.flush()
            cur_session.commit()
        except Exception, e:
            cur_session.rollback()
            print self.url_pattern(), e
        finally:
            cur_session.close()
        self.write(json_res)


class CommentReply(OrigionHandler):#problem
    @classmethod
    def url_pattern(cls):
        return r"/comment/reply"
    @tornado.gen.coroutine
    def post(self, *args, **kwargs):
        uid = self.param("uid")
        nickname =  self.param('nickname')
        blog_id = self.param('blog_id')
        comment_id = self.param('comment_id')
        content = self.param('content')
        ip = self.request.remote_ip
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')
        content_comment_imp = ContentComment(content =content , author_id =uid , aauthor =ip , time = current_time)
        cur_session = Session()
        cur_session.add(content_comment_imp)
        try:
            cur_session.flush()
            cur_session.commit()
            reply_comment_id = content_comment_imp.id
        except Exception, e:
            cur_session.rollback()
            print self.url_pattern(), e
        finally: 
            cur_session.close()
        cur_session.add(ContentBlogComment(blog_id =blog_id , comment_id = reply_comment_id))
        old_comment = cur_session.query(ContentComment.author_id, ContentComment.content).filter(ContentComment.id ==  comment_id).all()
        cur_session.add(AppCommentReply(comment_id = comment_id, reply_id = reply_comment_id))

        try:
            cur_session.flush()
            cur_session.commit()
        except Exception, e:
            cur_session.rollback()
            print self.url_pattern(), e
        finally: 
            cur_session.close()
        to_uid = old_comment[0].author_id
        content = old_comment[0].content
        abstract_content = content[:100]
        subject = '%s等人回复了您的评论：%s'%(nickname, abstract_content)
        push_message_to_uid(to_uid, subject)
        cur_session.merge(AppMessage(message_from = uid, message_to = to_uid, subject = subject, date = current_time, message_type = 1, blog_id = blog_id, comment_id = comment_id)) 
        try:
            cur_session.flush()
            cur_session.commit()
        except Exception, e:
            cur_session.rollback()
            print self.url_pattern(), e
        finally: 
            cur_session.close()
        json_res = json.dumps({"result":1, "error":"/comment/reply success"})#problem
        self.write(json_res)



class CommentReport(OrigionHandler):#problem
    @tornado.gen.coroutine
    def post(self, *args, **kwargs):
        uid = self.param('uid')
        comment_id = self.param('comment_id')
        cur_session = Session()
        cur_session.query(ContentComment).filter(ContentComment.id == comment_id).update({ContentComment.report_count: ContentComment.report_count + 1})
        try:
            cur_session.flush()
            cur_session.commit()
        except Exception, e:
            cur_session.rollback()
            print self.url_pattern(), e
        finally: 
            cur_session.close()
        json_res = json.dumps({"result":1, "error":"/comment/report success"})#problem
        self.write(json_res)



class Message(OrigionHandler):#message
    @classmethod
    def url_pattern(cls):
        return r"/message/(\d*)"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        json_res = get_info(self.request, args, kwargs)
        self.write(json_res)


class MessageAllreadyRead(OrigionHandler):#message
    @classmethod
    def url_pattern(cls):
        return r"/message/allreadyread/(\d*)"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        json_res = get_info(self.request, args, kwargs)
        self.write(json_res)







class Blogview(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/blogview/(\d*)"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        blog_id = args[0]
        json_res = get_info(self.request, args, kwargs)
        record = json.loads(json_res)
        clu = record['blog']
        relate_blog = record['related_blog'][0:2]
        comment_cnt = clu['comment_count']
        self.render('blog.html', id = clu["id"], title = clu['title'], content = clu['content'], cover = clu['cover'], blog = '2016-5-40', author = clu['author'], date = clu['date'], time = clu['date'], abstract = clu['abstract'], comment_cnt = clu['comment_count'], relate_blog = relate_blog)



class Setting(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/setting"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        uid = self.param('uid') 
        cur_session = Session()
        if uid is None:
            pass
        else:
            clu = cur_session.query(AppDevicetoken.enable_push).filter(text("app_devicetoken.author_id = :uid")).params(uid = uid).all()
            json_res = change_to_json(clu)
            self.write(json_res)



class FlushAllCache(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/flush_all_cache"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        file_dir=os.path.join(os.path.dirname(__file__), "redis_cache/redis_cache/sync_cache.sh"),
        cmd_str = "sh %s"%file_dir
        os.system(cmd_str)
        self.write('%s\tcache_allready_flushed'%cmd_str)


class FlushSingleBlogContent(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/flush_single_blog_content/(\d{1,})"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        blog_id = args[0]
        tt = os.path.dirname(os.path.abspath(__file__))
        file_dir = "%s/redis_cache/redis_cache/flush_singal_blog.py"%(os.path.dirname(__file__))
        cmd_str = "python %s %s"%(file_dir, blog_id)
        os.system(cmd_str)
        self.write('%s\tcache_allready_flushed'%cmd_str)

class FlushHomePageBlog(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/flush_home_page_blog"

    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        tt = os.path.dirname(os.path.abspath(__file__))
        file_dir = "%s/redis_cache/redis_cache/flush_home_page_blog.py"%(os.path.dirname(__file__))
        cmd_str = "python %s"%file_dir
        os.system(cmd_str)
        self.write('%s\tcache_allready_flushed'%cmd_str)


class FlushHomePageBlogIndex(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/flush_home_page_blog_index"

    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        tt = os.path.dirname(os.path.abspath(__file__))
        file_dir = "%s/redis_cache/redis_cache/flush_home_page_blog_index.py"%(os.path.dirname(__file__))
        cmd_str = "python %s"%file_dir
        os.system(cmd_str)
        self.write('%s\tcache_allready_flushed'%cmd_str)




class PushBlogToAllUsers(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/push_blog_to_all_users/(\d*)"

    @tornado.gen.coroutine
    def get(self, *args, **kwargs):

        blog_id = args[0]
        print "PUSH", time.ctime(),self.request
        def push_message_to_all_users(subject):
            app_name = '留学生日报'
            mk = os.path.dirname(os.path.abspath("__file__"))
            ios_dir =  "%s%s"%(mk, "/push/push_blog_to_all_users.py")
            cmd = ["python",ios_dir, blog_id, subject, app_name] 
            subprocess.Popen(cmd)


        engine_for_push = create_engine(database.DB_PATH)
        Session_for_push = sessionmaker()
        Session_for_push.configure(bind=engine_for_push)


        cur_session = Session_for_push()
        clu = cur_session.query(ContentBlog.title).filter(ContentBlog.id == blog_id).all()
        cur_session.close()
        if not clu:
            self.write('no_such_blog')
        else:
            title = clu[0].title
            push_message_to_all_users(title)
            self.write('blog_pushed')
    



class PushBlogToAPPID(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/push_blog_to_appid/(\d*)"

    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        blog_id = args[0]
        print blog_id
        def push_message_to_appid(subject):
            app_name = '留学生日报'
            mk = os.path.dirname(os.path.abspath("__file__"))
            ios_dir =  "%s%s"%(mk, "/push/push_blog_to_appid.py")
            cmd = ["python",ios_dir, blog_id, subject, app_name] 
            subprocess.Popen(cmd)

        cur_session = Session()
        clu = cur_session.query(ContentBlog.title).filter(ContentBlog.id == blog_id).all()
        if not clu:
            self.write('no_such_blog')
        else:
            title = clu[0].title
            push_message_to_appid(title)
            self.write('blog_pushed')
    



class AdsTa(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/adsta"
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):

        redirect_url = self.param('url')
        if redirect_url:
            self.redirect(redirect_url)
        else:
            self.write('None')







class Test1(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/test1"
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        self.write("22220")




class Test2(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/test2"

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):

        blog_id = "1177"
        print "PUSH", time.ctime(),self.request
        def push_message_to_all_users_test(subject):
            app_name = '留学生日报'
            mk = os.path.dirname(os.path.abspath("__file__"))
            ios_dir =  "%s%s"%(mk, "/push/push_blog_to_all_users_test.py")
            cmd = ["python",ios_dir, blog_id, subject, app_name] 
            subprocess.Popen(cmd)


        engine_for_push = create_engine(database.DB_PATH)
        Session_for_push = sessionmaker()
        Session_for_push.configure(bind=engine_for_push)


        cur_session = Session_for_push()
        clu = cur_session.query(ContentBlog.title).filter(ContentBlog.id == blog_id).all()
        cur_session.close()
        if not clu:
            self.write('no_such_blog')
        else:
            title = clu[0].title
            push_message_to_all_users_test(title)
            self.write('blog_pushed')
        self.write("10")



    def on_fetch(self, response):
        self.write("sleep 6")
        self.finish()


class Rss(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/rss"


    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        cur_session = Session()
        clus = cur_session.query(ContentBlog.id, ContentBlog.title, func.replace(ContentBlog.cover,'covers', '%s/covers'%self.image_base_url).label("cover"), func.replace(ContentBlog.thumb, 'thumb/', '%s/thumb/'%self.image_base_url).label("thumb"),ContentBlog.date,ContentBlog.abstract, ContentBlog.content, ContentBlog.source).filter(ContentBlog.hotness == 0).order_by(ContentBlog.id.desc()).limit(30).all()
        cur_session.close()
        clu_json = change_to_json_1(clus)
        clus = json.loads(clu_json)
        copyright = "本文经授权转载自北美留学生日报，Collegedaily.cn，All Rights Reserved"
        self.render('rss.html', clus = clus, copyright = copyright)

