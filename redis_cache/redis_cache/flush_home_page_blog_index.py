# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import json
import os
import urllib2


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



from redis_con_pool import conn_pool_home_page_blog_index 

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





conn_home_page_blog_index = redis.Redis(connection_pool= conn_pool_home_page_blog_index)
def flush_blog_cache(blog_id, blog):
    for key in blog.keys():
        conn_home_page_blog_index.hset(blog_id, key, blog[key])


if __name__ == "__main__":
    image_base_url =  'http://o6y4guqxy.bkt.clouddn.com/media'

    import database
    engine = create_engine(database.DB_PATH)
    #engine = create_engine(database.DB_PATH, pool_size = 10, pool_recycle=3600, echo = False)
    Session = sessionmaker()
    Session.configure(bind=engine)
    cur_session = Session()


    c_time = time.strftime('%Y-%m-%d %H:%M:%S')

    clu = cur_session.query(ContentBlog.id, ContentBlog.title, ContentBlog.author, func.replace(ContentBlog.cover, 'covers/', '%s/covers/'%image_base_url).label('cover'), func.replace(ContentBlog.thumb, 'thumb/', '%s/thumb/'%image_base_url).label('thumb'), ContentBlog.date, ContentBlog.abstract, ContentBlog.category_id, ContentBlog.is_out, ContentBlog.is_big, ContentBlog.index_pic, ContentBlog.source, ContentBlog.source_url, ContentCategory.name.label("category_name") ).join(ContentCategory, ContentBlog.category_id == ContentCategory.id).join(ContentTag, ContentBlog.tag_id == ContentTag.id).filter(text("content_blog.hotness = 0 and content_blog.id in (select blog_id from content_indexblog)")).order_by(ContentBlog.id.asc()).all()
    cur_session.close()
    json_res = change_to_json_1(clu)
    clu_dict = json.loads(json_res)

    for i in clu_dict:
        tt = i['cover']
        try:
            tt = tt.encode('utf-8')
        except Exception, e:
            print e
        i['cover'] =urllib2.quote(tt, safe =":;/?@&=+$,") 


    conn_home_page_blog_index.flushdb()
    for blog in clu_dict:
        conn_home_page_blog_index.lpush('0', blog)

    print "home_page_blog_index_flushed", time.ctime()
