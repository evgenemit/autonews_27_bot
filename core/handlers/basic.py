from aiogram import types

from core.keyboards import reply


async def start(msg: types.Message):
    """Команда /start"""

    await msg.answer(
        'Привет, этот бот должен помочь быстро создавать новости на сайте школы.',
        reply_markup=reply.main_keyboard()
    )
