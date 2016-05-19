#coding=utf-8
import datetime
from sqlalchemy import Column, BigInteger, Boolean, DateTime, INTEGER
from sqlalchemy.dialects.mysql import VARCHAR, TEXT, INTEGER
from  base_orm import BASEOBJ, ModelBase, Session


class AppCommentPraise(ModelBase):
#class ContentAuth(BASEOBJ):
#class ContentAuth(StandaloneResourceBase):

    _resource_name_ = 'auth'
    __tablename__ = 'app_comment_praise'

    id = Column(INTEGER, nullable=True,  primary_key = True)
    comment_id = Column(INTEGER, nullable=True, default='')
    author_id = Column(INTEGER, nullable=True, default='')



if __name__ == '__main__':
    clu = Session.query(AppCommentPraise).all()
    for i in clu:
        print i
