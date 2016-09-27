import os
import time
import sys
nn = os.path.dirname('.')
mm = os.path.abspath('.')
tt = os.path.abspath(__file__)
kk = os.path.dirname(tt)
pp = os.path.dirname(kk)

sys.path.append(tt)
sys.path.append(kk)
sys.path.append(pp)
import redis_con_pool


file_dir=os.path.join(os.path.dirname(__file__), "/sync_cache.sh")
cmd_dir = "sh %s"%file_dir

while True:
    file_dir=os.path.join(os.path.dirname(__file__), "sync_cache.sh"),
    cmd_str = "sh %s"%file_dir
    os.system(cmd_str)
    print '%s\tflush_cache'%time.ctime()
    time.sleep(300)
