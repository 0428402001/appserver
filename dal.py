# coding=utf-8
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

class URL(object):
    def _image_base_url():
        return 'http://o6y4guqxy.bkt.clouddn.com/media'
        #return 'http://app.collegedaily.cn/media'
    image_base_url = _image_base_url()




def _get_hot_blog(p):
    clu = Session.query(ContentBlog.id, ContentBlog.title, ContentBlog.author, func.replace(ContentBlog.cover,'covers', '%s/covers'%URL.image_base_url).label('cover'), func.replace(ContentBlog.thumb, 'thumb/', '%s/thumb/'%URL.image_base_url).label('thumb'), ContentBlog.date, ContentBlog.abstract, ContentBlog.category_id, ContentBlog.is_out, ContentBlog.is_big, ContentBlog.index_pic, ContentBlog.source, ContentBlog.source_url, ContentCategory.name.label("category_name"), ContentTag.name.label("tag_name") ).join(ContentCategory, ContentBlog.category_id == ContentCategory.id).join(ContentTag, ContentBlog.category_id == ContentTag.id).join(ContentHotblog, ContentHotblog.blog_id == ContentBlog.id).order_by(ContentBlog.date.desc()).offset(p[0]).limit(p[1]).all()
    json_res = change_to_json(clu)
    return json_res 

def _get_query_hot():
    clu = Session.query(ContentHotquery)
    json_res = change_to_json_1(clu)
    return json_res 

def _get_category_hot():
    clu = Session.query(ContentHotcate.cate_id.label('category_id'), ContentCategory.name.label('category_name'), func.replace(ContentCategory.cover, 'covers/', '%s/covers/'%URL.image_base_url).label('cover'),ContentCategory.introduction, ContentAuth.nickname.label('dj_name'), func.replace(ContentAuth.head, 'covers', '%s/covers'%URL.image_base_url).label('dj_head'), ContentAuth.sign.label('dj_desc')).join(ContentCategory, ContentHotcate.cate_id == ContentCategory.id).join(ContentAuth, ContentCategory.dj_id == ContentAuth.id).all()
    json_res = change_to_json_1(clu)
    return json_res 

def _get_category():
    clu = Session.query(ContentCategory.id.label('category_id'), ContentCategory.name.label('category_name'), func.replace(ContentCategory.cover, 'covers/', '%s/covers/'%URL.image_base_url).label('cover'),ContentCategory.introduction, ContentAuth.nickname.label('dj_name'), func.replace(ContentAuth.head, 'covers', '%s/covers'%URL.image_base_url).label('dj_head'), ContentAuth.sign.label('dj_desc')).join(ContentAuth, ContentCategory.dj_id == ContentAuth.id).all()
    json_res = change_to_json_1(clu)
    return json_res 



def _get_app_subscription(uid, cat_set):
    sub_clu = Session.query(func.count(AppSubscription.id).label('sub_count'), AppSubscription.category_id).filter(and_(AppSubscription.author_id == uid ,AppSubscription.category_id.in_(cat_set))).group_by(AppSubscription.category_id).all()
    json_res = change_to_json_1(sub_clu)
    return json_res 



def _get_blog(p):
    clu = Session.query(ContentBlog.id, ContentBlog.title, ContentBlog.author, func.replace(ContentBlog.cover,'covers', '%s/covers'%URL.image_base_url).label('cover'), func.replace(ContentBlog.thumb, 'thumb/', '%s/thumb/'%URL.image_base_url).label('thumb'), ContentBlog.date, ContentBlog.abstract, ContentBlog.category_id, ContentBlog.is_out, ContentBlog.is_big, ContentBlog.index_pic, ContentBlog.source, ContentBlog.source_url, ContentCategory.name.label("category_name"), ContentTag.name.label("tag_name") ).join(ContentCategory, ContentBlog.category_id == ContentCategory.id).join(ContentTag, ContentBlog.category_id == ContentTag.id).order_by(ContentBlog.date.desc()).offset(p[0]).limit(p[1]).all()
    json_res = change_to_json_1(clu)
    return json_res

def _get_blog_index(p):
    clu = Session.query(ContentBlog.id, ContentBlog.title, ContentBlog.author, func.replace(ContentBlog.cover, 'covers/', '%s/covers/'%URL.image_base_url).label('cover'), func.replace(ContentBlog.thumb, 'thumb/', '%s/thumb/'%URL.image_base_url).label('thumb'), ContentBlog.date, ContentBlog.abstract, ContentBlog.category_id, ContentBlog.is_out, ContentBlog.is_big, ContentBlog.index_pic, ContentBlog.source, ContentBlog.source_url, ContentCategory.name.label("category_name"), ContentTag.name.label("tag_name") ).join(ContentCategory, ContentBlog.category_id == ContentCategory.id).join(ContentTag, ContentBlog.category_id == ContentTag.id).filter(text("content_blog.id in (select blog_id from content_indexblog)")).order_by(ContentBlog.date.desc()).offset(p[0]).limit(p[1]).all()
    json_res = change_to_json_1(clu)
    return json_res


