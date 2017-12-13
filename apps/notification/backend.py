import redis
from django.conf import settings
from kombu.utils import cached_property


class RedisBackend(object):
    redis = redis
    max_connections = None

    def __init__(self, host='localhost', port=6379, db=0, password=None,
                 expires=None, max_connections=None, url=None,
                 connection_pool=None):
        self.max_connections = (
            max_connections or self.max_connections
        )
        self._ConnectionPool = connection_pool

        self.connparams = {
            'host': getattr(settings, 'NOTIFICATION_REDIS_HOST', host),
            'port': getattr(settings, 'NOTIFICATION_REDIS_PORT', port),
            'db': getattr(settings, 'NOTIFICATION_REDIS_DB', db),
            'password': getattr(settings, 'NOTIFICATION_REDIS_PASSWORD', password),
            'max_connections': getattr(settings, 'NOTIFICATION_REDIS_MAX_CONNECTIONS', self.max_connections),
        }
        self.url = url
        self.expires = expires

    def get(self, key):
        return self.client.get(key)

    def mget(self, keys):
        return self.client.mget(keys)

    def sadd(self, key, value):
        return self.client.sadd(key, value)

    def smembers(self, key):
        return self.client.smembers(key)

    def srem(self, key, values):
        return self.client.srem(key, values)

    def set(self, key, value, ex=None, px=None, nx=False, xx=False):
        return self.client.set(key, value, ex, px, nx, xx)

    def expire(self, key, time):
        return self.client.expire(key, time)

    def scan_iter(self, match):
        return self.client.scan_iter(match)

    def delete(self, keys):
        return self.client.delete(keys)

    def _create_client(self, socket_timeout=None, socket_connect_timeout=None,
                       **params):
        return self._new_redis_client(
            socket_timeout=socket_timeout and float(socket_timeout),
            socket_connect_timeout=socket_connect_timeout and float(
                socket_connect_timeout), **params
        )

    def _new_redis_client(self, **params):
        return self.redis.Redis(connection_pool=self.ConnectionPool(**params))

    @property
    def ConnectionPool(self):
        if self._ConnectionPool is None:
            self._ConnectionPool = self.redis.ConnectionPool
        return self._ConnectionPool

    @cached_property
    def client(self):
        return self._create_client(**self.connparams)
