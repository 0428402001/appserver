# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import json
import os
import time

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



#written_by_liujun
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
        print self.request
        #clu = Session.query(ContentAuth.id.label('newcolumn'), ContentAuth.password.label("pa_t")).filter(ContentAuth.id == "1").all()
        #json_res = change_to_json(clu)
        #self.write(json_res)
        self.write('ting')


class StartupImage(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/startup/image"
    def get(self, *args, **kwargs):
        clu = Session.query(AppInfo.value.label("url")).filter(AppInfo.key == "url_startup_image").all()
        json_res = change_to_json(clu)
        self.write(json_res)


class Config(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/config"
    def get(self, *args, **kwargs):
        clu = Session.query(AppInfo).all()
        json_res = change_to_json(clu)
        self.write(json_res)

class Activity(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/activity"
    def get(self, *args, **kwargs):
        clu = Session.query(ContentActivity).all()
        json_res = change_to_json(clu)
        self.write(json_res)


class Category(OrigionHandler):#problem
    @classmethod
    def url_pattern(cls):
        return r"/category"
    def get(self, *args, **kwargs):
        json_res = get_info(self.request, args, kwargs)
        self.write(json_res)



class CategoryHot(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/category/hot"
    def get(self, *args, **kwargs):
        json_res = get_info(self.request, args, kwargs)
        self.write(json_res)



        



class CategorySubscription(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/category/subscription"
    def get(self, *args, **kwargs):
        uid =  self.param("uid")
        json_res = get_info(self.request, args, kwargs)
        self.write(json_res)

    def post(self, *args, **kwargs):
        func_type = self.param('type')
        uid = self.param('uid')
        category_id = self.param('category_id')

        if func_type == 'remove':
            Session.query(AppSubscription).filter(and_(AppSubscription.author_id == uid, AppSubscription.category_id == category_id)).delete()
            Session.flush()
            try:
                Session.commit()
            except:
                Session.rollback()
            clu = {'resutl':1, 'error':'/category/subscription remove success'}
        elif func_type == 'add':
            Session.add(AppSubscription(author_id = uid, category_id = category_id))
            Session.flush()
            try:
                Session.commit()
            except:
                Session.rollback()
            clu = {'resutl':1, 'error':'/category/subscription add success'}
        else:
            clu = {'resutl':0, 'error':'wrong parameter.'}
        json_res = change_to_json_2(clu)
        self.write(json_res)









class CategorySubscriptionstate(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/category/subscription_state"
    def get(self, *args, **kwargs):
        uid = self.param('uid')
        category_id = self.param('category_id')
        clu = Session.query(AppSubscription).filter(text("app_subscription.author_id = :uid and app_subscription.category_id = :category_id")).params(uid = uid, category_id = category_id).all()
        json_res = change_to_json(clu)
        self.write(json_res)





class UserProfile(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/user/profile"
    def get(self, *args, **kwargs):
        clu = Session.query(ContentAuth.id, ContentAuth.nickname, ContentAuth.sign,ContentAuth.head,ContentAuth.school,ContentAuth.grade,AuthClassify.name.label("identity")).join(AuthClassify, ContentAuth.identity == AuthClassify.id).filter(text("content_auth.id = :uid")).params(uid = uid).all()
        json_res = change_to_json(clu)
        self.write(json_res)

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
        return_uid = -1
        if len(check_result) == 0:
            content_auth_imp = ContentAuth(email = email, password = password, username = sns_nickname, last_login = last_login, date_joined = date_joined, head = sns_head, nickname = sns_nickname, regist_from = 1, sns_type = sns_type, sns_uid = sns_uid)
            Session.add(content_auth_imp)
            Session.flush()
            try:
                Session.commit()
            except:
                Session.rollback()
            return_uid = content_auth_imp.id
        else:
            return_uid = check_result[0].id
            Session.query(ContentAuth).filter(ContentAuth.id == return_uid).update({ContentAuth.last_login: last_login})
            Session.flush()
            try:
                Session.commit()
            except:
                Session.rollback()

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
                Session.flush()
                try:
                    Session.commit()
                except:
                    Session.rollback()
            else:
                Session.query(AppDevicetoken).filter(and_(AppDevicetoken.author_id == return_uid, AppDevicetoken.device_token == device_token)).update({AppDevicetoken.update_dateline: d})
                Session.flush()
                try:
                    Session.commit()
                except:
                    Session.rollback()
        clu = {'uid':return_uid}
        clu_json = change_to_json_2(clu)
        self.write(clu_json)



    



class UserClassify(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/user/classify"
    def get(self, *args, **kwargs):
        clu = Session.query(AuthClassify).order_by(AuthClassify.id)
        json_res = change_to_json(clu)
        self.write(json_res)


class MenuInfo(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/menu/info"
    def get(self, *args, **kwargs):
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
    def get(self, *args, **kwargs):
        json_res = get_info(self.request, args, kwargs)
        self.write(json_res)



class BlogHot(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/blog/hot"
    def get(self, *args, **kwargs):
        json_res = get_info(self.request, args, kwargs)
        self.write(json_res)


class BlogIndex(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/blog/index"
    def get(self, *args, **kwargs):
        json_res = get_info(self.request, args, kwargs)
        self.write(json_res)




class Blog(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/blog"
    def get(self, *args, **kwargs):
        json_res = get_info(self.request, args, kwargs)
        self.write(json_res)


class BlogCategory(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/blog/category/(\d*)"
    def get(self, *args, **kwargs):
        category_id = args[0]
        p = self.get_page_index() 
        uid = self.param("uid")
        clu = Session.query(ContentBlog.id, ContentBlog.title, ContentBlog.author, func.replace(ContentBlog.cover, 'covers', '%s/covers'%self.image_base_url).label('cover'), func.replace(ContentBlog.thumb,'thumb/', '%s/thumb/'%self.image_base_url).label('thumb'), ContentBlog.date, ContentBlog.abstract, ContentBlog.category_id, ContentBlog.is_out, ContentBlog.is_big, ContentBlog.index_pic, ContentBlog.source, ContentBlog.source_url, ContentCategory.name.label("category_name"), ContentTag.name.label("tag_name")).join(ContentCategory, ContentBlog.category_id == ContentCategory.id).join(ContentTag, ContentBlog.category_id == ContentTag.id).filter(ContentBlog.category_id ==  category_id).order_by(ContentBlog.date.desc()).offset(p[0]).limit(p[1]).all()
        json_res = change_to_json(clu)
        self.write(json_res)




class BlogFavorateUID(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/blog/favorate/(\d*)"
    def get(self, *args, **kwargs):
        json_res = get_info(self.request, args, kwargs)
        self.write(json_res)





class BlogPraise(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/blog/praise"


    def post(self, *args, **kwargs):
        func_type = self.param('type')
        uid = self.param('uid')
        blog_id = self.param('blog_id')

        if func_type == 'remove':
            Session.query(AppBlogPraise).filter(and_(AppBlogPraise.author_id == uid, AppBlogPraise.blog_id == blog_id)).delete()
            Session.query(ContentBlog).filter(ContentBlog.id == blog_id).update({ContentBlog.praise_count : ContentBlog.praise_count - 1})
            Session.flush()
            try:
                Session.commit()
            except:
                Session.rollback()
            clu = {'resutl':1, 'error':'/blog/praise remove success'}
        elif func_type == 'add':
            Session.add(AppBlogPraise(author_id = uid, blog_id = blog_id))
            Session.query(ContentBlog).filter(ContentBlog.id == blog_id).update({ContentBlog.praise_count : ContentBlog.praise_count + 1})
            Session.flush()
            try:
                Session.commit()
            except:
                Session.rollback()
            clu = {'resutl':1, 'error':'/blog/praise add success'}
        else:
            clu = {'resutl':0, 'error':'wrong parameter.'}
        json_res = change_to_json_2(clu)
        self.write(json_res)






class BlogFavorate(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/blog/favorate"
    def post(self, *args, **kwargs):
        func_type = self.param('type')
        uid = self.param('uid')
        blog_id = self.param('blog_id')
        if func_type == 'remove':
            Session.query(AppFavorate).filter(and_(AppFavorate.author_id == uid, AppFavorate.blog_id == blog_id)).delete()
            Session.flush()
            try:
                Session.commit()
            except:
                Session.rollback()
            clu = {'resutl':1, 'error':'/blog/favorate remove success'}
        elif func_type == 'add':
            Session.add(AppFavorate(author_id = uid, blog_id = blog_id))
            Session.flush()
            try:
                Session.commit()
            except:
                Session.rollback()
            clu = {'resutl':1, 'error':'/blog/favorate add success'}
        else:
            clu = {'resutl':0, 'error':'wrong parameter.'}
        json_res = change_to_json_2(clu)
        self.write(json_res)


class BlogQuery(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/blog/query/(.*)"
    def get(self, *args, **kwargs):
        json_res = get_info(self.request, args, kwargs)
        self.write(json_res)


class TagBlog(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/tag/(\d*)"
    def get(self, *args, **kwargs):
        blog_id = args[0]
        clu = Session.query(ContentTag.id.label('id'), ContentTag.name.label('name')).join(ContentBlogTagmany, ContentTag.id == ContentBlogTagmany.tag_id).filter(ContentBlogTagmany.blog_id == blog_id).all()
        json_res = change_to_json_1(clu)
        self.write(json_res)






class BlogTag(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/blog/tag/(\d*)"
    def get(self, *args, **kwargs):
        tag_id = args[0]
        clu = Session.query(ContentBlog.id, ContentBlog.title, func.replace(ContentBlog.cover,'covers', '%s/covers'%self.image_base_url).label("cover"), func.replace(ContentBlog.thumb, 'thumb/', '%s/thumb/'%self.image_base_url).label("thumb"),ContentBlog.date,ContentBlog.abstract,ContentBlog.category_id, ContentCategory.name.label("category_name"), ContentBlog.tag_id, ContentTag.name.label("tag_name"), ContentBlog.is_out, ContentBlog.is_big, ContentBlog.index_pic, ContentBlog.source, ContentBlog.source_url).join(ContentCategory, ContentBlog.category_id == ContentCategory.id).join(ContentTag, ContentBlog.tag_id == ContentTag.id).filter(text("content_blog.tag_id = :tag_id")).params(tag_id =  tag_id).all()
        json_res = change_to_json(clu)
        self.write(json_res)


class BlogID(OrigionHandler):#problem
    @classmethod
    def url_pattern(cls):
        return r"/blog/(\d{1,})"
    def get(self, *args, **kwargs):#need
        print self.request.uri
        blog_id = args[0]
        uid = self.param('uid')
        blog_praise = []
        blog_favorate = []
        if uid is not None:
            blog_praise = Session.query(AppBlogPraise.id.label("pid")).filter(and_(AppBlogPraise.blog_id == blog_id, AppBlogPraise.author_id == uid)).all()
            blog_favorate = Session.query(AppFavorate.id.label("fid")).filter(and_(AppFavorate.blog_id == blog_id, AppFavorate.author_id == uid)).all()
        comment_cnt_clu = Session.query(func.count(ContentBlogComment.comment_id).label("comment_count")).join(ContentComment, ContentBlogComment.comment_id == ContentComment.id).filter(ContentBlogComment.blog_id == blog_id).all()
        comment_cnt = comment_cnt_clu[0][0]

        if len(blog_praise) == 0: 
            is_praise = 0
        else:
            is_praise = 1
        if len(blog_favorate) == 0:
            is_favorate = 0
        else:
            is_favorate = 1
        blog = Session.query(ContentBlog.id, ContentBlog.title, ContentBlog.author, func.replace(ContentBlog.cover, 'covers', '%s/covers'%self.image_base_url).label('cover'), func.replace(ContentBlog.thumb, 'thumb/', '%s/thumb/'%self.image_base_url).label('thumb'), ContentBlog.date, ContentBlog.category_id, ContentBlog.content, ContentBlog.abstract).filter(ContentBlog.id == blog_id).all()
        blog_json = change_to_json(blog)
        blog = json.loads(blog_json)
        blog['comment_count'] = comment_cnt
        blog['is_praise'] = is_praise
        blog['is_favorate'] = is_favorate

        related_blog_clu = Session.query(ContentBlog.id, ContentBlog.title, func.replace(ContentBlog.cover, 'covers','%s/covers'%self.image_base_url).label("cover"), func.replace(ContentBlog.thumb, 'thumb/', '%s/thumb/'%self.image_base_url).label("thumb"),ContentBlog.date,ContentBlog.abstract,ContentBlog.category_id, ContentCategory.name.label("category_name"), ContentBlog.tag_id, ContentTag.name.label("tag_name"), ContentBlog.is_out, ContentBlog.is_big, ContentBlog.index_pic, ContentBlog.source, ContentBlog.source_url).join(ContentCategory, ContentBlog.category_id == ContentCategory.id).join(ContentTag, ContentBlog.tag_id == ContentTag.id).filter(text("content_blog.tag_id in (select tag_id from content_blog where id = :blog_id)")).params(blog_id =  blog_id).all()
        related_blog_json = change_to_json_1(related_blog_clu)
        related_blog = json.loads(related_blog_json)

        hot_comment_clu = Session.query(ContentBlogComment.comment_id,  ContentComment.content, ContentComment.author_id, ContentAuth.nickname, ContentComment.praise_count, ContentComment.time).join(ContentComment, ContentBlogComment.comment_id == ContentComment.id).join(ContentAuth, ContentComment.author_id == ContentAuth.id).filter(text("content_comment.visible = 1")).all()
        hot_comment_json = change_to_json_1(hot_comment_clu)
        hot_comment = json.loads(hot_comment_json)


        clu = {'blog':blog, 'related_blog':related_blog, 'hot_comment':hot_comment}
        json_res = change_to_json_2(clu)
        self.write(json_res)




class CommentHot(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/comment/hot/(\d*)"
    def get(self, *args, **kwargs):
        blog_id = args[0]
        clu = Session.query(ContentBlogComment.id,  ContentComment.content, ContentComment.author_id, ContentComment.aauthor, ContentComment.time).join(ContentComment, ContentBlogComment.comment_id == ContentComment.id).filter(text("content_blog_comment.blog_id = :blog_id")).params(blog_id =  blog_id).all()
        json_res = change_to_json(clu)
        self.write(json_res)



class CommentBlog(OrigionHandler):#problem
    @classmethod
    def url_pattern(cls):
        return r"/comment/(\d*)"
    def get(self, *args, **kwargs):
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

    def post(self, *args, **kwargs):
        blog_id = self.param('blog_id')
        content = self.param('content')
        uid = self.param('uid')
        ip = self.request.remote_ip 
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')
        content_comment_imp = ContentComment(content =content , author_id =uid , aauthor =ip , time = current_time)
        Session.add(content_comment_imp)
        Session.flush()
        try:
            Session.commit()
        except:
            Session.rollback()
        comment_id = content_comment_imp.id
        Session.add(ContentBlogComment(blog_id =blog_id , comment_id = comment_id))
        Session.flush()
        try:
            Session.commit()
        except:
            Session.rollback()
        res = {'result':"1", "error":"/comment add success"}
        res_json = json.dumps(res)
        self.write(res_json)



class CommentPraiseCommentID(OrigionHandler):#problem
    @classmethod
    def url_pattern(cls):
        return r"/comment/praise/(\d*)"
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
        #Session.query(AppMessage).filter(AppMessage.id == message_id).update({AppMessage.is_read:1})
        #Session.flush()
        try:
            Session.commit()
        except:
            Session.rollback()
        self.write(json_res)


    def post(self, *args, **kwargs):
        print 222



class CommentPraise(OrigionHandler):#problem
    @classmethod
    def url_pattern(cls):
        return r"/comment/praise"
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
            Session.flush()
            try:
                Session.commit()
            except:
                Session.rollback()
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

            Session.flush()
            try:
                Session.commit()
            except:
                Session.rollback()

            #push_message_to_uid
            clu = {'resutl':1, 'error':'/comment/praise add success'}

        elif praise_type == 'remove':
            Session.query(AppCommentPraise).filter(and_(AppCommentPraise.author_id == uid, AppCommentPraise.comment_id == comment_id)).deletee()
            Session.query(ContentComment).filter(ContentComment.id ==  comment_id).update({ContentComment.praise_count : ContentComment.praise_count - 1})
            Session.flush()
            Session.commit()
            Session.rollback()
            clu = {'resutl':1, 'error':'/comment/praise remove success'}
        else:
            clu = {'resutl':0, 'error':'wrong parameter.'}
        json_res = change_to_json_2(clu)
        self.write(json_res)


class CommentReplyComment_id(OrigionHandler):#problem
    @classmethod
    def url_pattern(cls):
        return r"/comment/reply/(\d*)"
    def get(self, *args, **kwargs):
        json_res = get_info(self.request, args, kwargs)
        message_id = self.param('message_id')
        #Session.query(AppMessage).filter(AppMessage.id == message_id).update({AppMessage.is_read: 1})
       # try:
       #     Session.flush()
       #     Session.commit()
       # except:
       #     Session.rollback()
        self.write(json_res)


class CommentReply(OrigionHandler):#problem
    @classmethod
    def url_pattern(cls):
        return r"/comment/reply"
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
        except:
            Session.rollback()
        reply_comment_id = content_comment_imp.id
        Session.add(ContentBlogComment(blog_id =blog_id , comment_id = reply_comment_id))
        old_comment = Session.query(ContentComment.author_id, ContentComment.content).filter(ContentComment.id ==  comment_id).all()
        Session.add(AppCommentReply(comment_id = comment_id, reply_id = reply_comment_id))

        try:
            Session.commit()
            Session.commit()
        except:
            Session.rollback()
        to_uid = old_comment[0].author_id
        content = old_comment[0].content
        abstract_content = content[:100]
        subject = '%s等人回复了您的评论：%s'%(nickname, abstract_content)
        #push_message_to_uid(to_uid, subject)
        Session.merge(AppMessage(message_from = uid, message_to = to_uid, subject = subject, date = current_time, message_type = 1, blog_id = blog_id, comment_id = comment_id)) 
        try:
            Session.flush()
            Session.commit()
        except:
            Session.rollback()
        json_res = json.dumps({"result":1, "error":"/comment/reply success"})#problem
        self.write(json_res)



class CommentReport(OrigionHandler):#problem
    def post(self, *args, **kwargs):
        uid = self.param('uid')
        comment_id = self.param('comment_id')
        Session.query(ContentComment).filter(ContentComment.id == comment_id).update({ContentComment.report_count: ContentComment.report_count + 1})
        try:
            Session.commit()
        except:
            Session.rollback()
        json_res = json.dumps({"result":1, "error":"/comment/report success"})#problem
        self.write(json_res)



class Message(OrigionHandler):#message
    @classmethod
    def url_pattern(cls):
        return r"/message/(\d*)"
    def get(self, *args, **kwargs):
        json_res = get_info(self.request, args, kwargs)
        self.write(json_res)



class Blogview(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/blogview/(\d*)"
    def get(self, *args, **kwargs):
        blog_id = args[0]
        clu = Session.query(ContentBlog).filter(ContentBlog.id == blog_id).all()
        if len(clu) == 0:
            self.write('没有对应的文章')
        else:
            clu_res = change_to_json(clu)
            clu = json.loads(clu_res)
            self.render('blog.html', id = clu["id"], title = clu['title'], content = clu['content'], cover = clu['cover'], blog = '2016-5-40', author = clu['author'], date = clu['date'], time = clu['date'])



class Setting(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/setting"
    def get(self, *args, **kwargs):
        uid = self.param('uid') 
        if uid is None:
            pass
        else:
            clu = Session.query(AppDevicetoken.enable_push).filter(text("app_devicetoken.author_id = :uid")).params(uid = uid).all()
            json_res = change_to_json(clu)
            self.write(json_res)





class Test1(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/test1"
    def get(self, *args, **kwargs):
        self.write(22220)
       # clu = Session.query(ContentBlog).filter(ContentBlog.id == 712).all()
       # clu_res = change_to_json(clu)
       # clu = json.loads(clu_res)
       # self.render('blog.html', id = clu["id"], title = clu['title'], content = clu['content'], cover = clu['cover'], blog = '2016-5-40', author = clu['author'], date = clu['date'], time = clu['date'])




class Test2(OrigionHandler):
    @classmethod
    def url_pattern(cls):
        return r"/test2"
    def get(self, *args, **kwargs):
        clu = Session.query(ContentAuth).all()
        json_res = change_to_json(clu)
        self.write(json_res)


