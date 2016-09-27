#used for redis connect_pool
import redis


#redis_r_0 = redis.Redis(connection_pool=conn_pool_0)
conn_pool_blog = redis.ConnectionPool(host='localhost', port=6379, db=0)
#redis_r_blog = redis.Redis(connection_pool=conn_pool_blog)

conn_pool_relate_blog = redis.ConnectionPool(host='localhost', port=6379, db=1)
#redis_r_relate_blog = redis.Redis(connection_pool=conn_pool_relate_blog)

conn_pool_home_page_blog_index = redis.ConnectionPool(host='localhost', port=6379, db=2)

conn_pool_home_page_blog = redis.ConnectionPool(host='localhost', port=6379, db=3)

conn_pool_hot_category = redis.ConnectionPool(host='localhost', port=6379, db=4)

conn_pool_hot_blog = redis.ConnectionPool(host='localhost', port=6379, db=5)


conn_pool_test = redis.ConnectionPool(host='localhost', port=6379, db=6)


conn_pool_blog_content = redis.ConnectionPool(host='localhost', port=6379, db=6)
