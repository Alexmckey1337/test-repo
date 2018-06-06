import multiprocessing
import os

bind = "0.0.0.0:5000"

worker_class = 'gevent'
workers = multiprocessing.cpu_count() * 2 + 1

chdir = '/app'

timeout = os.environ.get('WORKER_TIMEOUT', 30)

max_requests = 1000
max_requests_jitter = 100

accesslog = '-'
access_log_format = '%(L)s %(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
