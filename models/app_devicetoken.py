#coding=utf-8
import datetime
from sqlalchemy import Column, BigInteger, Boolean, DateTime, INTEGER
from sqlalchemy.dialects.mysql import VARCHAR, TEXT, INTEGER
from  base_orm import BASEOBJ, ModelBase, Session


class AppDevicetoken(ModelBase):
#class ContentAuth(BASEOBJ):
#class ContentAuth(StandaloneResourceBase):

    _resource_name_ = 'auth'
    __tablename__ = 'app_devicetoken'

    id = Column(INTEGER, nullable=True,  primary_key = True)
    author_id = Column(INTEGER, nullable=True, default='')
    device_token = Column(VARCHAR(100, charset='utf8'), nullable=True, default='')
    update_dateline = Column(INTEGER, nullable=True, default='')
    enable_push = Column(INTEGER, nullable=True, default=1)



