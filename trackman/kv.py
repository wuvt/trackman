import redis


class KVStore(object):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.redis_conn = redis.from_url(app.config['REDIS_URL'])

    def info(self):
        return self.redis_conn.info()

    def delete(self, k):
        return self.redis_conn.delete(k)

    def expire(self, k, ttl):
        return self.redis_conn.expire(k, ttl)

    def get(self, k, cast=None):
        v = self.redis_conn.get(k)
        if v is None:
            return None
        elif cast == int:
            return int(v)
        elif cast == bool:
            if v == b"true" or v == b"True":
                return True
            else:
                return False
        else:
            return v

    def set(self, k, v):
        return self.redis_conn.set(k, v)
