#coding=utf-8
import datetime
from sqlalchemy import Column, BigInteger, Boolean, DateTime, INTEGER
from sqlalchemy.dialects.mysql import VARCHAR, TEXT, INTEGER
from  base_orm import BASEOBJ


class AppSubscription(BASEOBJ):
#class ContentAuth(StandaloneResourceBase):

    _resource_name_ = 'app'
    __tablename__ = 'app_subscription'

    id = Column(INTEGER, nullable=True,  primary_key = True)
    author_id = Column(INTEGER, nullable=True, default='')
    category_id = Column(INTEGER, nullable=True, default='')
