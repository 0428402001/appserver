#coding=utf-8
import datetime
from sqlalchemy import Column, BigInteger, Boolean, DateTime, Integer
from sqlalchemy.dialects.mysql import VARCHAR, TEXT, INTEGER
from  base_orm import BASEOBJ, ModelBase, Session


class ContentAuth(ModelBase):

    _resource_name_ = 'auth'
    __tablename__ = 'content_auth'

    id = Column(Integer, nullable=True,  primary_key = True)
    password = Column(VARCHAR(128, charset='utf8'), nullable=True, default='')
    last_login = Column(DateTime, nullable=True, default='')
    is_superuser = Column(Integer, nullable=True, default='')
    username = Column(VARCHAR(30, charset='utf8'), nullable=True, default='')
    last_name = Column(VARCHAR(30, charset='utf8'), nullable=True, default='')
    email = Column(VARCHAR(75, charset='utf8'), nullable=True, default='')
    phone = Column(VARCHAR(75, charset='utf8'), nullable=True, default='')
    is_staff = Column(Integer, nullable=True, default='')
    is_active = Column(Integer, nullable=True, default=1)
    date_joined = Column(DateTime, nullable=True, default='')

    subscribe = Column(Integer, nullable=True, default=False)                         
    head = Column(VARCHAR(256, charset='utf8'), nullable=True, default='')       
    sign = Column(VARCHAR(200, charset='utf8'), nullable=True, default='')      
    area = Column(VARCHAR(20, charset='utf8'), nullable=True, default=0) 
    nickname = Column(VARCHAR(20, charset='utf8'), nullable=True, default='')   
    identity = Column(Integer, nullable=True, default=7)
    school = Column(VARCHAR(32, charset='utf8'), nullable=True, default='')    
    grade = Column(VARCHAR(32, charset='utf8'), nullable=True, default='')    
    regist_from = Column(Integer, nullable=True, default=0) 
    sns_type = Column(Integer, nullable=True, default=0)  
    sns_uid = Column(VARCHAR(32, charset='utf8'), nullable=True, default='')

    @classmethod
    def keys(cls):
        return cls.__dict__.keys()

class ContentAuth_to(ContentAuth):
    _resource_name_ = 'to_user'

class ContentAuth_from(ContentAuth):
    _resource_name_ = 'from_user'

if __name__ == "__main__":

    clu = Session.query(ContentAuth_from.id).all()
    #clu = Session.query(ContentAuth_from.id.label('from_id'), ContentAuth_from.username.label('from_user'), ContentAuth_to.username.label('to_user')).join(ContentAuth_to, ContentAuth_from.id == ContentAuth_to.id).all()
    for i in clu:
        pass
#        print i


