#coding=utf-8
import datetime
from sqlalchemy import Column, BigInteger, Boolean, DateTime, INTEGER
from sqlalchemy.dialects.mysql import VARCHAR, TEXT, INTEGER
from  base_orm import BASEOBJ, ModelBase


class ContentAd(ModelBase):
#class ContentActivity(BASEOBJ):
#class ContentAuth(StandaloneResourceBase):

    _resource_name_ = 'content'
    __tablename__ = 'content_ad'

    id = Column(INTEGER, nullable=True,  primary_key = True)
    title = Column(VARCHAR(256, charset='utf8'), nullable=True, default='')
    cover = Column(VARCHAR(100, charset='utf8'), nullable=True, default='')
    url = Column(VARCHAR(256, charset='utf8'), nullable=True, default='')
