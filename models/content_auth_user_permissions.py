#coding=utf-8
import datetime
from sqlalchemy import Column, BigInteger, Boolean, DateTime, INTEGER
from sqlalchemy.dialects.mysql import VARCHAR, TEXT, INTEGER
from  base_orm import BASEOBJ, ModelBase, Session


class ContentAuthUserPermissions(ModelBase):
#class ContentAuth(BASEOBJ):
#class ContentAuth(StandaloneResourceBase):

    _resource_name_ = 'auth'
    __tablename__ = 'content_auth_user_permissions'

    id = Column(INTEGER, nullable=True, primary_key = True)
    auth_id = Column(INTEGER, nullable=True, default='')
    group_id = Column(INTEGER, nullable=True, default='')



