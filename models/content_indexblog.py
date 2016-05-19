#coding=utf-8
import datetime
from sqlalchemy import Column, BigInteger, Boolean, DateTime, INTEGER
from sqlalchemy.dialects.mysql import VARCHAR, TEXT, INTEGER
from  base_orm import BASEOBJ, ModelBase


class ContentIndexblog(ModelBase):
#class ContentComment(BASEOBJ):
#class ContentAuth(StandaloneResourceBase):

    _resource_name_ = 'auth'
    __tablename__ = 'content_indexblog'

    blog_id = Column(INTEGER, nullable=True,  primary_key = True)
