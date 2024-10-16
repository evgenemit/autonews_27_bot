from typing import Callable, Awaitable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class AdminMiddleware(BaseMiddleware):
    """Проверка является ли пользователь администратором"""
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user = data.get('event_from_user')
        if user:
            user_id = user.id
        db = data.get('db')
        if db:
            is_admin = await db.is_admin(user_id)
            if is_admin:
                return await handler(event, data)
        return await data['bot'].send_message(
            user_id,
            'Недостаточно прав.'
        )
