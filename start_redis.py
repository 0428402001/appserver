import datetime
import redis
import json
from models.base_orm import Session
from models.content_auth import ContentAuth





pool = redis.ConnectionPool(host='localhost', port=6379, db=0)#db = 0 used to cache the content_auth
r = redis.Redis(connection_pool=pool)


def get_map_field(single_session_result):
    fields = {}
    obj = single_session_result
    for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata' and x != 'count' and x != 'keys' and x != 'index' and x != "conjugate"]:
        data = obj.__getattribute__(field)
        if isinstance(data, datetime.datetime): 
            data=data.strftime('%Y-%m-%d') 
        elif isinstance(data, datetime.date): 
            data=data.strftime('%Y-%m-%d') 
        fields[field] = data
    return fields

clu = Session.query(ContentAuth).all()
for single_session_result in clu:
    auth_id = single_session_result.id
    map_field = {}
    map_field = get_map_field(single_session_result)
    r.hmset(auth_id, map_field)





