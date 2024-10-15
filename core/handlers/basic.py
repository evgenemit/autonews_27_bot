from aiogram import types
from aiogram.fsm.context import FSMContext

from core.keyboards import reply


async def start(msg: types.Message):
    """Команда /start"""
    await msg.answer(
        'Привет, этот бот должен помочь быстро создавать новости на сайте школы.',
        reply_markup=reply.main_keyboard()
    )


async def main_menu(msg: types.Message, state: FSMContext):
    """Главное меню"""
    await msg.answer('Меню', reply_markup=reply.main_keyboard())
