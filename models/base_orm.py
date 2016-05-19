import logging
#from json import json_util
import json


from sqlalchemy import event
from sqlalchemy.dialects.mysql import VARCHAR
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm import scoped_session, sessionmaker, Session, object_mapper
from sqlalchemy.types import TypeDecorator
import sqlalchemy


import datetime 

BASEOBJ = declarative_base()


def change_to_json(session_result):
    Hosts = []
    for obj in session_result:
        fields = {}
        #for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata' ]:
        for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata' and x != 'count' and x != 'keys' and x != 'index' and x != "conjugate"]:
            data = obj.__getattribute__(field)

            if isinstance(data, datetime.datetime): 
                data=data.strftime('%Y-%m-%d %H:%M:%S') 
            elif isinstance(data, datetime.date): 
                data=data.strftime('%Y-%m-%d %H:%M:%S') 

            fields[field] = data
        Hosts.append(fields)
    if len(Hosts) == 1 :
        Hosts = Hosts[0]
    res_json = json.dumps(Hosts)
    #res_json = json.dumps(Hosts, default=date_handler, check_circular=False)
    return res_json 



def change_to_json_1(session_result):
    Hosts = []
    for obj in session_result:
        fields = {}
        #for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata' ]:
        for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata' and x != 'count' and x != 'keys' and x != 'index' and x != "conjugate"]:
            data = obj.__getattribute__(field)

            if isinstance(data, datetime.datetime): 
                data=data.strftime('%Y-%m-%d %H:%M:%S') 
            elif isinstance(data, datetime.date): 
                data=data.strftime('%Y-%m-%d %H:%M:%S') 

            fields[field] = data
        Hosts.append(fields)
    res_json = json.dumps(Hosts)
    #res_json = json.dumps(Hosts, default=date_handler, check_circular=False)
    return res_json 






def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj

def change_to_json_2(clu):
    res_json =  json.dumps(clu, cls=new_alchemy_encoder(), check_circular=False, default=date_handler)
    return res_json



def new_alchemy_encoder():
    _visited_objs = []
    class AlchemyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj.__class__, DeclarativeMeta):
                # don't re-visit self
                if obj in _visited_objs:
                    return None
                _visited_objs.append(obj)

                # an SQLAlchemy class
                fields = {}
                for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                    data = obj.__getattribute__(field)
                    try:
                        if isinstance(data, datetime.date): 
                            data=data.strftime('%Y-%m-%d %H:%M:%S') 
                        if isinstance(data, datetime.datetime): 
                            data=data.strftime('%Y-%m-%d %H:%M:%S') 

                        json.dumps(data) # this will fail on non-encodable values, like other classes
                        fields[field] = data
                    except TypeError:
                        fields[field] = None
                return fields
            return json.JSONEncoder.default(self, obj)
    return AlchemyEncoder


class ModelBase(BASEOBJ):

    __abstract__ = True
    __table_args__ = {'mysql_engine': 'InnoDB'}
    __table_initialized__ = False



   # @classmethod
   # def query_to_list(cls, user_cred, q, kwargs):
   #     retlist = []
   #     for row in q.all():
   #         item = {}
   #         for k in cls.list_fields(user_cred):
   #             if k=='name':
   #                 c = row.get_name()
   #             else:
   #                 c = getattr(row, k, None)
   #             if c is not None:
   #                 if isinstance(c, datetime.datetime):
   #                     item[k] = timeutils.isotime(c)
   #                 else:
   #                     item[k] = c
   #         if 'details' not in kwargs or kwargs['details'] in ['True', True]:
   #             func = getattr(row, 'get_customize_columns', None)
   #             if func is not None and callable(func):
   #                 new_item = func(user_cred, kwargs)
   #             else:
   #                 new_item = None
   #             if new_item is not None and len(new_item) > 0:
   #                 for k in new_item:
   #                     item[k] = new_item[k]
   #         retlist.append(item)
   #     return retlist



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


def _create_engine(desc):
    engine_args = {
                    'pool_recycle': 3600,
                    'pool_size': 5,
                    #'echo': True,
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



wanka_engine = _create_engine('mysql://collegedaily:Zhuoxing1989@rdskhmm9d27q0t1etbxsfpublic.mysql.rds.aliyuncs.com:3306/collapp?charset=utf8')
#wanka_engine = _create_engine('mysql://root:yestem@localhost:3306/mysql?charset=utf8')

Session = scoped_session(sessionmaker(bind=wanka_engine,
                                    expire_on_commit=False,
                                    autoflush=False,
                                    autocommit=False))


