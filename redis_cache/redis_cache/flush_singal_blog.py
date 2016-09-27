# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import json
import os
import time
import subprocess
import re


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
from models.content_blog_comment import ContentBlogComment
from models.content_comment import ContentComment
from models.content_category import ContentCategory
from models.content_tag import ContentTag



from models.base_orm import change_to_json
from models.base_orm import change_to_json_1
from models.base_orm import change_to_json_2



from redis_con_pool import conn_pool_blog_content 

blog_r = redis.Redis(connection_pool = conn_pool_blog_content)
def flush_blog_cache(blog_id, blog):
    for key in blog.keys():
        blog_r.hset(blog_id, key, blog[key])


if __name__ == "__main__":
    blog_id = int(sys.argv[1])
    image_base_url =  'http://o6y4guqxy.bkt.clouddn.com/media'
    
    import database

    engine = create_engine(database.DB_PATH, pool_size = 10, pool_recycle=3600, echo = False)
    Session = sessionmaker()
    Session.configure(bind=engine)
    cur_session = Session()


    comment_cnt_clu = cur_session.query(func.count(ContentBlogComment.comment_id).label("comment_count")).join(ContentComment, ContentBlogComment.comment_id == ContentComment.id).filter(ContentBlogComment.blog_id == blog_id).all()
    comment_cnt = comment_cnt_clu[0][0]

    blog = cur_session.query(ContentBlog.id, ContentBlog.title, ContentBlog.author, func.replace(ContentBlog.cover, 'covers', '%s/covers'%image_base_url).label('cover'), func.replace(ContentBlog.thumb, 'thumb/', '%s/thumb/'%image_base_url).label('thumb'), ContentBlog.date, ContentBlog.category_id, ContentBlog.content, ContentBlog.abstract,ContentBlog.source).filter(and_(ContentBlog.id == blog_id, ContentBlog.hotness == 0)).all()
    blog_json = change_to_json(blog)
    blog = json.loads(blog_json)
    if blog:
        blog['content'] = re.sub(r"src=\"", "data-original=\"", blog['content'])
        blog['comment_count'] = comment_cnt

        #blog['is_praise'] = is_praise
        #blog['is_favorate'] = is_favorate

        related_blog_clu = cur_session.query(ContentBlog.id, ContentBlog.title, func.replace(ContentBlog.cover, 'covers','%s/covers'%image_base_url).label("cover"), func.replace(ContentBlog.thumb, 'thumb/', '%s/thumb/'%image_base_url).label("thumb"),ContentBlog.date,ContentBlog.abstract,ContentBlog.category_id, ContentCategory.name.label("category_name"), ContentBlog.tag_id, ContentTag.name.label("tag_name"), ContentBlog.is_out, ContentBlog.is_big, ContentBlog.index_pic, ContentBlog.source, ContentBlog.source_url, ContentBlog.source).join(ContentCategory, ContentBlog.category_id == ContentCategory.id).join(ContentTag, ContentBlog.tag_id == ContentTag.id).filter(text("content_blog.hotness = 0 and content_blog.tag_id in (select tag_id from content_blog where id = :blog_id)")).params(blog_id =  blog_id).all()
        related_blog_json = change_to_json_1(related_blog_clu)
        related_blog = json.loads(related_blog_json)

        #hot_comment_clu = cur_session.query(ContentBlogComment.comment_id,  ContentComment.content, ContentComment.author_id, ContentAuth.nickname, ContentComment.praise_count, ContentComment.time).join(ContentComment, ContentBlogComment.comment_id == ContentComment.id).join(ContentAuth, ContentComment.author_id == ContentAuth.id).filter(and_(ContentBlogComment.blog_id == blog_id, ContentComment.visible == 1)).all()
        #hot_comment_json = change_to_json_1(hot_comment_clu)
        #hot_comment = json.loads(hot_comment_json)
        #clu = {'blog':blog, 'related_blog':related_blog, 'hot_comment':hot_comment}

        clu = {'blog':blog, 'related_blog':related_blog}
        #json_res = change_to_json_2(clu)
        for key in clu.keys():
            print key
            blog_r.hset(blog_id, key, clu[key])
    else:
        print "the blog doesn't exist"
