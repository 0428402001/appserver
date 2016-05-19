import os
import json
import threading
 
from xml.dom import minidom
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import (create_engine,MetaData,Column,Integer,String)
from sqlalchemy import func
from sqlalchemy.sql.expression import and_, or_
from sqlalchemy import Table, Column, Integer, String, Text, DateTime, MetaData, ForeignKey, Boolean
from datetime import datetime
import time,uuid,re

from content_auth import ContentAuth
from content_category import ContentCategory
from app_subscription import AppSubscription
from content_blog import ContentBlog
from base_orm import Session

from sqlalchemy import distinct


from sqlalchemy.ext.declarative import DeclarativeMeta
class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    if isinstance(data, datetime): 
                        data=data.strftime('%Y-%m-%d %H:%M:%S') 
                    json.dumps(data) # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            # a json-encodable dict
            return fields
    
        return json.JSONEncoder.default(self, obj)

def new_alchemy_encoder():
    _visited_objs = []
    class AlchemyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj.__class__, DeclarativeMeta):
                # don't re-visit self
                if obj in _visited_objs:
                    return None
                _visited_objs.append(obj)

                # an SQLAlchemy class
                fields = {}
                for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                    data = obj.__getattribute__(field)
                    try:
                        if isinstance(data, datetime): 
                            data=data.strftime('%Y-%m-%d %H:%M:%S') 
                        json.dumps(data) # this will fail on non-encodable values, like other classes
                        fields[field] = data
                    except TypeError:
                        fields[field] = None
                return fields

            return json.JSONEncoder.default(self, obj)
    return AlchemyEncoder

def change_to_json(session_result):
    Hosts =[]
    for vmc in vmcs:
        #print json.dumps(vmc, cls=AlchemyEncoder)
        Hosts.append(vmc)
    res_json =  json.dumps(Hosts, cls=new_alchemy_encoder(), check_circular=False)
    return res_json




def test(vmcs):
    Hosts = []
    for obj in vmcs:
        fields = {}
        #for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata' ]:
        for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata' and x != 'count' and x != 'keys' and x != 'index']:
            data = obj.__getattribute__(field)
            if isinstance(data, datetime): 
                data=data.strftime('%Y-%m-%d %H:%M:%S') 
            fields[field] = data
        Hosts.append(fields)
    return Hosts



class Tk(object):
    def __init__(self):
        self.mk = 20
    def keys(self):
        return self.__dict__.keys()

if __name__ == '__main__':
    base_url = 'http://app.collegedaily.cn/media'
    vmcs = Session.query(distinct(ContentCategory.id).label('category_id'), ContentCategory.name.label('category_name'), func.replace(ContentCategory.cover, 'covers', '%s/covers'%base_url).label('cover'), ContentCategory.introduction, ContentCategory.dj_id).all()
    uid =  548
    uid_sub = []
    for i in vmcs:
        result = {}
        for field in i._fields:
            result[field] = getattr(i,field)
        category_id = i[0]
        category_name = i[1]
        dj_id = i[4]
        clu_count = Session.query(func.count(AppSubscription.id).label('subscribed')).filter(and_(AppSubscription.category_id == category_id, AppSubscription.author_id == uid)).all()
        subscribed = clu_count[0][0]
        for j in clu_count:
            for field in j._fields:
                result[field] = getattr(j,field)

        clu_auth = Session.query(ContentAuth.nickname.label('dj_name'), func.replace(ContentAuth.head,'covers', '%s/covers'%base_url).label('dj_head'), ContentAuth.sign.label('dj_desc')).filter(ContentAuth.id == dj_id).all()
        for j in clu_auth:
            for field in j._fields:
                result[field] = getattr(j,field)
        uid_sub.append(result)
    json_res = json.dumps(uid_sub)
    print json_res





