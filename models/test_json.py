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
class ContentAuth_from(ContentAuth):
    pass


class ContentAuth_to(ContentAuth):
    pass

if __name__ == '__main__':
    
    clu = Session.query(ContentAuth_from.id.label('from_id') ).all()
    for i in clu:
        print type(i) 
        break



    clu = Session.query(ContentAuth_from.id ).all()
    print type(clu)
    for i in clu:
        print type(i) 
        break
