#!/usr/bin/env python

import logging
import uuid
import random
import time
import json

import datetime

from wanka.common import timeutils
from wanka.common import regutils
from wanka.common import stringutils
from wanka.common import filterclauses
from wanka.common import boolutils
from wanka.common import threadutils

from tornado.options import options
from tornado.web import HTTPError

import sqlalchemy
from sqlalchemy import Column, DateTime, Boolean, BigInteger, Text
from sqlalchemy import or_
from sqlalchemy import event
from sqlalchemy.dialects.mysql import VARCHAR
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, Session, object_mapper
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import TypeDecorator


def _to_str(string):
    if string is not None:
        if not isinstance(string, basestring):
            return str(string)
        else:
            return string
    else:
        return None

def brief_str(obj):
    brief_len = 18
    objstr = _to_str(obj)
    if objstr is None:
        objstr = 'None'
    if len(objstr) > brief_len:
        return objstr[:brief_len] + '...'
    else:
        return objstr


"""
SQLAlchemy models for database
"""


class MySQLPingListener(object):
    """
    Ensures that MySQL connections checked out of the
    pool are alive.

    Borrowed from:
    http://groups.google.com/group/sqlalchemy/msg/a4ce563d802c929f
    """
    def checkout(self, dbapi_con, con_record, con_proxy):
        try:
            print "Ping MYSQL..."
            dbapi_con.cursor().execute('select 1')
        except dbapi_con.OperationalError, ex:
            if ex.args[0] in (2006, 2013, 2014, 2045, 2055):
                msg = 'Got mysql server has gone away: %s' % ex
                logging.warn(msg)
                raise sqlalchemy.exc.DisconnectionError(msg)
            else:
                raise


def get_utcnow():
    return timeutils.utcnow()


def get_uuid():
    return str(uuid.uuid4())


BASEOBJ = declarative_base()


class ModelBase(BASEOBJ):
    """Base class for Nova and Glance Models"""
    __abstract__ = True
    __table_args__ = {'mysql_engine': 'InnoDB'}
    __table_initialized__ = False

    def save_object(self):
        """Save a new object"""
        session = master_db()
        session.add(self)
        session.commit()
        clean_db_session()

    def save_updates(self):
        """Save a new object"""
        session = master_db()
        session.add(self)
        session.commit()
        clean_db_session()

    @classmethod
    def query(cls, *args):
        """ Query """
        session = slave_db()
        if len(args) == 0:
            q = session.query(cls)
        else:
            q = session.query(*args)
        return q

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def __iter__(self):
        self._i = iter(object_mapper(self).columns)
        return self

    def next(self):
        n = self._i.next().name
        return n, getattr(self, n)

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def items(self):
        return self.__dict__.items()

    def to_dict(self):
        dt = self.__dict__.copy()
        ret = {}
        for k in dt.keys():
            if not k.startswith('_'):
                v = dt[k]
                if type(v) in [datetime.datetime]:
                    v = timeutils.isotime(v)
                elif not type(v) in [basestring, str, unicode, int, float]:
                    v = r'%s' % v
                ret[k] = v
        return ret

    @classmethod
    def convert_base64_id(cls):
        pass

    @classmethod
    def get_column_def(cls, colname):
        for c in cls.__table__.columns:
            if c.name == colname:
                return c
        return None

    @classmethod
    def is_column_string(cls, col):
        if hasattr(col.type, 'charset'):
            return True
        else:
            return False

    @classmethod
    def is_searchable(cls, col, is_chs):
        if hasattr(col.type, 'charset') and \
                (not is_chs or col.type.charset == 'utf8'):
            return True
        return False


class JSONEncodedDict(TypeDecorator):
    "Represents an immutable structure as a json-encoded string."
    impl = Text

    def process_bind_param(self, value, dialect):
        if value is not None:
            try:
                value = json.dumps(value)
            except Exception as e:
                logging.error('JSONEncodedDict: dump error %s' % e)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            try:
                value = json.loads(value)
            except Exception as e:
                logging.error('JSONEncodedDict: load error %s' % e)
        return value


