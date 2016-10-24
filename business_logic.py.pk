# coding=utf-8
import re
import json
import os
import time


from tornado.concurrent import run_on_executor

from tornado.httpclient import AsyncHTTPClient
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


import dal

#conn_pool_blog = redis.ConnectionPool(host='localhost', port=6379, db=0)
#redis_r_blog = redis.Redis(connection_pool=conn_pool_blog)





def change_to_int(page):
    try:
        page = page.encode('utf-8')
        page = float(page)
        page = int(page)
    except:
        pass
    return page 

def get_param(key, request_arguments):
    if request_arguments.has_key(key):
        value = request_arguments[key][0]
    else:
        value = None
    return value



def get_page_index(request_arguments):
    if request_arguments.has_key('page'):
        page = request_arguments['page'][0]
    else:
        page = 1
    page = change_to_int(page)
    if request_arguments.has_key('per_page'):
        per_page = request_arguments['per_page']
    else:
        per_page = 20
    per_page = change_to_int(per_page)
    start_page = (page-1)*per_page
    if start_page < 0:
        start_page = 0
    return [start_page, per_page]


def check_if_category_subscred(uid, clu):
    cat_set = set()
    for cate in clu:
        cate_id = cate['category_id']
        cat_set.add(cate_id)
    sub_clu_json = dal._get_app_subscription(uid, cat_set)
    sub_clu = json.loads(sub_clu_json)
    if_subed_dict = {}
    for i in sub_clu:
        if_subed_dict[i['category_id']] = i['sub_count']
    for i in clu:
        cat_id = i['category_id']
        if if_subed_dict.has_key(cat_id):
            i['subscribed'] = 1
        else:
            i['subscribed'] = 0
    return clu

def get_blog_content(blog_id,uid):
    json_res = dal._get_blog_by_cache(blog_id)
    if json_res:
        record = json.loads(json_res)
    else:
        print blog_id
        blog_json = dal._get_blog(blog_id)

        blog = json.loads(blog_json)
        m = re.findall(r"<[^>]*img[^>]*src[^>]*>", blog["content"])
        for img in m:
            old_img = img
            new_img = re.sub(r"src=\"", "data-original=\"", old_img)
            blog['content'] = blog['content'].replace(old_img, new_img)

        related_blog_json = dal._get_relate_blog(blog_id)
        related_blog = json.loads(related_blog_json)
        comment_cnt = dal._get_cmt_cnt(blog_id)


        record = {'blog':blog, 'related_blog':related_blog}

    is_favorate = dal._get_if_favorate(blog_id, uid)
    is_praise = dal._get_if_praise(blog_id, uid)

    record['blog']['is_favorate'] = is_favorate
    record['blog']['is_praise'] = is_praise

    res_json = change_to_json_2(record)
    return res_json





