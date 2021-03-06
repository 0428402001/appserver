#coding=utf-8
import datetime
from sqlalchemy import Column, BigInteger, Boolean, DateTime, INTEGER
from sqlalchemy.dialects.mysql import VARCHAR, TEXT, INTEGER
from  base_orm import BASEOBJ


class ContentBlogComment(BASEOBJ):
#class ContentAuth(StandaloneResourceBase):

    _resource_name_ = 'blog'
    __tablename__ = 'content_blog_comment'

    id = Column(INTEGER, nullable=True, primary_key = True)
    blog_id = Column(INTEGER, nullable=True, default='')  
    comment_id = Column(INTEGER, nullable=True, default='')
