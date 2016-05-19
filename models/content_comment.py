#coding=utf-8
import datetime
from sqlalchemy import Column, BigInteger, Boolean, DateTime, INTEGER
from sqlalchemy.dialects.mysql import VARCHAR, TEXT, INTEGER
from  base_orm import BASEOBJ, ModelBase


class ContentComment(ModelBase):
#class ContentComment(BASEOBJ):
#class ContentAuth(StandaloneResourceBase):

    _resource_name_ = 'auth'
    __tablename__ = 'content_comment'

    id = Column(INTEGER, nullable=True , primary_key = True, autoincrement=True)
    content = Column(VARCHAR(256, charset='utf8'), nullable=True, default='')
    author_id = Column(INTEGER, nullable=True, default='')
    aauthor = Column(VARCHAR(256, charset='utf8'), nullable=True, default='')
    visible = Column(INTEGER, nullable=True, default=1)
    time = Column(DateTime, nullable=True, default='')
    praise_count = Column(INTEGER, nullable=True, default=0)
    report_count = Column(INTEGER, nullable=True, default=0)
    report_reason = Column(VARCHAR(200, charset='utf8'), nullable=True, default='')