def _get_blog_query(keyword, p):
    clu = Session.query(ContentBlog.id, ContentBlog.title, ContentBlog.author, func.replace(ContentBlog.cover, 'covers/', '%s/covers/'%URL.image_base_url).label('cover'), func.replace(ContentBlog.thumb, 'thumb/', '%s/thumb/'%URL.image_base_url).label('thumb'), ContentBlog.date, ContentBlog.abstract, ContentBlog.category_id, ContentCategory.name.label("category_name"), ContentBlog.tag_id, ContentTag.name.label("tag_name"), ContentBlog.is_out, ContentBlog.is_big, ContentBlog.index_pic, ContentBlog.source, ContentBlog.source_url).join(ContentCategory, ContentBlog.category_id == ContentCategory.id).join(ContentTag, ContentBlog.tag_id == ContentTag.id).filter(ContentBlog.title.like("%%%s%%"%keyword)).order_by(ContentBlog.date.desc()).offset(p[0]).limit(p[1]).all()
    json_res = change_to_json_1(clu)
    return json_res



def _get_blog_favorate_uid(uid, p):
    clu = Session.query(AppFavorate.id, ContentBlog.id, ContentBlog.title, func.replace(ContentBlog.cover, 'covers', '%s/covers'%URL.image_base_url).label('cover'), func.replace(ContentBlog.thumb, 'thumb/', '%s/thumb/'%URL.image_base_url).label('thumb'), ContentBlog.abstract, ContentBlog.author).join(ContentBlog, AppFavorate.blog_id == ContentBlog.id).filter("app_favorate.author_id = :uid").params(uid = uid).order_by(AppFavorate.id).offset(p[0]).limit(p[1]).all()
    json_res = change_to_json_1(clu)
    return json_res



def _get_app_subscri_uid(uid):
    clu = Session.query(ContentCategory.id.label('category_id'), ContentCategory.name.label('category_name'), func.replace(ContentCategory.cover, 'covers/', '%s/covers/'%URL.image_base_url).label('cover'),ContentCategory.introduction, ContentAuth.nickname.label('dj_name'), func.replace(ContentAuth.head, 'covers', '%s/covers'%URL.image_base_url).label('dj_head'), ContentAuth.sign.label('dj_desc')).join(ContentAuth, ContentCategory.dj_id == ContentAuth.id).join(AppSubscription, AppSubscription.category_id ==ContentCategory.id ).filter(AppSubscription.author_id == uid).all()
    json_res = change_to_json_1(clu)
    return json_res

def _get_main_comment(comment_id):
    main_content = Session.query(ContentComment.id.label('comment_id'), ContentComment.author_id, ContentComment.content, ContentComment.time, ContentAuth.nickname, func.replace(ContentAuth.head, 'covers/', '%s/covers/'%URL.image_base_url).label('head'), ContentComment.praise_count).join(ContentAuth, ContentComment.author_id == ContentAuth.id).filter(ContentComment.id == comment_id)
    main_content_json = change_to_json(main_content)
    return main_content_json

def _get_praise_people(p, comment_id):
    praise_info = Session.query(AppCommentPraise.id, AppCommentPraise.author_id, ContentAuth.nickname, func.replace(ContentAuth.head, 'covers/', '%s/covers/'%URL.image_base_url).label('head')).join(ContentAuth, AppCommentPraise.author_id == ContentAuth.id).filter(AppCommentPraise.comment_id == comment_id).offset(p[0]).limit(p[1]).all()
    res_json = change_to_json_1(praise_info)
    return res_json

def _get_comment_reply(p, comment_id):
    reply_content = Session.query(AppCommentReply.reply_id.label("comment_id") ,ContentComment.author_id, ContentComment.content, ContentComment.time, ContentAuth.nickname, ContentAuth.head).join(ContentComment, AppCommentReply.reply_id == ContentComment.id).join(ContentAuth, ContentComment.author_id == ContentAuth.id).filter(AppCommentReply.comment_id == comment_id).offset(p[0]).limit(p[1]).all()
    reply_content_json = change_to_json_1(reply_content)
    return reply_content_json



def _get_message_from_users(p, uid):
    changed_url = "http://o6y4guqxy.bkt.clouddn.com/media/"
    messages = Session.query(AppMessage.id, AppMessage.message_from, AppMessage.message_to,AppMessage.subject, AppMessage.content, AppMessage.date, AppMessage.message_type, AppMessage.is_read, AppMessage.blog_id, AppMessage.comment_id, func.replace(ContentAuth.head, 'covers/', '%s/covers/'%URL.image_base_url).label("head"), ContentBlog.title.label("blog_title"), ContentBlog.tag_id, ContentBlog.is_out, ContentBlog.source, ContentBlog.source_url, ContentBlog.abstract, func.replace(ContentBlog.cover, 'covers/', '%s/covers/'%changed_url).label('cover'), ContentComment.content.label('commit_content')).join(ContentAuth,  AppMessage.message_from == ContentAuth.id).join( ContentBlog, AppMessage.blog_id == ContentBlog.id).join(ContentComment, AppMessage.comment_id == ContentComment.id).filter(and_(AppMessage.message_to == uid, AppMessage.is_read == 0)).order_by(AppMessage.id.desc()).all()
    messages_json = change_to_json_1(messages)
    return messages_json


def _get_message_from_offical():
    messages1 = Session.query(AppMessage).filter(AppMessage.message_from == 1).all()
    messages1_json = change_to_json(messages1)
    return messages1_json
