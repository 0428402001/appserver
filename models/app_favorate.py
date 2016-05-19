#coding=utf-8
import datetime
from sqlalchemy import Column, BigInteger, Boolean, DateTime, INTEGER
from sqlalchemy.dialects.mysql import VARCHAR, TEXT, INTEGER
from  base_orm import BASEOBJ, ModelBase, Session


class AppFavorate(ModelBase):
#class ContentAuth(BASEOBJ):
#class ContentAuth(StandaloneResourceBase):

    _resource_name_ = 'auth'
    __tablename__ = 'app_favorate'

    id = Column(INTEGER, nullable=True,  primary_key = True)
    author_id = Column(INTEGER, nullable=True, default='')
    blog_id = Column(INTEGER, nullable=True, default='')


if __name__ == "__main__":

    q = Session.query(ContentAuth).filter(ContentAuth.id == "1").all()
    for i in q:
    #tt = ContentAuth.query_to_list(None, q,{})
        print vars(i)

    #print tt