class ResourceBase(ModelBase):
    """ Base class for resource type object """
    __abstract__ = True

    _resource_name_ = None
    _alias_name_ = None

    __protected_attributes__ = set([
        "created_at", "updated_at", "deleted_at", "deleted"])

    created_at = Column(DateTime, default=get_utcnow,
                        nullable=False)
    updated_at = Column(DateTime, default=get_utcnow,
                        nullable=False, onupdate=get_utcnow)
    deleted_at = Column(DateTime)
    deleted = Column(Boolean, nullable=False, default=False)

    @classmethod
    def context_class(cls):
        return None

    @classmethod
    def query(cls, *args):
        """ Query """
        session = master_db()
        if len(args) == 0:
            q = session.query(cls).filter(cls.deleted != True)
        else:
            q = session.query(*args).filter(cls.deleted != True)
        return q

    @classmethod
    def raw_query(cls, *args):
        """ Query """
        return super(ResourceBase, cls).query(*args)

    @classmethod
    def fetch(cls, id, user_cred=None):
        return NotImplemented

    def delete(self):
        """Delete this object"""
        self.deleted = True
        self.deleted_at = get_utcnow()
        self.save_updates()

    @classmethod
    def create_required_fields(cls):
        return NotImplemented

    @classmethod
    def create_optional_fields(cls):
        return NotImplemented

    def post_create(self, user_cred, owner_cred, data):
        pass

    def post_update(self, user_cred, data):
        pass

    def pre_delete(self, user_cred):
        pass

    def customize_create(self, user_cred, owner_cred, data):
        return ''

    @classmethod
    def validate_create_data(cls, user_cred, owner_cred, data):
        return ''

    @classmethod
    def create_item(cls, kwargs):
        item = cls()
        for field in cls.create_required_fields():
            setattr(item, field, kwargs.get(field))
        for field in cls.create_optional_fields():
            val = kwargs.get(field)
            if val is not None:
                setattr(item, field, val)
        return item

    @classmethod
    def update_fields(cls):
        return NotImplemented

    def validate_update_data(self, user_cred, kwargs):
        return ''

    def update_item(self, kwargs):
        change_str = ''
        for field in self.update_fields():
            if kwargs.has_key(field):
                old_val = getattr(self, field, None)
                new_val = kwargs.get(field)
                if _to_str(old_val) != _to_str(new_val):
                    setattr(self, field, new_val)
                    if change_str != '':
                        change_str += ';'
                    change_str += '%s:%s=>%s;' % (field, brief_str(old_val),
                                                brief_str(new_val))
        if change_str != '':
            self.save_updates()
        return change_str

    def validate_delete_condition(self, user_cred):
        return ''

    @classmethod
    def detail_fields(cls, user_cred):
        return ['created_at']

    def get_details(self, user_cred, kwargs):
        kwval = {}
        for field in self.detail_fields(user_cred):
            val = getattr(self, field, None)
            if val is not None:
                if isinstance(val, datetime.datetime):
                    kwval[field] = timeutils.isotime(val)
                else:
                    kwval[field] = val
        return kwval

    @classmethod
    def list_fields(cls, user_cred):
        return []

    @classmethod
    def search_fields(cls, user_cred):
        return cls.list_fields(user_cred)

    @classmethod
    def list_items_filter(cls, query, user_cred, data):
        return query

    @classmethod
    def list_items_query(cls, user_cred, kwargs):
        q = cls.query()
        print "&&&", user_cred, kwargs, q
        for key in kwargs:
            field = getattr(cls, key, None)
            if field is not None:
                q = q.filter(field==kwargs.get(key))
        return q

    @classmethod
    def apply_list_items_search_filters(cls, user_cred, search, filters):
        likes = search.split(',')
        for like in likes:
            like = like.strip()
            if len(like) > 0:
                like_args = []
                like_str = '%' + like + '%'
                is_chs = stringutils.is_chs(like)
                for k in cls.search_fields(user_cred):
                    col = getattr(cls, k, None)
                    if col is not None:
                        cdef = cls.get_column_def(k)
                        if cdef is not None and cls.is_searchable(cdef, is_chs):
                            like_args.append(col.like(like_str))
                if len(like_args) > 0:
                    filters.append(or_(*like_args))

    @classmethod
    def list_items(cls, user_cred, kwargs):
        max_limit = 2048
        if kwargs.has_key('limit'):
            limit = int(kwargs['limit'])
        else:
            limit = 0
        if kwargs.has_key('offset'):
            offset = int(kwargs['offset'])
        else:
            offset = 0
        print "database.py", user_cred
        q = cls.list_items_query(user_cred, kwargs)
        q = cls.list_items_filter(q, user_cred, kwargs)
        filters = []
        if 'search' in kwargs and len(kwargs['search']) > 0:
            cls.apply_list_items_search_filters(user_cred,
                            kwargs['search'], filters)
        f_idx = 0
        while ('filter.%d') % f_idx in kwargs:
            filter = kwargs['filter.%d' % f_idx]
            f_idx += 1
            f = filterclauses.parse(filter)
            if f is not None:
                cond = f.get_filter(cls)
                if cond is not None:
                    print cond
                    filters.append(cond)
        if len(filters) > 0:
            if kwargs.get('filter_any', False):
                q = q.filter(or_(*filters))
            else:
                for cond in filters:
                    q = q.filter(cond)
        total_cnt = q.count()
        if total_cnt > max_limit and (limit <= 0 or limit > max_limit):
            limit = max_limit
        if not kwargs.has_key('order_by'):
            iddef = cls.get_column_def('id')
            if iddef is not None and not cls.is_column_string(iddef):
                kwargs['order_by'] = 'id'
            else:
                kwargs['order_by'] = 'created_at'
            kwargs['order'] = 'desc'
        order_by_col = getattr(cls, kwargs['order_by'], None)
        if order_by_col is not None:
            if kwargs.has_key('order') and kwargs['order'] == 'desc':
                order_func = getattr(order_by_col, 'desc', None)
            else:
                order_func = getattr(order_by_col, 'asc', None)
            if order_func is not None:
                q = q.order_by(order_func())
        if limit > 0:
            q = q.limit(limit)
        if offset > 0:
            q = q.offset(offset)
        retlist = cls.query_to_list(user_cred, q, kwargs)
        return (retlist, total_cnt, limit, offset)

    @classmethod
    def query_to_list(cls, user_cred, q, kwargs):
        retlist = []
        for row in q.all():
            item = {}
            for k in cls.list_fields(user_cred):
                if k=='name':
                    c = row.get_name()
                else:
                    c = getattr(row, k, None)
                if c is not None:
                    if isinstance(c, datetime.datetime):
                        item[k] = timeutils.isotime(c)
                    else:
                        item[k] = c
            if 'details' not in kwargs or kwargs['details'] in ['True', True]:
                func = getattr(row, 'get_customize_columns', None)
                if func is not None and callable(func):
                    new_item = func(user_cred, kwargs)
                else:
                    new_item = None
                if new_item is not None and len(new_item) > 0:
                    for k in new_item:
                        item[k] = new_item[k]
            retlist.append(item)
        return retlist

    @classmethod
    def produce_list_items_response(cls, user_cred, kwargs, ret):
        (retlist, total_cnt, limit, offset) = ret
        retlen = len(retlist)
        retlist = cls.customize_filter_list(retlist, user_cred, kwargs)
        if len(retlist) != retlen:
            total_cnt = len(retlist)
        retval = {}
        retval[cls._resource_name_ + 's'] = retlist
        if len(retlist) != total_cnt:
            retval['total'] = total_cnt
            if limit > 0:
                retval['limit'] = limit
            if offset > 0:
                retval['offset'] = offset
        return retval

    def get_customize_columns(self, user_cred, kwargs):
        return {}

    @classmethod
    def customize_filter_list(cls, results, user_cred, kwargs):
        return results

    def customize_delete(self, user_cred):
        return ''


