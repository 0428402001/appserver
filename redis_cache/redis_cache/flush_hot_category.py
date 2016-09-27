# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import os

cur_dir = os.path.dirname(__file__)
p_dir = os.path.dirname(cur_dir)
g_dir = os.path.dirname(p_dir)
sys.path.append(g_dir)
sys.path.append(p_dir)


cur_dir =  os.path.abspath('.')
p_dir = os.path.dirname(cur_dir)
g_dir = os.path.dirname(p_dir)
sys.path.append(g_dir)
sys.path.append(p_dir)


from redis_con_pool import conn_pool_hot_category




import json
import time
import subprocess

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
from sqlalchemy import event
from sqlalchemy.dialects.mysql import VARCHAR
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm import scoped_session, sessionmaker, object_mapper
from sqlalchemy.types import TypeDecorator
import sqlalchemy

import redis
import logging

from models.base_orm import change_to_json_1



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

conn_hot_category = redis.Redis(connection_pool= conn_pool_hot_category)


import database
if __name__ == "__main__":

    engine = create_engine(database.DB_PATH, echo = False)
    #engine = create_engine(database.DB_PATH, pool_size = 10, pool_recycle=3600, echo = False)
    Session = sessionmaker()
    Session.configure(bind=engine)
    cur_session = Session()


    image_base_url =  'http://o6y4guqxy.bkt.clouddn.com/media'
    clu = cur_session.query(ContentCategory.id.label('category_id'), ContentCategory.name.label('category_name'), func.replace(ContentCategory.cover, 'covers/', '%s/covers/'%image_base_url).label('cover'),ContentCategory.introduction, ContentAuth.nickname.label('dj_name'), func.replace(ContentAuth.head, 'covers', '%s/covers'%image_base_url).label('dj_head'), ContentAuth.sign.label('dj_desc'), ContentCategory.sort).join(ContentAuth, ContentCategory.dj_id ==  ContentAuth.id).order_by(ContentCategory.sort.asc()).all()
    cur_session.close()
    json_res = change_to_json_1(clu)

    record = json.loads(json_res)
    record = record[-4:]
    conn_hot_category.flushdb()
    for blog in record:
        conn_hot_category.lpush('0', blog)

