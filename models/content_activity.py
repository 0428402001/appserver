#coding=utf-8
import datetime
from sqlalchemy import Column, BigInteger, Boolean, DateTime, INTEGER
from sqlalchemy.dialects.mysql import VARCHAR, TEXT, INTEGER, LONGTEXT
from  base_orm import BASEOBJ, ModelBase, Session


class ContentActivity(ModelBase):
#class ContentActivity(BASEOBJ):
#class ContentAuth(StandaloneResourceBase):

    _resource_name_ = 'activity'
    __tablename__ = 'content_activity'

    id = Column(INTEGER, nullable=True,  primary_key = True)
    title = Column(VARCHAR(256, charset='utf8'), nullable=True, default='')
    cover = Column(VARCHAR(100, charset='ascii'), nullable=True, default='')
    content = Column(LONGTEXT, nullable=True, default='')
    date = Column(DateTime, nullable=True, default='')
    addr = Column(VARCHAR(30, charset='utf8'), nullable=True, default='')