class StandaloneResourceBase(ResourceBase):
    """ Base class for standalone resource type object """
    __abstract__ = True

    _NAME_SEPARATOR_ = '-'
    _NAME_LENGTH_ = 128
    _NAME_REQUIRE_ASCII_ = True

    id = Column(VARCHAR(36, charset='ascii'), primary_key=True, default=get_uuid)
    name = Column(VARCHAR(_NAME_LENGTH_, charset='utf8'),
                            nullable=False, index=True)
    description   = Column(VARCHAR(256, charset='utf8'))

    def get_name(self):
        return self.name

    def get_short_desc(self):
        desc = {}
        desc['res_name'] = self._resource_name_
        desc['id'] = self.id
        desc['name'] = self.get_name()
        return desc

    def get_details(self, user_cred, kwargs):
        kwval = super(StandaloneResourceBase, self).get_details(user_cred, kwargs)
        kwval['name'] = self.get_name()
        if kwargs.has_key('with_meta') and kwargs['with_meta']:
            meta = self.get_all_metadata()
            if len(meta) > 0:
                kwval['metadata'] = meta
        features = self.get_extra_features()
        if features is not None:
            for key in features.keys():
                kwval[key] = features[key]
        return kwval

    def get_extra_features(self):
        from wanka.common.service_extra_features import resource_extra_feature_map
        extra_class = resource_extra_feature_map.get(
                self._resource_name_, None)
        if extra_class is not None:
            features = extra_class.get_features_details(self)
            return features
        return None

    @classmethod
    def fetch(cls, id_str, user_cred=None):
        obj = cls.fetch_by_id(id_str)
        if obj is not None:
            return obj
        return cls.fetch_by_name(id_str, user_cred)

    @classmethod
    def raw_fetch(cls, id_str):
        return cls.raw_query().filter(cls.id==id_str).first()

    @classmethod
    def fetch_by_id(cls, id_str):
        if regutils.match_uuid(id_str):
            obj = cls.query().filter(cls.id==id_str).first()
            return obj
        return None

    @classmethod
    def fetch_by_name(cls, name, user_cred):
        return cls.query().filter(cls.name==name).first()

    @classmethod
    def is_new_name_unique(cls, name_str, user_cred, kwargs):
        return NotImplemented

    def is_alter_name_unique(self, name_str, user_cred, kwargs):
        return NotImplemented

    @classmethod
    def allow_list_items(cls, user_cred, qsvars, ctx_obj=None):
        return NotImplemented

    def allow_get_details(self, user_cred):
        return NotImplemented

    def allow_delete_item(self, user_cred):
        return NotImplemented

    @classmethod
    def allow_create_item(cls, user_cred, ctx_obj=None):
        return NotImplemented

    def allow_update_item(self, user_cred):
        return NotImplemented

    @classmethod
    def allow_name_separator(cls):
        return False

    @classmethod
    def validate_name(cls, namestr):
        # if namestr.find(cls._NAME_SEPARATOR_) >= 0 and \
        #         not cls.allow_name_separator():
        #     return 'Symbol "%s" not allowed in name' % cls._NAME_SEPARATOR_
        # elif cls._NAME_REQUIRE_ASCII_ and not regutils.match_name(namestr):
        #     return 'Name starts with letter, \
        #             and contains letter, number and ._@- only'
        if len(namestr) > cls._NAME_LENGTH_:
            return 'Name longer than %d' % (cls._NAME_LENGTH_)
        else:
            return ''

    @classmethod
    def validate_create_data(cls, user_cred, owner_cred, kwargs):
        if 'name' in kwargs:
            ret = cls.validate_name(kwargs['name'])
            if len(ret) > 0:
                return ret
            cred = owner_cred
            if cred is None:
                cred = user_cred
            if not cls.is_new_name_unique(kwargs['name'], cred, kwargs):
                return "Duplicate name %s" % kwargs['name']
        return super(StandaloneResourceBase, cls) \
                        .validate_create_data(user_cred, owner_cred, kwargs)

    def validate_update_data(self, user_cred, kwargs):
        if 'name' in kwargs:
            ret = self.validate_name(kwargs['name'])
            if len(ret) > 0:
                return ret
            if not self.is_alter_name_unique(kwargs['name'], user_cred, kwargs):
                return "Duplicate name %s" % kwargs['name']
        return super(StandaloneResourceBase, self) \
                        .validate_update_data(user_cred, kwargs)

    def get_metadata(self, key):
        from wanka.models.metadata import Metadata
        return Metadata.get_value(self, key)

    def set_metadata(self, key, value, user_cred):
        from wanka.models.metadata import Metadata
        if Metadata.is_sysadmin_key(key) and not user_cred.is_system_admin():
            return False
        if value is not None and value in ['null', 'None']:
            value = None
        return Metadata.set_value(self, key, value, user_cred)

    def set_all_metadata(self, dictstore, user_cred):
        from wanka.models.metadata import Metadata
        for k in dictstore.keys():
            if Metadata.is_sysadmin_key(k) and not user_cred.is_system_admin():
                return False
            if dictstore[k] is not None and \
                    isinstance(dictstore[k], basestring) and \
                    dictstore[k].lower() in ['none', 'null']:
                dictstore[k] = None
        return Metadata.set_all(self, dictstore, user_cred)

    def remove_metadata(self, key, user_cred):
        from wanka.models.metadata import Metadata
        return Metadata.set_value(self, key, None, user_cred)

    def remove_all_metadata(self, user_cred):
        from wanka.models.metadata import Metadata
        return Metadata.remove_all(self, user_cred)

    def get_all_metadata(self):
        from wanka.models.metadata import Metadata
        return Metadata.get_all(self)

    def allow_get_details_metadata(self, user_cred, field=None):
        return user_cred.is_system_admin()

    def get_details_metadata(self, user_cred, field=None):
        if field is not None:
            val = self.get_metadata(field)
        else:
            val = self.get_all_metadata()
        # print val
        return val

    def allow_perform_metadata(self, user_cred, **kwargs):
        return user_cred.is_system_admin()

    def perform_metadata(self, user_cred, **kwargs):
        if self.set_all_metadata(kwargs, user_cred):
            return ''
        else:
            return 'Failed to set metadata'

    def get_customize_columns(self, user_cred, kwargs):
        cols = super(StandaloneResourceBase, self) \
                        .get_customize_columns(user_cred, kwargs)
        if kwargs.has_key('with_meta') and \
                boolutils.to_bool(kwargs['with_meta']):
            meta = self.get_all_metadata()
            if len(meta) > 0:
                cols['metadata'] = meta
        return cols

    def post_update(self, user_cred, data):
        super(StandaloneResourceBase, self).post_update(user_cred, data)
        if data.has_key('__meta__'):
            kwargs = data['__meta__']
            self.perform_metadata(user_cred, **kwargs)

    def post_create(self, user_cred, owner_cred, data):
        super(StandaloneResourceBase, self).post_create(user_cred,
                                                        owner_cred, data)
        if '__meta__' in data:
            kwargs = data['__meta__']
            self.perform_metadata(user_cred, **kwargs)

    def pre_delete(self, user_cred):
        super(StandaloneResourceBase, self).pre_delete(user_cred)
        self.remove_all_metadata(user_cred)


