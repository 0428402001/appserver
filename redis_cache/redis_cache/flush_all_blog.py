# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')



import json
import os


cur_dir =  os.path.abspath('.')
p_dir = os.path.dirname(cur_dir)
g_dir = os.path.dirname(p_dir)
sys.path.append(g_dir)
sys.path.append(p_dir)


from redis_con_pool import conn_pool_blog


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

from models.content_blog import ContentBlog
from models.base_orm import Session
from models.base_orm import change_to_json_1


blog_r = redis.Redis(connection_pool = conn_pool_blog)
def flush_blog_cache(blog_id, blog):
    for key in blog.keys():
        blog_r.hset(blog_id, key, blog[key])


if __name__ == "__main__":
    image_base_url =  'http://o6y4guqxy.bkt.clouddn.com/media'
    clu = Session.query(ContentBlog.id, ContentBlog.title, ContentBlog.author, func.replace(ContentBlog.cover, 'covers', '%s/covers'%image_base_url).label('cover'), func.replace(ContentBlog.thumb, 'thumb/', '%s/thumb/'%image_base_url).label('thumb'), ContentBlog.date, ContentBlog.category_id, ContentBlog.content, ContentBlog.abstract,ContentBlog.source).filter(ContentBlog.hotness == 0).all()
    clu_json = change_to_json_1(clu)
    clu_dict = json.loads(clu_json)
    for blog in clu_dict:
        blog_id = blog["id"]
        flush_blog_cache(blog_id, blog)

