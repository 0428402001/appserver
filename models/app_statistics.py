#coding=utf-8
import datetime
from sqlalchemy import Column, BigInteger, Boolean, DateTime, INTEGER
from sqlalchemy.dialects.mysql import VARCHAR, TEXT, INTEGER
from  base_orm import BASEOBJ, ModelBase


class AppStatistics(ModelBase):
#class AppInfo(BASEOBJ):
#class ContentAuth(StandaloneResourceBase):
    _resource_name_ = 'app'
    __tablename__ = 'app_statistics'

    id = Column(INTEGER, nullable=True,  primary_key = True)
    author_id = Column(INTEGER, nullable=True, default='')
    category_id = Column(INTEGER, nullable=True, default='')
    blog_id = Column(INTEGER, nullable=True, default='')
    dateline = Column(INTEGER, nullable=True, default='')
