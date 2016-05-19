#coding=utf-8
import datetime
from sqlalchemy import Column, BigInteger, Boolean, DateTime, INTEGER
from sqlalchemy.dialects.mysql import VARCHAR, TEXT, INTEGER
from  base_orm import BASEOBJ, ModelBase, Session


class AuthPermission(ModelBase):
#class ContentAuth(BASEOBJ):

    _resource_name_ = 'auth'
    __tablename__ = 'auth_permission'

    id = Column(INTEGER, nullable=True,  primary_key = True)
    name = Column(VARCHAR(50, charset='utf8'), nullable=True, default='')
    content_type_id = Column(INTEGER, nullable=True, default='')
    codename = Column(VARCHAR(100, charset='utf8'), nullable=True, default='')

if __name__ == "__main__":

    q = Session.query(ContentAuth).filter(ContentAuth.id == "1").all()
    for i in q:
    #tt = ContentAuth.query_to_list(None, q,{})
        print vars(i)

    #print tt

