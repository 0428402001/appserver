# coding=utf-8
import json
import os
import time
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



from redis_cache.redis_con_pool import conn_pool_hot_category 
from redis_cache.redis_con_pool import conn_pool_hot_blog 


from redis_cache.redis_con_pool import conn_pool_blog_content

import database


#engine = create_engine(database.DB_PATH, poolclass=NullPool)
engine = create_engine(database.DB_PATH, pool_size = 3, pool_recycle=3600, echo = False)
#engine = create_engine('mysql://collegedaily:Zhuoxing1989@rdskhmm9d27q0t1etbxsf.mysql.rds.aliyuncs.com:3306/collapp?charset=utf8', pool_size = 20, pool_recycle=200, echo = False)
Session = sessionmaker()
Session.configure(bind=engine)



def get_start_and_end(p):
    p_start = p[0]
    p_end = p[0] + p[1] -1
    return p_start, p_end


class URL(object):
    def _image_base_url():
        return 'http://o6y4guqxy.bkt.clouddn.com/media'
        #return 'http://app.collegedaily.cn/media'
    image_base_url = _image_base_url()


def _get_ad(p):
    cur_session = Session()
    clu = cur_session.query(ContentAd.id, ContentAd.title, func.replace(ContentAd.cover, "covers", "%s/covers"%URL.image_base_url).label('cover'), ContentAd.url, ContentAd.is_active).offset(p[0]).limit(p[1]).all()
    cur_session.close()
    json_res = change_to_json_1(clu)
    return json_res

def _get_hot_blog_by_cache(p):
    cur_session = Session()
    redis_hot_blog = redis.Redis(connection_pool=conn_pool_hot_blog)  
    p_start, p_end = get_start_and_end(p)
    record = redis_hot_blog.lrange('0', p_start, p_end)
    blog_s = []
    for item in record:
        blog_s.append(eval(item))
    if not blog_s:
        return 
    else:
        json_res = change_to_json_2(blog_s)
        return json_res


def _get_hot_blog(p):
    cur_session = Session()
    clu = cur_session.query(ContentBlog.id, ContentBlog.title, ContentBlog.author, func.replace(ContentBlog.cover,'covers', '%s/covers'%URL.image_base_url).label('cover'), func.replace(ContentBlog.thumb, 'thumb/', '%s/thumb/'%URL.image_base_url).label('thumb'), ContentBlog.date, ContentBlog.abstract, ContentBlog.category_id, ContentBlog.is_out, ContentBlog.is_big, ContentBlog.index_pic, ContentBlog.source, ContentBlog.source_url, ContentCategory.name.label("category_name"), ContentTag.name.label("tag_name") ).join(ContentCategory, ContentBlog.category_id == ContentCategory.id).join(ContentTag, ContentBlog.category_id == ContentTag.id).join(ContentHotblog, ContentHotblog.blog_id == ContentBlog.id).filter(ContentBlog.hotness == 0).order_by(ContentHotblog.sort.desc()).offset(p[0]).limit(p[1]).all()
    cur_session.close()
    json_res = change_to_json(clu)
    return json_res 


def _get_query_hot():
    cur_session = Session()
    clu = cur_session.query(ContentHotquery)
    cur_session.close()
    json_res = change_to_json_1(clu)
    return json_res 

def _get_category_hot():
    cur_session = Session()
    clu = cur_session.query(ContentHotcate.cate_id.label('category_id'), ContentCategory.name.label('category_name'), func.replace(ContentCategory.cover, 'covers/', '%s/covers/'%URL.image_base_url).label('cover'),ContentCategory.introduction, ContentAuth.nickname.label('dj_name'), func.replace(ContentAuth.head, 'covers', '%s/covers'%URL.image_base_url).label('dj_head'), ContentAuth.sign.label('dj_desc')).join(ContentCategory, ContentHotcate.cate_id == ContentCategory.id).join(ContentAuth, ContentCategory.dj_id == ContentAuth.id).all()
    cur_session.close()
    json_res = change_to_json_1(clu)
    return json_res 