class JointResourceBase(ResourceBase):
    """ Base class for joint resource type object """

    __abstract__ = True

    row_id = Column(BigInteger, primary_key=True)

    @classmethod
    def fetch(cls, item1, item2):
        key1 = getattr(cls, item1._resource_name_ + '_id', None)
        if key1 is None and item1._alias_name_ is not None:
            key1 = getattr(cls, item1._alias_name_ + '_id', None)
        key2 = getattr(cls, item2._resource_name_ + '_id', None)
        if key2 is None and item2._alias_name_ is not None:
            key2 = getattr(cls, item2._alias_name_ + '_id', None)
        if key1 is not None:
            q = cls.query().filter(key1==item1.id)
            if q is not None and key2 is not None:
                q = q.filter(key2==item2.id)
                if q is not None:
                    return q.first()
        return None

    def get_details(self, item1, item2, user_cred, kwargs):
        kwval = super(JointResourceBase, self).get_details(user_cred, kwargs)
        kwval[item1._resource_name_] = item1.get_name()
        kwval[item2._resource_name_] = item2.get_name()
        return kwval

    @classmethod
    def allow_list_items(cls, ctx_obj, user_cred, qsvars):
        return NotImplemented

    @classmethod
    def allow_create_item(cls, res1, res2, user_cred):
        return NotImplemented

    def allow_get_details(self, res1, res2, user_cred):
        return NotImplemented

    def allow_delete_item(self, res1, res2, user_cred):
        return NotImplemented

    def allow_update_item(self, res1, res2, user_cred):
        return NotImplemented

    def validate_delete_condition(self, user_cred, res1, res2):
        return ''

    def validate_update_data(self, user_cred, kwargs, res1, res2):
        return ''

    @classmethod
    def validate_create_data(cls, user_cred, owner_cred, kwargs, res1, res2):
        return ''


