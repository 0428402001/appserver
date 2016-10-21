#coding=utf-8
import datetime
from sqlalchemy import Column, BigInteger, Boolean, DateTime, INTEGER
from sqlalchemy.dialects.mysql import VARCHAR, TEXT, INTEGER
from  base_orm import BASEOBJ, ModelBase, Session


class AppPhonecode(ModelBase):
#class ContentAuth(BASEOBJ):
#class ContentAuth(StandaloneResourceBase):

    __tablename__ = 'app_phonecode'

    id = Column(INTEGER, nullable=True, primary_key = True)
    phone =  Column(VARCHAR(20, charset='utf8'), nullable=True, default='0')
    code = Column(VARCHAR(20, charset='utf8'), nullable=True, default='0')
    add_time = Column(DateTime, nullable=True, default='')