def _get_category():
    cur_session = Session()
    clu = cur_session.query(ContentCategory.id.label('category_id'), ContentCategory.name.label('category_name'), func.replace(ContentCategory.cover, 'covers/', '%s/covers/'%URL.image_base_url).label('cover'),ContentCategory.introduction, ContentAuth.nickname.label('dj_name'), func.replace(ContentAuth.head, 'covers', '%s/covers'%URL.image_base_url).label('dj_head'), ContentAuth.sign.label('dj_desc')).join(ContentAuth, ContentCategory.dj_id == ContentAuth.id).order_by(ContentCategory.sort.desc()).all()
    cur_session.close()
    json_res = change_to_json_1(clu)
    return json_res 



def _get_app_subscription(uid, cat_set):
    cur_session = Session()
    sub_clu = cur_session.query(func.count(AppSubscription.id).label('sub_count'), AppSubscription.category_id).filter(and_(AppSubscription.author_id == uid ,AppSubscription.category_id.in_(cat_set))).group_by(AppSubscription.category_id).all()
    cur_session.close()
    json_res = change_to_json_1(sub_clu)
    return json_res 


def _get_tag_by_blog_id(blog_id):
    cur_session = Session()
    tag_name_clu = cur_session.query(ContentTag.name.label("tag_name")).join(ContentBlogTagmany.tag_id == ContentTag.id).filter(ContentBlogTagmany.blog_id == blog_id).all()
    cur_session.close()
    json_res = change_to_json_1(tag_name_clu)
    return json_res


def _get_home_page_blog(p):
    cur_session = Session()
    clu = cur_session.query(ContentBlog.id, ContentBlog.title, ContentBlog.author, func.replace(ContentBlog.cover,'covers', '%s/covers'%URL.image_base_url).label('cover'), func.replace(ContentBlog.thumb, 'thumb/', '%s/thumb/'%URL.image_base_url).label('thumb'), ContentBlog.date, ContentBlog.abstract, ContentBlog.category_id, ContentBlog.is_out, ContentBlog.is_big, ContentBlog.index_pic, ContentBlog.source, ContentBlog.source_url, ContentCategory.name.label("category_name"), ContentTag.name.label('tag_name') ).join(ContentCategory, ContentBlog.category_id == ContentCategory.id).join(ContentTag, ContentBlog.tag_id == ContentTag.id).filter(ContentBlog.hotness == 0).order_by(ContentBlog.date.desc()).offset(p[0]).limit(p[1]).all()
    cur_session.close()
    json_res = change_to_json_1(clu)
    return json_res

def _get_blog_index(p):
    cur_session = Session()
    clu = cur_session.query(ContentBlog.id, ContentBlog.title, ContentBlog.author, func.replace(ContentBlog.cover, 'covers/', '%s/covers/'%URL.image_base_url).label('cover'), func.replace(ContentBlog.thumb, 'thumb/', '%s/thumb/'%URL.image_base_url).label('thumb'), ContentBlog.date, ContentBlog.abstract, ContentBlog.category_id, ContentBlog.is_out, ContentBlog.is_big, ContentBlog.index_pic, ContentBlog.source, ContentBlog.source_url, ContentCategory.name.label("category_name") ).join(ContentCategory, ContentBlog.category_id == ContentCategory.id).join(ContentTag, ContentBlog.tag_id == ContentTag.id).filter(text("content_blog.hotness = 0 and content_blog.id in (select blog_id from content_indexblog)")).order_by(ContentBlog.date.desc()).offset(p[0]).limit(p[1]).all()
    cur_session.close()
    json_res = change_to_json_1(clu)
    return json_res


