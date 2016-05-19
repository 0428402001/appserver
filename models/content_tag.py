#coding=utf-8
import datetime
from sqlalchemy import Column, BigInteger, Boolean, DateTime, INTEGER
from sqlalchemy.dialects.mysql import VARCHAR, TEXT, INTEGER
from  base_orm import BASEOBJ


class ContentTag(BASEOBJ):
#class ContentAuth(StandaloneResourceBase):

    _resource_name_ = 'blog'
    __tablename__ = 'content_tag'

    id = Column(INTEGER, nullable=True,  primary_key = True)
    name = Column(VARCHAR(64, charset='utf8'), nullable=True, default='')