def get_info(request, args, kwargs):
    uri = request.uri
    uri = uri.split('?')[0]
    if re.search(r'^/blog/hot$', uri):
        request_arguments = request.arguments
        p = get_page_index(request_arguments)
        json_res = dal._get_hot_blog_by_cache(p)
        if json_res:
            return json_res
        else:
            json_res = dal._get_hot_blog(p)
            return json_res 
    if re.search(r'^/query/hot$', uri):
        json_res = dal._get_query_hot()
        return  json_res 
    if re.search(r'^/category/hot$', uri):
        uid = get_param('uid', request.arguments)
        json_res = dal._get_category_hot()
        if uid is None:
            return json_res 
        else:
            clu = json.loads(json_res)
            clu = check_if_category_subscred(uid, clu)
            json_res = change_to_json_2(clu)
            return json_res

    
    if re.search(r'^/category$', uri):
        uid = get_param('uid', request.arguments)
        json_res = dal._get_category()
        if uid is None:
            return json_res
        else:
            clu = json.loads(json_res)
            clu = check_if_category_subscred(uid, clu)
            json_res = change_to_json_2(clu)
            return json_res


    if re.search(r'^/ad$', uri):
        request_arguments = request.arguments
        p = get_page_index(request_arguments)
        json_res = dal._get_ad(p)
        return json_res 



    
    if re.search(r'^/blog$', uri):
        pass
        request_arguments = request.arguments
        p = get_page_index(request_arguments)
        json_res = dal._get_home_page_blog(p)
        return json_res 


    if re.search(r'^/blogview/(\d*)', uri):
        blog_id = args[0]
        uid = get_param('uid', request.arguments)
        return get_blog_content(blog_id, uid)


    if re.search(r'^/blog/\d{1,}$', uri):
        blog_id = args[0]
        uid = get_param('uid', request.arguments)

        return get_blog_content(blog_id, uid)






    if  re.search(r'^/blog/index$', uri):
        pass
        request_arguments = request.arguments
        p = get_page_index(request_arguments)
        json_res = dal._get_blog_index(p)
        return json_res 

    if re.search(r'^/blog/query/.+$', uri):
        keyword = args[0]
        request_arguments = request.arguments
        p = get_page_index(request_arguments)
        json_res = dal._get_blog_query(keyword, p)
        return json_res



    if re.search(r'^/blog/favorate/\d*$', uri):
        request_arguments = request.arguments
        p = get_page_index(request_arguments)
        uid = args[0]
        json_res = dal._get_blog_favorate_uid(uid, p)
        return json_res

    if re.search(r'^/category/subscription$', uri):
        uid = get_param('uid', request.arguments)
        json_res = dal._get_app_subscri_uid(uid)
        clu = json.loads(json_res)
        for i in clu:
            i['subscribed'] = 1
        json_res = change_to_json_2(clu)
        return json_res


    if re.search(r'^/comment/praise/\d*$', uri):
        request_arguments = request.arguments
        p = get_page_index(request_arguments)
        comment_id = args[0] 
        main_content_json = dal._get_main_comment(comment_id)
        main_content = json.loads(main_content_json)
        
        praise_info_json = dal._get_praise_people(p, comment_id) 
        praise_info = json.loads(praise_info_json)

        clu = {'main_comment': main_content,  'praise_people':praise_info}

        json_res = change_to_json_2(clu)
        return json_res



    if re.search(r'^/comment/reply/\d*$', uri):
        request_arguments = request.arguments
        p = get_page_index(request_arguments)
        comment_id = args[0] 
        main_content_json = dal._get_main_comment(comment_id)
        main_content = json.loads(main_content_json)
        reply_content_json = dal._get_comment_reply(p, comment_id)

        reply_content = json.loads(reply_content_json)
        clu = {'main_comment':main_content, 'reply_comments':reply_content}
        json_res = change_to_json_2(clu)
        return json_res
            
    if re.search(r'^/message/\d*$', uri):
        uid = args[0]
        request_arguments = request.arguments
        p = get_page_index(request_arguments)
        messages_json = dal._get_message_from_users_not_read(p, uid)
        messages = json.loads(messages_json)

        message_cnt = len(messages)
        for mess in messages:
            mess['message_cnt'] = message_cnt

        messages1_json = dal._get_message_from_offical()
        messages1 = json.loads(messages1_json)
        for mess in messages1:
            mess['message_cnt'] = message_cnt
        messages = messages1 + messages
        json_res = change_to_json_2(messages)
        return json_res



    if re.search(r'^/message/allreadyread/\d*$', uri):
        uid = args[0]
        request_arguments = request.arguments
        p = get_page_index(request_arguments)
        messages_json = dal._get_message_from_users_allready_read(p, uid)
        json_res = messages_json
        return json_res






    if re.search(r'^/blog/category/\d*$', uri):
        category_id = args[0]
        request_arguments = request.arguments
        p = get_page_index(request_arguments)
        uid = get_param('uid', request.arguments)
        json_res = dal._get_blog_category(uid, category_id, p)
        return json_res


    if re.search(r'^/test2$', uri):
        json_res = dal._get_query_hot()
        return json_res


    if re.search(r'^/test1$', uri):
        return 222 


    if re.search(r'^/rss/\d{1,}$', uri):
        blog_id = args[0]
        uid = get_param('uid', request.arguments)
        return get_blog_content(blog_id, uid)