'''
class StandaloneResourceBase(ResourceBase):
    """ Base class for standalone resource type object """
    __abstract__ = True

    _NAME_SEPARATOR_ = '-'
    _NAME_LENGTH_ = 128
    _NAME_REQUIRE_ASCII_ = True

    id = Column(VARCHAR(36, charset='ascii'), primary_key=True, default=get_uuid)
    name = Column(VARCHAR(_NAME_LENGTH_, charset='utf8'),
                            nullable=False, index=True)
    description   = Column(VARCHAR(256, charset='utf8'))

    def get_name(self):
        return self.name

    def get_short_desc(self):
        desc = {}
        desc['res_name'] = self._resource_name_
        desc['id'] = self.id
        desc['name'] = self.get_name()
        return desc

    def get_details(self, user_cred, kwargs):
        kwval = super(StandaloneResourceBase, self).get_details(user_cred, kwargs)
        kwval['name'] = self.get_name()
        if kwargs.has_key('with_meta') and kwargs['with_meta']:
            meta = self.get_all_metadata()
            if len(meta) > 0:
                kwval['metadata'] = meta
        features = self.get_extra_features()
        if features is not None:
            for key in features.keys():
                kwval[key] = features[key]
        return kwval

    def get_extra_features(self):
        from wanka.common.service_extra_features import resource_extra_feature_map
        extra_class = resource_extra_feature_map.get(
                self._resource_name_, None)
        if extra_class is not None:
            features = extra_class.get_features_details(self)
            return features
        return None

    @classmethod
    def fetch(cls, id_str, user_cred=None):
        obj = cls.fetch_by_id(id_str)
        if obj is not None:
            return obj
        return cls.fetch_by_name(id_str, user_cred)

    @classmethod
    def raw_fetch(cls, id_str):
        return cls.raw_query().filter(cls.id==id_str).first()

    @classmethod
    def fetch_by_id(cls, id_str):
        if regutils.match_uuid(id_str):
            obj = cls.query().filter(cls.id==id_str).first()
            return obj
        return None

    @classmethod
    def fetch_by_name(cls, name, user_cred):
        return cls.query().filter(cls.name==name).first()

    @classmethod
    def is_new_name_unique(cls, name_str, user_cred, kwargs):
        if cls.query() \
                .filter(cls.name==name_str).count() == 0:
            return True
        else:
            return False

    def is_alter_name_unique(self, name_str, user_cred, kwargs):
        cls = self.__class__
        if cls.query() \
                .filter(cls.name==name_str) \
                .filter(cls.id!=self.id).count() == 0:
            return True
        else:
            return False

    @classmethod
    def allow_list_items(cls, user_cred, qsvars, ctx_obj=None):
        return NotImplemented

    def allow_get_details(self, user_cred):
        return NotImplemented

    def allow_delete_item(self, user_cred):
        return NotImplemented

    @classmethod
    def allow_create_item(cls, user_cred, ctx_obj=None):
        return NotImplemented

    def allow_update_item(self, user_cred):
        return NotImplemented

    @classmethod
    def allow_name_separator(cls):
        return False

    @classmethod
    def validate_name(cls, namestr):
        if namestr.find(cls._NAME_SEPARATOR_) >= 0 and \
                not cls.allow_name_separator():
            return 'Symbol "%s" not allowed in name' % cls._NAME_SEPARATOR_
        elif cls._NAME_REQUIRE_ASCII_ and not regutils.match_name(namestr):
            return 'Name starts with letter, \
                    and contains letter, number and ._@- only'
        elif len(namestr) > cls._NAME_LENGTH_:
            return 'Name longer than %d' % (cls._NAME_LENGTH_)
        else:
            return ''

    @classmethod
    def validate_create_data(cls, user_cred, owner_cred, kwargs):
        if 'name' in kwargs:
            ret = cls.validate_name(kwargs['name'])
            if len(ret) > 0:
                return ret
            cred = owner_cred
            if cred is None:
                cred = user_cred
            if not cls.is_new_name_unique(kwargs['name'], cred, kwargs):
                return "Duplicate name %s" % kwargs['name']
        return super(StandaloneResourceBase, cls) \
                        .validate_create_data(user_cred, owner_cred, kwargs)

    def validate_update_data(self, user_cred, kwargs):
        if 'name' in kwargs:
            ret = self.validate_name(kwargs['name'])
            if len(ret) > 0:
                return ret
            if not self.is_alter_name_unique(kwargs['name'], user_cred, kwargs):
                return "Duplicate name %s" % kwargs['name']
        return super(StandaloneResourceBase, self) \
                        .validate_update_data(user_cred, kwargs)

    def get_metadata(self, key):
        from wanka.models.metadata import Metadata
        return Metadata.get_value(self, key)

    def set_metadata(self, key, value, user_cred):
        from wanka.models.metadata import Metadata
        if Metadata.is_sysadmin_key(key) and not user_cred.is_system_admin():
            return False
        if value is not None and value in ['null', 'None']:
            value = None
        return Metadata.set_value(self, key, value, user_cred)

    def set_all_metadata(self, dictstore, user_cred):
        from wanka.models.metadata import Metadata
        for k in dictstore.keys():
            if Metadata.is_sysadmin_key(k) and not user_cred.is_system_admin():
                return False
            if dictstore[k] is not None and \
                    isinstance(dictstore[k], basestring) and \
                    dictstore[k].lower() in ['none', 'null']:
                dictstore[k] = None
        return Metadata.set_all(self, dictstore, user_cred)

    def remove_metadata(self, key, user_cred):
        from wanka.models.metadata import Metadata
        return Metadata.set_value(self, key, None, user_cred)

    def remove_all_metadata(self, user_cred):
        from wanka.models.metadata import Metadata
        return Metadata.remove_all(self, user_cred)

    def get_all_metadata(self):
        from wanka.models.metadata import Metadata
        return Metadata.get_all(self)

    def allow_get_details_metadata(self, user_cred, field=None):
        return user_cred.is_system_admin()

    def get_details_metadata(self, user_cred, field=None):
        if field is not None:
            val = self.get_metadata(field)
        else:
            val = self.get_all_metadata()
        # print val
        return val

    def allow_perform_metadata(self, user_cred, **kwargs):
        return user_cred.is_system_admin()

    def perform_metadata(self, user_cred, **kwargs):
        if self.set_all_metadata(kwargs, user_cred):
            return ''
        else:
            return 'Failed to set metadata'

    def get_customize_columns(self, user_cred, kwargs):
        cols = super(StandaloneResourceBase, self) \
                        .get_customize_columns(user_cred, kwargs)
        if kwargs.has_key('with_meta') and \
                boolutils.to_bool(kwargs['with_meta']):
            meta = self.get_all_metadata()
            if len(meta) > 0:
                cols['metadata'] = meta
        return cols

    def post_update(self, user_cred, data):
        super(StandaloneResourceBase, self).post_update(user_cred, data)
        if data.has_key('__meta__'):
            kwargs = data['__meta__']
            self.perform_metadata(user_cred, **kwargs)

    def post_create(self, user_cred, owner_cred, data):
        super(StandaloneResourceBase, self).post_create(user_cred,
                                                        owner_cred, data)
        if '__meta__' in data:
            kwargs = data['__meta__']
            self.perform_metadata(user_cred, **kwargs)

    def pre_delete(self, user_cred):
        super(StandaloneResourceBase, self).pre_delete(user_cred)
        self.remove_all_metadata(user_cred)

    def set_status(self, status):
        if hasattr(self, 'status'):
            self.status = status
            self.save_updates()

    def allow_perform_status(self, user_cred, status=None):
        return hasattr(self, 'status') and user_cred.is_system_admin()

    def perform_status(self, user_cred, status=None):
        if hasattr(self, 'status') and \
                status is not None and self.status != status:
            self.set_status(status)
        return ''


class KeystoneCacheObject(StandaloneResourceBase):
    __abstract__ = True

    @classmethod
    def save(cls, idstr, name):
        obj = cls.query().filter(cls.id==idstr).first()
        if obj is None:
            obj = cls(id=idstr, name=name)
            obj.save_object()
        elif obj.name != name:
            obj.name = name
            obj.save_updates()

    @classmethod
    def batch_fetch_names(cls, idstrs):
        objs = cls.query().filter(cls.id.in_(idstrs)).all()
        table = {}
        for t in objs:
            table[t.id] = t.name
        return table

    @classmethod
    def fetch_by_id_or_name(cls, idstr):
        obj = cls.fetch_by_id(idstr)
        if obj is None:
            obj = cls.fetch_by_name(idstr)
        return obj

    @classmethod
    def fetch_by_id(cls, idstr):
        if stringutils.is_chs(idstr):
            return None
        return cls.query().filter(cls.id==idstr).first()

    @classmethod
    def fetch_by_name(cls, namestr, user_cred=None):
        return cls.query().filter(cls.name==namestr).first()


class JointResourceBase(ResourceBase):
    """ Base class for joint resource type object """

    __abstract__ = True

    row_id = Column(BigInteger, primary_key=True)

    @classmethod
    def fetch(cls, item1, item2):
        key1 = getattr(cls, item1._resource_name_ + '_id', None)
        if key1 is None and item1._alias_name_ is not None:
            key1 = getattr(cls, item1._alias_name_ + '_id', None)
        key2 = getattr(cls, item2._resource_name_ + '_id', None)
        if key2 is None and item2._alias_name_ is not None:
            key2 = getattr(cls, item2._alias_name_ + '_id', None)
        if key1 is not None:
            q = cls.query().filter(key1==item1.id)
            if q is not None and key2 is not None:
                q = q.filter(key2==item2.id)
                if q is not None:
                    return q.first()
        return None

    def get_details(self, item1, item2, user_cred, kwargs):
        kwval = super(JointResourceBase, self).get_details(user_cred, kwargs)
        kwval[item1._resource_name_] = item1.get_name()
        kwval[item2._resource_name_] = item2.get_name()
        return kwval

    @classmethod
    def allow_list_items(cls, ctx_obj, user_cred, qsvars):
        return NotImplemented

    @classmethod
    def allow_create_item(cls, res1, res2, user_cred):
        return NotImplemented

    def allow_get_details(self, res1, res2, user_cred):
        return NotImplemented

    def allow_delete_item(self, res1, res2, user_cred):
        return NotImplemented

    def allow_update_item(self, res1, res2, user_cred):
        return NotImplemented

    def validate_delete_condition(self, user_cred, res1, res2):
        return ''

    def validate_update_data(self, user_cred, kwargs, res1, res2):
        return ''

    @classmethod
    def validate_create_data(cls, user_cred, owner_cred, kwargs, res1, res2):
        return ''


class VirtualResourceBase(StandaloneResourceBase):
    """ Base class for standalone resource that is virtual """

    __abstract__ = True

    status = Column(VARCHAR(16, charset='ascii'), nullable=False, default='init')

    # backend_id = Column(VARCHAR(36, charset='ascii'), nullable=False)

    tenant_id  = Column(VARCHAR(36, charset='ascii'), nullable=False)
    user_id    = Column(VARCHAR(36, charset='ascii'), nullable=False)

    is_system = Column(Boolean, nullable=True, default=False)

    @classmethod
    def list_fields(cls, user_cred):
        fields = super(VirtualResourceBase, cls).list_fields(user_cred)
        fields.extend(['id', 'name'])
        if user_cred is not None and user_cred.is_system_admin():
            fields.extend(['tenant_id', 'user_id', 'is_system'])
        return fields

    @classmethod
    def detail_fields(cls, user_cred):
        fields = super(VirtualResourceBase, cls).detail_fields(user_cred)
        fields.extend(['id', 'name', 'description'])
        if user_cred is not None and user_cred.is_system_admin():
            fields.extend(['tenant_id', 'user_id', 'is_system'])
        return fields

    def is_owner(self, user_cred):
        if user_cred.is_system_admin() or \
            user_cred.user_id == self.user_id or \
            user_cred.tenant_id == self.tenant_id:
            return True
        else:
            return False

    def is_admin(self, user_cred):
        if user_cred.is_system_admin() or \
            user_cred.user_id == self.user_id or \
            (user_cred.tenant_id == self.tenant_id and user_cred.is_admin()):
            return True
        else:
            return False

    def get_owner_user_cred(self):
        return None
        # from wanka.common.auth import TokenCredential
        # return TokenCredential(None, self.tenant_id, None, self.user_id, None,
        #                                                     [], 0, False)

    @classmethod
    def allow_name_separator(cls):
        return True

    @classmethod
    def fetch_by_name(cls, name_str, user_cred):
        return cls.query() \
                    .filter(cls.name==name_str) \
                    .filter(cls.tenant_id==user_cred.tenant_id).first()

    @classmethod
    def list_items_filter(cls, query, user_cred, data):
        query = super(VirtualResourceBase, cls).list_items_filter(query,
                                                            user_cred, data)
        if user_cred.is_system_admin() and data.get('admin', False):
            tenant = data.get('tenant', None)
            if tenant is not None:
                from wanka.models.tenantcache import TenantCache
                tcache = TenantCache.fetch_by_id_or_name(tenant)
                if tcache is not None:
                    query = query.filter(cls.tenant_id==tcache.id)
                else:
                    raise HTTPError(404, 'Tenant %s not found' % tenant)
            user = data.get('user', None)
            if user is not None:
                from wanka.models.usercache import UserCache
                ucache = UserCache.fetch_by_id_or_name(user)
                if ucache is not None:
                    query = query.filter(cls.user_id==ucache.id)
                else:
                    raise HTTPError(404, 'User %s not found' % user)
            is_system = boolutils.to_bool(data.get('system', False))
            if not is_system:
                query = query.filter(or_(cls.is_system==None,
                                        cls.is_system==False))
        else:
            query = query.filter(cls.tenant_id==user_cred.tenant_id) \
                            .filter(or_(cls.is_system==None,
                                        cls.is_system==False))
        return query

    @classmethod
    def is_new_name_unique(cls, name_str, user_cred, kwargs):
        if cls.query().filter(cls.name==name_str) \
                    .filter(cls.tenant_id==user_cred.tenant_id).count() == 0:
            return True
        return False

    def is_alter_name_unique(self, name_str, user_cred, kwargs):
        if self.__class__.query().filter(self.__class__.name==name_str) \
                    .filter(self.__class__.id!=self.id) \
                    .filter(self.__class__.tenant_id==user_cred.tenant_id) \
                    .count() == 0:
            return True
        return False

    @classmethod
    def validate_create_data(cls, user_cred, owner_cred, kwargs):
        if kwargs.get('is_system', False) == True and \
                not user_cred.is_system_admin():
            return 'Non-admin user not allowed to create system object'
        return super(VirtualResourceBase, cls) \
                    .validate_create_data(user_cred, owner_cred, kwargs)

    def customize_create(self, user_cred, owner_cred, kwargs):
        if owner_cred is not None:
            cred = owner_cred
        else:
            cred = user_cred
        self.tenant_id = cred.tenant_id
        self.user_id   = cred.user_id
        self.is_system = (kwargs.get('is_system', False)==True)
        return super(VirtualResourceBase, self).customize_create(user_cred,
                        owner_cred, kwargs)

    def is_system_resource(self):
        return (self.is_system == True)

    @classmethod
    def allow_list_items(cls, user_cred, qsvars, ctx_obj=None):
        if qsvars.get('admin', False) and not user_cred.is_system_admin():
            return False
        return True

    def allow_get_details(self, user_cred):
        return self.is_owner(user_cred)

    @classmethod
    def allow_create_item(cls, user_cred, ctx_obj=None):
        return True

    def allow_update_item(self, user_cred):
        return self.is_owner(user_cred)

    def allow_delete_item(self, user_cred):
        return self.is_owner(user_cred)

    def allow_perform_status(self, user_cred, status=None):
        return user_cred.is_system_admin()

    def allow_get_details_metadata(self, user_cred, field=None):
        return self.is_owner(user_cred)

    def allow_perform_metadata(self, user_cred, **kwargs):
        return self.is_owner(user_cred)

    def perform_status(self, user_cred, status=None):
        if status is not None and self.status != status:
            self.set_status(status)
        return ''

    def get_tenant_cache(self):
        # from wanka.models.tenantcache import TenantCache
        # return TenantCache.raw_fetch(self.tenant_id)
        return None

    def get_user_cache(self):
        # from wanka.models.usercache import UserCache
        # return UserCache.raw_fetch(self.user_id)
        return None

    def get_customize_columns(self, user_cred, kwargs):
        ret = super(VirtualResourceBase, self) \
                    .get_customize_columns(user_cred, kwargs)
        if user_cred.is_system_admin():
            tc = self.get_tenant_cache()
            if tc is not None:
                ret['tenant'] = tc.get_name()
            uc = self.get_user_cache()
            if uc is not None:
                ret['user'] = uc.get_name()
        return ret

    def get_details(self, user_cred, kwargs):
        kwvals = super(VirtualResourceBase, self) \
                    .get_details(user_cred, kwargs)
        if user_cred.is_system_admin():
            tc = self.get_tenant_cache()
            if tc is not None:
                kwvals['tenant'] = tc.get_name()
            uc = self.get_user_cache()
            if uc is not None:
                kwvals['user'] = uc.get_name()
        return kwvals

    def allow_perform_change_owner(self, user_cred, tenant=None, user=None):
        if user_cred.is_system_admin():
            return True
        else:
            return False

    def perform_change_owner(self, user_cred, tenant=None, user=None):
        # from wanka.models.tenantcache import TenantCache
        # tc = TenantCache.fetch_by_id_or_name(tenant)
        # if tc is None:
        #     return 'Cannot find tenant %s' % tenant
        # from wanka.models.usercache import UserCache
        # uc = UserCache.fetch_by_id_or_name(user)
        # if uc is None:
        #     return 'Cannot find user %s' % user
        # cls = self.__class__
        # name_dup_count = cls.query().filter(cls.name==self.name) \
        #                         .filter(cls.tenant_id==tc.id) \
        #                         .filter(cls.id!=self.id).count()
        # if name_dup_count > 0:
        #     return 'Duplicate name %s found' % self.name
        # self.tenant_id = tc.id
        # self.user_id = uc.id
        # self.save_updates()

        # ignore meter, let meter do change owner independently
        # from wanka.common import meterclient
        # meterclient.get_client().sync_owner(user_cred, self)
        return ''


class SharableVirtualResourceBase(VirtualResourceBase):
    """ Base class for sharable virtual resources, like disk and network """

    __abstract__ = True

    is_public = Column(Boolean, default=False, nullable=False)

    @classmethod
    def list_fields(cls, user_cred):
        fields = super(SharableVirtualResourceBase, cls).list_fields(user_cred)
        fields.extend(['is_public'])
        return fields

    @classmethod
    def detail_fields(cls, user_cred):
        fields = super(SharableVirtualResourceBase, cls).detail_fields(user_cred)
        fields.extend(['is_public'])
        return fields

    def allow_get_details(self, user_cred):
        return self.is_owner(user_cred) or self.is_public

    @classmethod
    def list_items_filter(cls, query, user_cred, data):
        if not user_cred.is_system_admin():
            return query.filter(or_(cls.tenant_id==user_cred.tenant_id,
                                    cls.is_public==True))
        else:
            return super(SharableVirtualResourceBase, cls) \
                        .list_items_filter(query, user_cred, data)

    def allow_perform_public(self, user_cred):
        return self.is_owner(user_cred)

    def allow_perform_private(self, user_cred):
        return self.is_owner(user_cred)

    def perform_public(self, user_cred):
        if not self.is_public:
            self.is_public = True
            self.save_updates()
        return ''

    def perform_private(self, user_cred):
        if self.is_public:
            self.is_public = False
            self.save_updates()
        return ''

    @classmethod
    def fetch_by_name(cls, name_str, user_cred):
        return cls.query() \
                    .filter(cls.name==name_str) \
                    .filter(or_(cls.tenant_id==user_cred.tenant_id,
                                    cls.is_public==True)).first()

    @classmethod
    def is_new_name_unique(cls, name_str, user_cred, kwargs):
        if cls.query().filter(cls.name==name_str) \
                    .filter(or_(cls.tenant_id==user_cred.tenant_id,
                                    cls.is_public==True)).count() == 0:
            return True
        return False

    def is_alter_name_unique(self, name_str, user_cred, kwargs):
        if self.__class__.query().filter(self.__class__.name==name_str) \
                    .filter(self.__class__.id!=self.id) \
                    .filter(or_(self.tenant_id==user_cred.tenant_id,
                                    self.is_public==True)) \
                    .count() == 0:
            return True
        return False


class AdminSharableVirtualInfoBase(SharableVirtualResourceBase):
    """ Base class for sharable virtual resources, like secgroups and dns """

    __abstract__ = True
    _RECORDS_SEPARATOR_ = ';'

    def allow_perform_public(self, user_cred):
        return user_cred.is_system_admin()

    def allow_perform_private(self, user_cred):
        return user_cred.is_system_admin()

    @classmethod
    def get_info_field_name(cls):
        return NotImplemented

    @classmethod
    def parse_input_info(cls, kwargs):
        return NotImplemented

    @classmethod
    def validate_create_data(cls, user_cred, owner_cred, data):
        records = cls.parse_input_info(data)
        data.setdefault(cls.get_info_field_name(),
                            cls._RECORDS_SEPARATOR_.join(records))
        return super(AdminSharableVirtualInfoBase, cls) \
                            .validate_create_data(user_cred, owner_cred, data)

    def get_info(self):
        info = getattr(self, self.get_info_field_name(), None)
        if info is not None and len(info) > 0:
            return info.split(self._RECORDS_SEPARATOR_)
        else:
            return []

    def set_info(self, records):
        setattr(self, self.get_info_field_name(),
                        self._RECORDS_SEPARATOR_.join(records))
        self.save_updates()

    def do_add_info(self, user_cred, kwargs):
        records = self.parse_input_info(kwargs)
        old_recs = self.get_info()
        adds = []
        for r in records:
            if r not in old_recs:
                old_recs.append(r)
                adds.append(r)
        if len(adds) > 0:
            self.set_info(old_recs)
            from wanka.models.opslog import OpsLog
            OpsLog.log_event(self, OpsLog.ACT_UPDATE,
                                '%s+%s' % (self.get_info_field_name(), adds),
                                user_cred)
            return True
        else:
            return False

    def do_remove_info(self, user_cred, kwargs, allow_empty=True):
        records = self.parse_input_info(kwargs)
        old_recs = self.get_info()
        removes = []
        for r in records:
            if r in old_recs:
                old_recs.remove(r)
                removes.append(r)
        if len(old_recs) == 0 and not allow_empty:
            raise HTTPError(406, 'Not allow empty records')
        if len(removes) > 0:
            self.set_info(old_recs)
            from wanka.models.opslog import OpsLog
            OpsLog.log_event(self, OpsLog.ACT_UPDATE,
                                '%s-%s' % (self.get_info_field_name(), removes),
                                user_cred)
            return True
        else:
            raise HTTPError(404, 'Not found')
'''


