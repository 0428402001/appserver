#coding=utf-8
import datetime
from sqlalchemy import Column, BigInteger, Boolean, DateTime, INTEGER
from sqlalchemy.dialects.mysql import VARCHAR, TEXT, INTEGER
from  base_orm import BASEOBJ, ModelBase


class ContentHottag(ModelBase):
#class ContentHotcate(BASEOBJ):
#class ContentAuth(StandaloneResourceBase):

    _resource_name_ = 'content'
    __tablename__ = 'content_hottag'

    tag_id = Column(INTEGER, nullable=True,  primary_key = True)
