#coding=utf-8
import datetime
from sqlalchemy import Column, BigInteger, Boolean, DateTime, INTEGER
from sqlalchemy.dialects.mysql import VARCHAR, TEXT, INTEGER, LONGTEXT
from  base_orm import BASEOBJ


class ContentBlog(BASEOBJ):
#class ContentAuth(StandaloneResourceBase):

    _resource_name_ = 'blog'
    __tablename__ = 'content_blog'

    id = Column(INTEGER, nullable=True,  primary_key = True)
    title = Column(VARCHAR(256, charset='utf8'), nullable=True, default='')  
    cover = Column(VARCHAR(100, charset='utf8'), nullable=True, default='')
    abstract = Column(VARCHAR(1024, charset='utf8'), nullable=True, default='')  
    content = Column(LONGTEXT, nullable=True, default='')
    author = Column(VARCHAR(128, charset='utf8'), nullable=True, default='')  
    editor = Column(VARCHAR(100, charset='utf8'), nullable=True, default='')
    tag_id = Column(INTEGER, nullable=True, default='')  
    category_id = Column(INTEGER, nullable=True, default='')
    date = Column(DateTime, nullable=True, default='')  
    hotness = Column(INTEGER, nullable=True, default='')
    new = Column(INTEGER, nullable=True, default='')  
    show_condition = Column(INTEGER, nullable=True, default='')
    praise_count = Column(INTEGER, nullable=True, default='')
    thumb = Column(VARCHAR(100, charset='utf8'), nullable=True, default='')  
    introduction = Column(VARCHAR(256, charset='utf8'), nullable=True, default='')  
    index_pic = Column(VARCHAR(100, charset='utf8'), nullable=True, default='')  
    is_big = Column(INTEGER, nullable=True, default='')  
    is_out = Column(INTEGER, nullable=True, default='')  
    source = Column(VARCHAR(100, charset='utf8'), nullable=True, default='')  
    source_url = Column(VARCHAR(100, charset='utf8'), nullable=True, default='')  
    sort = Column(INTEGER, nullable=True, default='')  
    publish_time = Column(DateTime, nullable=True, default='')  