def _get_blog_query(keyword, p):
    cur_session = Session()
    clu = cur_session.query(ContentBlog.id, ContentBlog.title, ContentBlog.author, func.replace(ContentBlog.cover, 'covers/', '%s/covers/'%URL.image_base_url).label('cover'), func.replace(ContentBlog.thumb, 'thumb/', '%s/thumb/'%URL.image_base_url).label('thumb'), ContentBlog.date, ContentBlog.abstract, ContentBlog.category_id, ContentCategory.name.label("category_name"), ContentBlog.tag_id, ContentTag.name.label("tag_name"), ContentBlog.is_out, ContentBlog.is_big, ContentBlog.index_pic, ContentBlog.source, ContentBlog.source_url).join(ContentCategory, ContentBlog.category_id == ContentCategory.id).join(ContentTag, ContentBlog.tag_id == ContentTag.id).filter(and_(ContentBlog.hotness == 0, ContentBlog.title.like("%%%s%%"%keyword))).order_by(ContentBlog.date.desc()).offset(p[0]).limit(p[1]).all()
    cur_session.close()
    json_res = change_to_json_1(clu)
    return json_res



def _get_blog_favorate_uid(uid, p):
    cur_session = Session()
    clu = cur_session.query(AppFavorate.id, ContentBlog.id, ContentBlog.title, func.replace(ContentBlog.cover, 'covers', '%s/covers'%URL.image_base_url).label('cover'), func.replace(ContentBlog.thumb, 'thumb/', '%s/thumb/'%URL.image_base_url).label('thumb'), ContentBlog.abstract, ContentBlog.author).join(ContentBlog, AppFavorate.blog_id == ContentBlog.id).filter("app_favorate.author_id = :uid").params(uid = uid).order_by(AppFavorate.id).offset(p[0]).limit(p[1]).all()
    cur_session.close()
    json_res = change_to_json_1(clu)
    return json_res



def _get_app_subscri_uid(uid):
    cur_session = Session()
    clu = cur_session.query(ContentCategory.id.label('category_id'), ContentCategory.name.label('category_name'), func.replace(ContentCategory.cover, 'covers/', '%s/covers/'%URL.image_base_url).label('cover'),ContentCategory.introduction, ContentAuth.nickname.label('dj_name'), func.replace(ContentAuth.head, 'covers', '%s/covers'%URL.image_base_url).label('dj_head'), ContentAuth.sign.label('dj_desc')).join(ContentAuth, ContentCategory.dj_id == ContentAuth.id).join(AppSubscription, AppSubscription.category_id ==ContentCategory.id ).filter(AppSubscription.author_id == uid).all()
    cur_session.close()
    json_res = change_to_json_1(clu)
    return json_res

def _get_main_comment(comment_id):
    cur_session = Session()
    main_content = cur_session.query(ContentComment.id.label('comment_id'), ContentComment.author_id, ContentComment.content, ContentComment.time, ContentAuth.nickname, func.replace(ContentAuth.head, 'covers/', '%s/covers/'%URL.image_base_url).label('head'), ContentComment.praise_count).join(ContentAuth, ContentComment.author_id == ContentAuth.id).filter(ContentComment.id == comment_id)
    cur_session.close()
    main_content_json = change_to_json(main_content)
    return main_content_json

def _get_praise_people(p, comment_id):
    cur_session = Session()
    praise_info = cur_session.query(AppCommentPraise.id, AppCommentPraise.author_id, ContentAuth.nickname, func.replace(ContentAuth.head, 'covers/', '%s/covers/'%URL.image_base_url).label('head')).join(ContentAuth, AppCommentPraise.author_id == ContentAuth.id).filter(AppCommentPraise.comment_id == comment_id).offset(p[0]).limit(p[1]).all()
    cur_session.close()
    res_json = change_to_json_1(praise_info)
    return res_json

def _get_comment_reply(p, comment_id):
    cur_session = Session()
    reply_content = cur_session.query(AppCommentReply.reply_id.label("comment_id") ,ContentComment.author_id, ContentComment.content, ContentComment.time, ContentAuth.nickname, ContentAuth.head).join(ContentComment, AppCommentReply.reply_id == ContentComment.id).join(ContentAuth, ContentComment.author_id == ContentAuth.id).filter(AppCommentReply.comment_id == comment_id).offset(p[0]).limit(p[1]).all()
    cur_session.close()
    reply_content_json = change_to_json_1(reply_content)
    return reply_content_json



