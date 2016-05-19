#coding=utf-8
import datetime
from sqlalchemy import Column, BigInteger, Boolean, DateTime, INTEGER
from sqlalchemy.dialects.mysql import VARCHAR, TEXT, INTEGER
from  base_orm import BASEOBJ, ModelBase, Session


class ContentAuthGroups(ModelBase):
#class ContentAuth(BASEOBJ):
#class ContentAuth(StandaloneResourceBase):

    _resource_name_ = 'auth'
    __tablename__ = 'content_auth_groups'

    id = Column(INTEGER, nullable=True,  primary_key = True)
    auth_id = Column(INTEGER, nullable=True, default='')
    group_id = Column(INTEGER, nullable=True, default='')


if __name__ == "__main__":

    print ContentAuth.keys()

    q = Session.query(ContentAuth).filter(ContentAuth.id == "1").all()
    for i in q:
        print dir(i)
    #tt = ContentAuth.query_to_list(None, q,{})
        print vars(i)

    #print tt