def is_db_connection_error(args):
    """Return True if error in connecting to db."""
    # NOTE(adam_g): This is currently MySQL specific and needs to be extended
    #               to support Postgres and others.
    conn_err_codes = ('2002', '2003', '2006')
    for err_code in conn_err_codes:
        if args.find(err_code) != -1:
            return True
    return False


def wrap_db_error(f):
    """Retry DB connection. Copied from nova and modified."""
    def _wrap(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except sqlalchemy.exc.OperationalError, e:
            if not is_db_connection_error(e.args[0]):
                raise

            _MAX_RETRIES = 10
            _RETRY_INTERVAL = 10

            remaining_attempts = _MAX_RETRIES
            while True:
                logging.warning('SQL connection failed. %d attempts left.' %
                                remaining_attempts)
                remaining_attempts -= 1
                time.sleep(_RETRY_INTERVAL)
                try:
                    return f(*args, **kwargs)
                except sqlalchemy.exc.OperationalError, e:
                    if (remaining_attempts == 0 or
                            not is_db_connection_error(e.args[0])):
                        raise
                except sqlalchemy.exc.DBAPIError:
                    raise
        except sqlalchemy.exc.DBAPIError:
            raise
    _wrap.func_name = f.func_name
    return _wrap


__master_engine = None
__slave_engines = None


def mysql_checkin(dbapi_connection, connection_record):
    logging.debug("DB checkin...")


def mysql_checkout(dbapi_con, con_record, con_proxy):
    try:
        logging.debug("mysql_checkout: Ping MYSQL...")
        dbapi_con.cursor().execute('select 1')
    except dbapi_con.OperationalError, ex:
        if ex.args[0] in (2006, 2013, 2014, 2045, 2055):
            msg = 'Got mysql server has gone away: %s' % ex
            logging.warn(msg)
            raise sqlalchemy.exc.DisconnectionError(msg)
        else:
            raise


def _create_engine(desc):
    engine_args = {
                    'pool_recycle': 3600,
                    'pool_size': 5,
                    'echo': False,
                    'convert_unicode': True,
                    # 'listeners': [MySQLPingListener()],
                    }
    try:
        engine = create_engine(desc, **engine_args)
        event.listen(engine, 'checkin', mysql_checkin)
        event.listen(engine, 'checkout', mysql_checkout)
        engine.connect = wrap_db_error(engine.connect)
        engine.connect()
        return engine
    except Exception as e:
        logging.error("Error connect to db engine: %s" % e)
        raise

wanka_engine = _create_engine('mysql://root:yestem@localhost:3306/test?charset=utf8')
#wanka_engine = _create_engine('mysql://root:yestem@localhost:3306/mysql?charset=utf8')
#wanka_engine = _create_engine('mysql://root:1234@127.0.0.1:3306/mysql?charset=utf8')

def _get_master_engine():
    global __master_engine
    if __master_engine is None:
        __master_engine = _create_engine('mysql://root:yestem@localhost:3306/mysql?charset=utf8')
        #__master_engine = _create_engine('mysql://root:1234@127.0.0.1:3306/mysql?charset=utf8')
    # logging.info("Using master db")
    return __master_engine


def _get_slave_engine():
    global __master_engine, __slave_engines
    if options.sql_slaves is not None:
        if __slave_engines is None:
            __slave_engines = []
            for desc in options.sql_slaves:
                __slave_engines.append(_create_engine(desc))
        index = random.randint(0, len(__slave_engines) - 1)
        # logging.info("Using slave db at (%d)", index)
        return __slave_engines[index]
    else:
        # logging.info("No slaves. Using master db")
        return _get_master_engine()


class RoutingSession(Session):

    def get_bind(self, mapper=None, clause=None):
        if self._use_engine == 'master':
            return _get_master_engine()
        elif self._use_engine == 'slave':
            return _get_slave_engine()
        elif self._flushing:
            return _get_master_engine()
        else:
            return _get_slave_engine()

    _use_engine = None

    def master(self):
        s = RoutingSession()
        vars(s).update(vars(self))
        s._use_engine = 'master'
        return s

    def slave(self):
        s = RoutingSession()
        vars(s).update(vars(self))
        s._use_master = 'slave'
        return s


Session = scoped_session(sessionmaker(bind=wanka_engine,
                                    expire_on_commit=False,
                                    autoflush=False,
                                    autocommit=False))

_session_records = {}


def master_engine():
    return _get_master_engine()


def master_db():
    global Session, _session_records
    s = Session()
    _session_records[threadutils.get_thread_id()] = time.time()
    print "**",s
    print s.query
    print "dict",_session_records
    return s


def slave_db():
    global Session, _session_records
    s = Session().slave()
    _session_records[threadutils.get_thread_id()] = time.time()
    return s


def clean_db_session():
    global Session, _session_records
    tid = threadutils.get_thread_id()
    if tid in _session_records:
        Session.close()
        Session.remove()
        _session_records.pop(tid, None)
        #del _session_records[tid]


def check_db_session():
    global _session_records
    for k in _session_records.keys():
        v = _session_records.get(k, 0)
        # v = _session_records[k]
        # print 'check threading %d %d' % (k, v)
        if v > 0 and time.time() - v > 900:
            logging.error('Outstanding db session at thread %s' % k)


_db_check_task = None


def start_db_check_task():
    global _db_check_task
    if _db_check_task is None:
        from tornado.ioloop import PeriodicCallback
        _db_check_task = PeriodicCallback(check_db_session, 5000)
        _db_check_task.start()


def stop_db_check_task():
    global _db_check_task
    if _db_check_task is not None:
        _db_check_task.stop()
        _db_check_task = None


def init():
    """
    Database initialization
    """
    print "Database initialization ..."
    start_db_check_task()

def stop():
    """
    Database finalization
    """
    stop_db_check_task()

