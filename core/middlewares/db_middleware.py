import asyncpg
from typing import Callable, Awaitable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from core.services.database import Database


class DbSession(BaseMiddleware):
    def __init__(self, connection: asyncpg.pool.Pool):
        super().__init__()
        self.connection = connection

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        async with self.connection.acquire() as connect:
            data['db'] = Database(connect)
            return await handler(event, data)
