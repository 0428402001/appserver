#coding=utf-8
import datetime
from sqlalchemy import Column, BigInteger, Boolean, DateTime, INTEGER
from sqlalchemy.dialects.mysql import VARCHAR, TEXT, INTEGER
from  base_orm import BASEOBJ, ModelBase, Session


class ContentCategory(ModelBase):
#class ContentCategory(BASEOBJ):
#class ContentAuth(StandaloneResourceBase):

    _resource_name_ = 'category'
    __tablename__ = 'content_category'

    id = Column(INTEGER, nullable=True,  primary_key = True)
    name = Column(VARCHAR(32, charset='utf8'), nullable=True, default='')
    cover = Column(VARCHAR(128, charset='utf8'), nullable=True, default='')
    introduction = Column(VARCHAR(1024, charset='utf8'), nullable=True, default='')
    dj_id = Column(INTEGER, nullable=True, default='')