def _get_message_from_users_not_read(p, uid):
    changed_url = "http://o6y4guqxy.bkt.clouddn.com/media/"
    cur_session = Session()
    messages = cur_session.query(AppMessage.id, AppMessage.message_from, AppMessage.message_to,AppMessage.subject, AppMessage.content, AppMessage.date, AppMessage.message_type, AppMessage.is_read, AppMessage.blog_id, AppMessage.comment_id, func.replace(ContentAuth.head, 'covers/', '%s/covers/'%URL.image_base_url).label("head"), ContentBlog.title.label("blog_title"), ContentBlog.tag_id, ContentBlog.is_out, ContentBlog.source, ContentBlog.source_url, ContentBlog.abstract, func.replace(ContentBlog.cover, 'covers/', '%s/covers/'%changed_url).label('cover'), ContentComment.content.label('commit_content')).join(ContentAuth,  AppMessage.message_from == ContentAuth.id).join( ContentBlog, AppMessage.blog_id == ContentBlog.id).join(ContentComment, AppMessage.comment_id == ContentComment.id).filter(and_(AppMessage.message_to == uid, AppMessage.is_read == 0)).order_by(AppMessage.id.desc()).all()
    cur_session.close()
    messages_json = change_to_json_1(messages)
    return messages_json



def _get_message_from_users_allready_read(p, uid):
    changed_url = "http://o6y4guqxy.bkt.clouddn.com/media/"
    cur_session = Session()
    messages = cur_session.query(AppMessage.id, AppMessage.message_from, AppMessage.message_to,AppMessage.subject, AppMessage.content, AppMessage.date, AppMessage.message_type, AppMessage.is_read, AppMessage.blog_id, AppMessage.comment_id, func.replace(ContentAuth.head, 'covers/', '%s/covers/'%URL.image_base_url).label("head"), ContentBlog.title.label("blog_title"), ContentBlog.tag_id, ContentBlog.is_out, ContentBlog.source, ContentBlog.source_url, ContentBlog.abstract, func.replace(ContentBlog.cover, 'covers/', '%s/covers/'%changed_url).label('cover'), ContentComment.content.label('commit_content')).join(ContentAuth,  AppMessage.message_from == ContentAuth.id).join( ContentBlog, AppMessage.blog_id == ContentBlog.id).join(ContentComment, AppMessage.comment_id == ContentComment.id).filter(and_(AppMessage.message_to == uid, AppMessage.is_read == 1)).order_by(AppMessage.id.desc()).offset(p[0]).limit(p[1]).all()
    cur_session.close()
    messages_json = change_to_json_1(messages)
    return messages_json



def _get_message_from_offical():
    cur_session = Session()
    messages1 = cur_session.query(AppMessage).filter(AppMessage.message_from == 1).all()
    cur_session.close()
    messages1_json = change_to_json_1(messages1)
    return messages1_json

def _get_blog_category(uid, category_id, p):
    cur_session = Session()
    clu = cur_session.query(ContentBlog.id, ContentBlog.title, ContentBlog.author, func.replace(ContentBlog.cover, 'covers', '%s/covers'%URL.image_base_url).label('cover'), func.replace(ContentBlog.thumb,'thumb/', '%s/thumb/'%URL.image_base_url).label('thumb'), ContentBlog.date, ContentBlog.abstract, ContentBlog.category_id, ContentBlog.is_out, ContentBlog.is_big, ContentBlog.index_pic, ContentBlog.source, ContentBlog.source_url, ContentCategory.name.label("category_name"), ContentTag.name.label("tag_name")).join(ContentCategory, ContentBlog.category_id == ContentCategory.id).join(ContentTag, ContentBlog.category_id == ContentTag.id).filter(and_(ContentBlog.category_id ==  category_id, ContentBlog.hotness == 0)).order_by(ContentBlog.date.desc()).offset(p[0]).limit(p[1]).all()
    cur_session.close()
    json_res = change_to_json_1(clu)
    return json_res

