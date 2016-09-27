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

from models.base_orm import Session

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

from tornado.httpclient import AsyncHTTPClient


from concurrent.futures import ThreadPoolExecutor


from redis_cache.redis_con_pool import conn_pool_hot_category 
from redis_cache.redis_con_pool import conn_pool_hot_blog 
from redis_cache.redis_con_pool import conn_pool_test



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
    clu = Session.query(AppDevicetoken.device_token).filter(AppDevicetoken.author_id == to_uid).order_by(AppDevicetoken.id.desc()).limit(1).all()
    if len(clu) == 0:
        pass
    else:
        token = clu[0].device_token
        mk = os.path.dirname(os.path.abspath("__file__"))
        print mk
        ios_dir =  "%s%s"%(mk, "/push/ios_single.py")
        cmd = ["python",ios_dir, token, subject] 
        subprocess.Popen(cmd)



def change_to_int(page):
    try:
        page = page.encode('utf-8')
        page = float(page)
        page = int(page)
    except:
        pass
    return page 


#class Cache(object):
#    def get_author_dict():
#        clu = Session.query(ContentAuth).all()
#        json_res = change_to_json(clu)
#        #auth_res = json.loads(json_res)
#        return json_res
#
#    author = get_author_dict()


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
        #print start_page, per_page
        if start_page < 0:
            start_page = 0
        return [start_page, per_page]



