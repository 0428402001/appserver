#coding=utf-8
import datetime
from sqlalchemy import Column, BigInteger, Boolean, DateTime, INTEGER
from sqlalchemy.dialects.mysql import VARCHAR, TEXT, INTEGER
from  base_orm import BASEOBJ, ModelBase, Session


class AppInfo(ModelBase):
#class AppInfo(BASEOBJ):
#class ContentAuth(StandaloneResourceBase):

    _resource_name_ = 'app'
    __tablename__ = 'app_info'

    id = Column(INTEGER, nullable=True,  primary_key = True)
    key = Column(VARCHAR(32, charset='utf8'), nullable=True, default='')
    value = Column(TEXT, nullable=True, default='')
    #value = Column(VARCHAR(64, charset='ascii'), nullable=True, default='')


if __name__ == "__main__":
    clu = Session.query(AppInfo).all()
    for i in clu:
        print i