def _get_blog_by_cache(blog_id):
    redis_blog = redis.Redis(connection_pool=conn_pool_blog_content)  
    record = redis_blog.hgetall(blog_id)
    if not record:
        return
    else:
        for key in record.keys():
            try:
                record[key] = eval(record[key])
            except Exception, e:
                print e
        json_res = change_to_json_2(record)
        return json_res 

def _get_blog(blog_id):
    cur_session = Session()
    blog = cur_session.query(ContentBlog.id, ContentBlog.title, ContentBlog.author, func.replace(ContentBlog.cover, 'covers', '%s/covers'%URL.image_base_url).label('cover'), func.replace(ContentBlog.thumb, 'thumb/', '%s/thumb/'%URL.image_base_url).label('thumb'), ContentBlog.date, ContentBlog.category_id, ContentBlog.content, ContentBlog.abstract,ContentBlog.source).filter(and_(ContentBlog.id == blog_id, ContentBlog.hotness == 0)).all()
    print "LENG", len(blog)
    blog_json = change_to_json(blog)
    cur_session.close()
    return blog_json

def _get_relate_blog(blog_id):
    cur_session = Session()
    related_blog_clu = cur_session.query(ContentBlog.id, ContentBlog.title, func.replace(ContentBlog.cover, 'covers','%s/covers'%URL.image_base_url).label("cover"), func.replace(ContentBlog.thumb, 'thumb/', '%s/thumb/'%URL.image_base_url).label("thumb"),ContentBlog.date,ContentBlog.abstract,ContentBlog.category_id, ContentCategory.name.label("category_name"), ContentBlog.tag_id, ContentTag.name.label("tag_name"), ContentBlog.is_out, ContentBlog.is_big, ContentBlog.index_pic, ContentBlog.source, ContentBlog.source_url, ContentBlog.source).join(ContentCategory, ContentBlog.category_id == ContentCategory.id).join(ContentTag, ContentBlog.tag_id == ContentTag.id).filter(text("content_blog.hotness = 0 and content_blog.tag_id in (select tag_id from content_blog where id = :blog_id)")).params(blog_id =  blog_id).limit(5).all()
    related_blog_json = change_to_json_1(related_blog_clu)
    cur_session.close()
    return related_blog_json

def _get_cmt_cnt(blog_id):
    cur_session = Session()
    comment_cnt_clu = cur_session.query(func.count(ContentBlogComment.comment_id).label("comment_count")).join(ContentComment, ContentBlogComment.comment_id == ContentComment.id).filter(ContentBlogComment.blog_id == blog_id).all()
    cur_session.close()
    comment_cnt = comment_cnt_clu[0][0]
    return comment_cnt

def _get_if_praise(blog_id, uid):
    cur_session = Session()
    blog_praise = cur_session.query(AppBlogPraise.id.label("pid")).filter(and_(AppBlogPraise.blog_id == blog_id, AppBlogPraise.author_id == uid)).all()
    cur_session.close()
    if len(blog_praise) == 0:
        is_praise = 0
    else:
        is_praise = 1
    return is_praise

def _get_if_favorate(blog_id,uid):
    cur_session = Session()
    blog_favorate = cur_session.query(AppFavorate.id.label("fid")).filter(and_(AppFavorate.blog_id == blog_id, AppFavorate.author_id == uid)).all()
    cur_session.close()
    if len(blog_favorate) == 0:
        is_favorate = 0
    else:
        is_favorate = 1
    return is_favorate



def _get_test2():
    cur_session = Session()
    clu = cur_session.query(ContentBlog.title. ContentBlog.id, ContentBlog.hotness).all()
    json_res = change_to_json_1(clu)
    return json_res




