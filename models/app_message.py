#coding=utf-8
import datetime
from sqlalchemy import Column, BigInteger, Boolean, DateTime, INTEGER
from sqlalchemy.dialects.mysql import VARCHAR, TEXT, INTEGER
from  base_orm import BASEOBJ, ModelBase, Session


class AppMessage(ModelBase):
#class ContentAuth(BASEOBJ):
#class ContentAuth(StandaloneResourceBase):

    _resource_name_ = 'auth'
    __tablename__ = 'app_message'

    id = Column(INTEGER, nullable=True, primary_key = True)
    message_from = Column(INTEGER, nullable=True, default='')
    message_to = Column(INTEGER, nullable=True, default='')
    subject = Column(VARCHAR(1024, charset='utf8'), nullable=True, default='')
    content = Column(TEXT, nullable=True, default='')
    date = Column(DateTime, nullable=True, default='')
    message_type = Column(INTEGER, nullable=True, default=0)
    is_read = Column(INTEGER, nullable=True, default=0)
    blog_id = Column(INTEGER, nullable=True, default=0)
    comment_id = Column(INTEGER, nullable=True, default=0)


if __name__ == "__main__":

    q = Session.query(ContentAuth).filter(ContentAuth.id == "1").all()
    for i in q:
    #tt = ContentAuth.query_to_list(None, q,{})
        print vars(i)

    #print tt