class TestHandler(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r'/ting'

    def get(self, *args, **kwargs):
        #clu = Session.query(ContentAuth.id.label('newcolumn'), ContentAuth.password.label("pa_t")).filter(ContentAuth.id == "1").all()
        #json_res = change_to_json(clu)
        #self.write(json_res)
        self.write('ting')


class StartupImage(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/startup/image"

    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        clu = Session.query(AppInfo.value.label("url")).filter(AppInfo.key == "url_startup_image").all()
        json_res = change_to_json(clu)
        self.write(json_res)


class Config(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/config"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        clu = Session.query(AppInfo).all()
        json_res = change_to_json(clu)
        self.write(json_res)

class Activity(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/activity"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        clu = Session.query(ContentActivity).all()
        json_res = change_to_json(clu)
        self.write(json_res)


class Category(OrigionHandler):#problem
    @classmethod
    def url_pattern(cls):
        return r"/category"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        print self.request
        json_res = get_info(self.request, args, kwargs)
        self.write(json_res)



class CategoryHot(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/category/hot"

    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        print self.request


        redis_record = redis_hot_category.lrange('0', 0, -1)
        hot_category = []
        for item in redis_record:
            hot_category.append(eval(item))

        json_res = change_to_json_2(hot_category)
        #json_res = get_info(self.request, args, kwargs)
        self.write(json_res)



class AD(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/ad"

    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        print self.request
        json_res = get_info(self.request, args, kwargs)
        self.write(json_res)




class CategorySubscription(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/category/subscription"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        print self.request
        uid =  self.param("uid")
        json_res = get_info(self.request, args, kwargs)
        self.write(json_res)

    @tornado.gen.coroutine
    def post(self, *args, **kwargs):
        print self.request
        func_type = self.param('type')
        uid = self.param('uid')
        category_id = self.param('category_id')

        if func_type == 'remove':
            Session.query(AppSubscription).filter(and_(AppSubscription.author_id == uid, AppSubscription.category_id == category_id)).delete()
            try:
                Session.flush()
                Session.commit()
            except Exception, e:
                Session.rollback()
                print e
            finally:
                Session.close()
            clu = {'resutl':1, 'error':'/category/subscription remove success'}
        elif func_type == 'add':
            Session.add(AppSubscription(author_id = uid, category_id = category_id))
            try:
                Session.flush()
                Session.commit()
            except Exception, e:
                Session.rollback()
                print e
            finally:
                Session.close()
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
        print self.request
        uid = self.param('uid')
        category_id = self.param('category_id')
        clu = Session.query(AppSubscription).filter(text("app_subscription.author_id = :uid and app_subscription.category_id = :category_id")).params(uid = uid, category_id = category_id).all()
        json_res = change_to_json(clu)
        self.write(json_res)





class UserProfile(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/user/profile"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        print self.request
        clu = Session.query(ContentAuth.id, ContentAuth.nickname, ContentAuth.sign,ContentAuth.head,ContentAuth.school,ContentAuth.grade,AuthClassify.name.label("identity")).join(AuthClassify, ContentAuth.identity == AuthClassify.id).filter(text("content_auth.id = :uid")).params(uid = uid).all()
        json_res = change_to_json(clu)
        self.write(json_res)

    @tornado.gen.coroutine
    def post(self, *args, **kwargs):
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

        print 'sns_uid\t%s\tsun_nickname\t%s\tsns_head\t%s\tdevice_token\t%s\temail\t%s\tpassword\t%s'%(sns_uid, sns_nickname, sns_head, device_token, email, password)


        check_result = Session.query(ContentAuth.id).filter(ContentAuth.sns_uid == sns_uid).all()
        print 5555555555555

        return_uid = -1
        if len(check_result) == 0:
            content_auth_imp = ContentAuth(email = email, password = password, username = sns_nickname, last_login = last_login, date_joined = date_joined, head = sns_head, nickname = sns_nickname, regist_from = 1, sns_type = sns_type, sns_uid = sns_uid)
            Session.add(content_auth_imp)
            try:
                Session.flush()
                Session.commit()
            except Exception, e:
                Session.rollback()
                print e

            finally:
                Session.close()
            return_uid = content_auth_imp.id
        else:
            return_uid = check_result[0].id
            Session.query(ContentAuth).filter(ContentAuth.id == return_uid).update({ContentAuth.last_login: last_login})
            try:
                Session.flush()
                Session.commit()
            except Exception, e:
                Session.rollback()
                print e
            finally:
                Session.close()

        #regist device token
        if device_token  is not None:
            dt = time.strftime('%Y-%m-%d %H:%M:%S')
            def datetime_timestamp(dt):
                time.strptime(dt, '%Y-%m-%d %H:%M:%S')
                s = time.mktime(time.strptime(dt, '%Y-%m-%d %H:%M:%S'))
                return int(s)
            d = datetime_timestamp(dt)
            app_dev_clu = Session.query(AppDevicetoken).filter(and_(AppDevicetoken.author_id == return_uid, AppDevicetoken.device_token == device_token)).all()
            if len(app_dev_clu) == 0:
                Session.add(AppDevicetoken(author_id = return_uid, device_token = device_token, update_dateline = d))
                try:
                    Session.flush()
                    Session.commit()
                except Exception, e:
                    Session.rollback()
                    print e
                finally:
                    Session.close()
            else:
                Session.query(AppDevicetoken).filter(and_(AppDevicetoken.author_id == return_uid, AppDevicetoken.device_token == device_token)).update({AppDevicetoken.update_dateline: d})
                try:
                    Session.flush()
                    Session.commit()
                except Exception, e:
                    Session.rollback()
                    print e
                finally:
                    Session.close()
        clu = {'uid':return_uid}
        clu_json = change_to_json_2(clu)
        self.write(clu_json)



class UpdateToken(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/update/token"
    @tornado.gen.coroutine
    def post(self, *args, **kwargs):
        print self.request
        uid = self.param('user_uid')
        device_token = self.param("device_token")

        dt = time.strftime('%Y-%m-%d %H:%M:%S')
        def datetime_timestamp(dt):
            time.strptime(dt, '%Y-%m-%d %H:%M:%S')
            s = time.mktime(time.strptime(dt, '%Y-%m-%d %H:%M:%S'))
            return int(s)
        d = datetime_timestamp(dt)

        print 'uid', uid
        print 'devoce', device_token


        clu = Session.query(AppDevicetoken.id).filter(and_(AppDevicetoken.author_id == uid)).order_by(AppDevicetoken.id.desc()).limit(1).all()
        if clu:
            device_id = clu[0].id
            print 'device_id',device_id
            Session.query(AppDevicetoken).filter(AppDevicetoken.id == device_id).update({AppDevicetoken.update_dateline: d, AppDevicetoken.device_token:device_token})
            try:
                Session.flush()
                Session.commit()
            except Exception, e:
                Session.rollback()
                print e
            finally:
                Session.close()
        else:
            pass
        self.write('token_updated')




    



class UserClassify(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/user/classify"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        print self.request
        clu = Session.query(AuthClassify).order_by(AuthClassify.id)
        json_res = change_to_json(clu)
        self.write(json_res)


class MenuInfo(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/menu/info"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        print self.request
        t_di = {}
        uid = self.param("uid")
        clu = Session.query(AppMessage.id).filter(and_(AppMessage.is_read == "0", AppMessage.message_to == uid))
        json_res = change_to_json(clu)
        clu = json.loads(json_res)
        t_di["unread_messages"] = clu

        clu = Session.query(ContentBlog.id).filter(ContentBlog.praise_count > "2")
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
        print self.request
        json_res = get_info(self.request, args, kwargs)
        self.write(json_res)



class BlogHot(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/blog/hot"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        print self.request
        json_res = get_info(self.request, args, kwargs)
        self.write(json_res)


class BlogIndex(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/blog/index"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        print self.request
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
        print self.request

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
        print self.request
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
        print self.request
        func_type = self.param('type')
        uid = self.param('uid')
        blog_id = self.param('blog_id')

        if func_type == 'remove':
            Session.query(AppBlogPraise).filter(and_(AppBlogPraise.author_id == uid, AppBlogPraise.blog_id == blog_id)).delete()
            Session.query(ContentBlog).filter(ContentBlog.id == blog_id).update({ContentBlog.praise_count : ContentBlog.praise_count - 1})
            try:
                Session.flush()
                Session.commit()
            except Exception, e:
                Session.rollback()
                print e

            finally:
                Session.close()
            clu = {'resutl':1, 'error':'/blog/praise remove success'}
        elif func_type == 'add':
            Session.add(AppBlogPraise(author_id = uid, blog_id = blog_id))
            Session.query(ContentBlog).filter(ContentBlog.id == blog_id).update({ContentBlog.praise_count : ContentBlog.praise_count + 1})
            try:
                Session.flush()
                Session.commit()
            except Exception, e:
                Session.rollback()
                print e
            finally:
                Session.close()
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
        if func_type == 'remove':
            Session.query(AppFavorate).filter(and_(AppFavorate.author_id == uid, AppFavorate.blog_id == blog_id)).delete()
            try:
                Session.flush()
                Session.commit()
            except Exception, e:
                Session.rollback()
                print e
            finally:
                Session.close()
            clu = {'resutl':1, 'error':'/blog/favorate remove success'}
        elif func_type == 'add':

            if_exit_clu = Session.query(AppFavorate).filter(and_(AppFavorate.author_id == uid, AppFavorate.blog_id == blog_id)).all()
            if len(if_exit_clu) == 0:
                Session.add(AppFavorate(author_id = uid, blog_id = blog_id))

                try:
                    Session.flush()
                    Session.commit()
                except Exception, e:
                    Session.rollback()
                    print e
                finally:
                    Session.close()

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
        print self.request
        json_res = get_info(self.request, args, kwargs)
        self.write(json_res)


class TagBlog(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/tag/(\d*)"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        print self.request
        blog_id = args[0]
        clu = Session.query(ContentTag.id.label('id'), ContentTag.name.label('name')).join(ContentBlogTagmany, ContentTag.id == ContentBlogTagmany.tag_id).filter(ContentBlogTagmany.blog_id == blog_id).all()
        json_res = change_to_json_1(clu)
        self.write(json_res)






class BlogTag(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/blog/tag/(\d*)"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        print self.request
        tag_id = args[0]
        clu = Session.query(ContentBlog.id, ContentBlog.title, func.replace(ContentBlog.cover,'covers', '%s/covers'%self.image_base_url).label("cover"), func.replace(ContentBlog.thumb, 'thumb/', '%s/thumb/'%self.image_base_url).label("thumb"),ContentBlog.date,ContentBlog.abstract,ContentBlog.category_id, ContentCategory.name.label("category_name"), ContentBlog.tag_id, ContentTag.name.label("tag_name"), ContentBlog.is_out, ContentBlog.is_big, ContentBlog.index_pic, ContentBlog.source, ContentBlog.source_url).join(ContentCategory, ContentBlog.category_id == ContentCategory.id).join(ContentTag, ContentBlog.tag_id == ContentTag.id).filter(text("content_blog.tag_id = :tag_id")).params(tag_id =  tag_id).all()
        json_res = change_to_json_1(clu)
        self.write(json_res)


class BlogID(OrigionHandler):#problem
    @classmethod
    def url_pattern(cls):
        return r"/blog/(\d{1,})"
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):#need
        print self.request
        print os.path.dirname(__file__)
        print os.path.join(os.path.dirname(__file__), "templates")
        json_res = get_info(self.request, args, kwargs)
        self.write(json_res)



class CommentHot(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/comment/hot/(\d*)"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        print self.request
        blog_id = args[0]
        clu = Session.query(ContentBlogComment.id,  ContentComment.content, ContentComment.author_id, ContentComment.aauthor, ContentComment.time).join(ContentComment, ContentBlogComment.comment_id == ContentComment.id).filter(text("content_blog_comment.blog_id = :blog_id")).params(blog_id =  blog_id).all()
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
        comments = Session.query(ContentBlogComment.comment_id,  ContentComment.content, ContentComment.author_id, ContentAuth.nickname, ContentComment.praise_count, ContentComment.time, func.replace(ContentAuth.head, 'covers/', '%s/covers'%self.image_base_url).label('head')).join(ContentComment, ContentBlogComment.comment_id == ContentComment.id).join(ContentAuth, ContentComment.author_id == ContentAuth.id).filter(text("content_blog_comment.blog_id = :blog_id and content_comment.visible = 1")).params(blog_id =  blog_id).order_by(ContentComment.id.desc()).offset(p[0]).limit(p[1]).all()
        json_res = change_to_json_1(comments)
        if uid is not None:
            comments = json.loads(json_res)
            for index in xrange(len(comments)):
                comment_id = comments[index]['comment_id']
                comment_praise = Session.query(AppCommentPraise.id).filter(and_(AppCommentPraise.comment_id ==  comment_id, AppCommentPraise.author_id == uid)).all()
                if len(comment_praise) == 0:
                    comments[index]['praise_state'] = 0 
                else:
                    comments[index]['praise_state'] = 1 
            json_res = change_to_json_2(comments)
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
        Session.add(content_comment_imp)
        try:
            Session.flush()
            Session.commit()
        except Exception, e:
            Session.rollback()
            print e
        finally:
            Session.close()
        comment_id = content_comment_imp.id
        Session.add(ContentBlogComment(blog_id =blog_id , comment_id = comment_id))
        try:
            Session.flush()
            Session.commit()
        except Exception, e:
            Session.rollback()
            print e
        finally:
            Session.close()
        res = {'result':"1", "error":"/comment add success"}
        res_json = json.dumps(res)
        self.write(res_json)



class CommentPraiseCommentID(OrigionHandler):#problem
    @classmethod
    def url_pattern(cls):
        return r"/comment/praise/(\d*)"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        print self.request
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
        Session.query(AppMessage).filter(AppMessage.id == message_id).update({AppMessage.is_read:1})
        try:
            Session.flush()
            Session.commit()
        except Exception, e:
            Session.rollback()
            print e

        finally:
            Session.close()
        self.write(json_res)


    @tornado.gen.coroutine
    def post(self, *args, **kwargs):
        print self.request
        print 222



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

        if praise_type == 'add':
            Session.add(AppCommentPraise(author_id = uid, comment_id = comment_id))
            Session.query(ContentComment).filter(ContentComment.id ==  comment_id).update({ContentComment.praise_count : ContentComment.praise_count + 1})
            try:
                Session.flush()
                Session.commit()
            except Exception, e:
                Session.rollback()
            finally:
                Session.close()
            old_comment = Session.query(ContentComment.author_id, ContentComment.content, ContentComment.praise_count).filter(ContentComment.id == comment_id)
            to_uid = old_comment[0].author_id
            content = old_comment[0].content
            praise_count = old_comment[0].praise_count
            abstr_content = content[:100]
            if praise_count > 1:
                subject = "%s 等 %s 人赞了您的评论：%s"%(nickname, praise_count, abstr_content)
            else:
                subject = '%s赞了您的评论： %s'%(nickname, abstr_content)
            Session.merge(AppMessage(message_from = uid, message_to = to_uid, subject = subject, date = current_time, message_type = 2, blog_id = blog_id, comment_id = comment_id)) 

            try:
                Session.flush()
                Session.commit()
            except Exception, e:
                Session.rollback()
                print e
            finally:
                Session.close()

            push_message_to_uid(to_uid, subject)
            clu = {'resutl':1, 'error':'/comment/praise add success'}

        elif praise_type == 'remove':
            Session.query(AppCommentPraise).filter(and_(AppCommentPraise.author_id == uid, AppCommentPraise.comment_id == comment_id)).deletee()
            Session.query(ContentComment).filter(ContentComment.id ==  comment_id).update({ContentComment.praise_count : ContentComment.praise_count - 1})
            try:
                Session.flush()
                Session.commit()
            except Exception, e:
                Session.rollback()
                print e
            finally:
                Session.close()
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
        print self.request
        json_res = get_info(self.request, args, kwargs)
        message_id = self.param('message_id')
        Session.query(AppMessage).filter(AppMessage.id == message_id).update({AppMessage.is_read: 1})
        try:
            Session.flush()
            Session.commit()
        except:
            Session.rollback()
        finally:
            Session.close()
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
        Session.add(content_comment_imp)
        try:
            Session.flush()
            Session.commit()
        except Exception, e:
            Session.rollback()
            print e
        finally: 
            Session.close()
        reply_comment_id = content_comment_imp.id
        Session.add(ContentBlogComment(blog_id =blog_id , comment_id = reply_comment_id))
        old_comment = Session.query(ContentComment.author_id, ContentComment.content).filter(ContentComment.id ==  comment_id).all()
        Session.add(AppCommentReply(comment_id = comment_id, reply_id = reply_comment_id))

        try:
            Session.flush()
            Session.commit()
        except Exception, e:
            Session.rollback()
            print e
        finally: 
            Session.close()
        to_uid = old_comment[0].author_id
        content = old_comment[0].content
        abstract_content = content[:100]
        subject = '%s等人回复了您的评论：%s'%(nickname, abstract_content)
        push_message_to_uid(to_uid, subject)
        Session.merge(AppMessage(message_from = uid, message_to = to_uid, subject = subject, date = current_time, message_type = 1, blog_id = blog_id, comment_id = comment_id)) 
        try:
            Session.flush()
            Session.commit()
        except Exception, e:
            Session.rollback()
            print e
        finally: 
            Session.close()
        json_res = json.dumps({"result":1, "error":"/comment/reply success"})#problem
        self.write(json_res)



class CommentReport(OrigionHandler):#problem
    @tornado.gen.coroutine
    def post(self, *args, **kwargs):
        uid = self.param('uid')
        comment_id = self.param('comment_id')
        Session.query(ContentComment).filter(ContentComment.id == comment_id).update({ContentComment.report_count: ContentComment.report_count + 1})
        try:
            Session.flush()
            Session.commit()
        except Exception, e:
            Session.rollback()
            print e
        finally: 
            Session.close()
        json_res = json.dumps({"result":1, "error":"/comment/report success"})#problem
        self.write(json_res)



class Message(OrigionHandler):#message
    @classmethod
    def url_pattern(cls):
        return r"/message/(\d*)"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        print self.request
        json_res = get_info(self.request, args, kwargs)
        self.write(json_res)


class MessageAllreadyRead(OrigionHandler):#message
    @classmethod
    def url_pattern(cls):
        return r"/message/allreadyread/(\d*)"
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        print self.request
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
        if uid is None:
            pass
        else:
            clu = Session.query(AppDevicetoken.enable_push).filter(text("app_devicetoken.author_id = :uid")).params(uid = uid).all()
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
        print blog_id
        def push_message_to_all_users(subject):
            clu = Session.query(AppDevicetoken.device_token).all()
            #clu = Session.query(AppDevicetoken.device_token).filter(AppDevicetoken.author_id == to_uid).order_by(AppDevicetoken.id.desc()).limit(1).all()
            if len(clu) == 0:
                pass
            else:
                tokens =  [i.device_token for i in clu]
                print type(tokens)
                token = clu[0].device_token
                mk = os.path.dirname(os.path.abspath("__file__"))
                print mk
              #  ios_dir =  "%s%s"%(mk, "/push/ios_single.py")
              #  cmd = ["python",ios_dir, token, subject] 
              #  subprocess.Popen(cmd)
        push_message_to_all_users(123)
        self.write('5555555')
    






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
        print self.request
        self.write('sleep 6')


    def on_fetch(self, response):
        self.write("sleep 6")
        self.finish()








