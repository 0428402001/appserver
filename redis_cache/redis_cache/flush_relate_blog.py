# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import json
import os
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

from content_blog import ContentBlog

from content_category import ContentCategory
from content_tag import ContentTag

from base_orm import Session
from base_orm import change_to_json_1

#def mysql_checkin(dbapi_connection, connection_record):
#    logging.debug("DB checkin...")
#
#def mysql_checkout(dbapi_con, con_record, con_proxy):
#    try:
#        logging.debug("mysql_checkout: Ping MYSQL...")
#        dbapi_con.cursor().execute('select 1')
#    except dbapi_con.OperationalError, ex:
#        if ex.args[0] in (2006, 2013, 2014, 2045, 2055):
#            msg = 'Got mysql server has gone away: %s' % ex
#            logging.warn(msg)
#            raise sqlalchemy.exc.DisconnectionError(msg)
#
#
#def wrap_db_error(f):
#    """Retry DB connection. Copied from nova and modified."""
#    def _wrap(*args, **kwargs):
#        try:
#            return f(*args, **kwargs)
#        except sqlalchemy.exc.OperationalError, e:
#            if not is_db_connection_error(e.args[0]):
#                raise
#
#            _MAX_RETRIES = 10
#            _RETRY_INTERVAL = 10
#
#            remaining_attempts = _MAX_RETRIES
#            while True:
#                logging.warning('SQL connection failed. %d attempts left.' %
#                                remaining_attempts)
#                remaining_attempts -= 1
#                time.sleep(_RETRY_INTERVAL)
#                try:
#                    return f(*args, **kwargs)
#                except sqlalchemy.exc.OperationalError, e:
#                    if (remaining_attempts == 0 or
#                            not is_db_connection_error(e.args[0])):
#                        raise
#                except sqlalchemy.exc.DBAPIError:
#                    raise
#        except sqlalchemy.exc.DBAPIError:
#            raise
#    _wrap.func_name = f.func_name
#    return _wrap
#
#
#
#
#
#
#def _create_engine(desc):
#    engine_args = {
#                    'pool_recycle': 3600,
#                    'pool_size': 5,
#                    #'echo': True,
#                    'echo': False,
#                    'convert_unicode': True,
#                    # 'listeners': [MySQLPingListener()],
#                    }
#    try:
#        engine = create_engine(desc, **engine_args)
#        event.listen(engine, 'checkin', mysql_checkin)
#        event.listen(engine, 'checkout', mysql_checkout)
#        engine.connect = wrap_db_error(engine.connect)
#        engine.connect()
#        return engine
#    except Exception as e:
#        logging.error("Error connect to db engine: %s" % e)
#        raise
#
#
#
#wanka_engine = _create_engine('mysql://collegedaily:Zhuoxing1989@rdskhmm9d27q0t1etbxsfpublic.mysql.rds.aliyuncs.com:3306/collapp?charset=utf8')
#
#Session = scoped_session(sessionmaker(bind=wanka_engine,
#                                    expire_on_commit=False,
#                                    autoflush=False,
#                                    autocommit=False))

blog_pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
blog_r = redis.Redis(connection_pool=blog_pool)


conn_pool_relate_blog = redis.ConnectionPool(host='localhost', port=6379, db=1)
redis_r_blog = redis.Redis(connection_pool=conn_pool_relate_blog)




def flush_blog_cache(blog_id, blog):
    for key in blog.keys():
        redis_r_blog.hset(blog_id, key, blog[key])


if __name__ == "__main__":

    p_list = blog_r.keys()
    for blog_id in p_list:
        image_base_url =  'http://o6y4guqxy.bkt.clouddn.com/media'
        related_blog_clu = Session.query(ContentBlog.id, ContentBlog.title, func.replace(ContentBlog.cover, 'covers','%s/covers'%image_base_url).label("cover"), func.replace(ContentBlog.thumb, 'thumb/', '%s/thumb/'%image_base_url).label("thumb"),ContentBlog.date,ContentBlog.abstract,ContentBlog.category_id, ContentCategory.name.label("category_name"), ContentBlog.tag_id, ContentTag.name.label("tag_name"), ContentBlog.is_out, ContentBlog.is_big, ContentBlog.index_pic, ContentBlog.source, ContentBlog.source_url, ContentBlog.source).join(ContentCategory, ContentBlog.category_id == ContentCategory.id).join(ContentTag, ContentBlog.tag_id == ContentTag.id).filter(text("content_blog.hotness = 0 and content_blog.tag_id in (select tag_id from content_blog where id = :blog_id)")).params(blog_id =  blog_id).all()
        related_blog_json = change_to_json_1(related_blog_clu)
        related_blog_dict = json.loads(related_blog_json)
        for related_blog in related_blog_dict:
            redis_r_blog.lpush(blog_id, related_blog)
            #redis_r_blog.lrange(blog_id, 0, -1)

