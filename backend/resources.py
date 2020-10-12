from contextvars import ContextVar

from aioredis import Redis
from databases import Database

__all__ = ['resources', ]


class Resources:
    def __init__(self) -> None:
        self.ctx_db: ContextVar[Database] = ContextVar('db')
        self.ctx_cache: ContextVar[Redis] = ContextVar('cache')

    @property
    def db(self) -> Database:
        return self.ctx_db.get()

    @property
    def cache(self):
        return self.ctx_cache.get()


resources = Resources()
