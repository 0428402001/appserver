#coding=utf-8
import datetime
from sqlalchemy import Column, BigInteger, Boolean, DateTime, INTEGER
from sqlalchemy.dialects.mysql import VARCHAR, TEXT, INTEGER
from  base_orm import BASEOBJ, ModelBase


class ContentHotquery(ModelBase):
#class ContentHotcate(BASEOBJ):
#class ContentAuth(StandaloneResourceBase):

    _resource_name_ = 'query'
    __tablename__ = 'content_hotquery'

    id = Column(INTEGER, nullable=True,  primary_key = True)
    hot_key = Column(VARCHAR(40, charset='utf8'), nullable=True, default='')
    detail = Column(VARCHAR(100, charset='utf8'), nullable=True, default='')
