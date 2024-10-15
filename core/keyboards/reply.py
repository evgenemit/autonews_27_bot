from datetime import datetime

from aiogram.utils.keyboard import ReplyKeyboardBuilder


def main_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.button(text='Создать новость')
    kb.button(text='По цепочке')
    kb.adjust(1)
    return kb.as_markup(
        input_field_placeholder='Выберите действие',
        resize_keyboard=True
    )


def date_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.button(text=datetime.now().strftime('%d.%m.%Y'))
    kb.button(text='Отмена')
    kb.adjust(1)
    return kb.as_markup(
        input_field_placeholder='дд.мм.гггг',
        resize_keyboard=True
    )


def cancle_keyboard(placeholder: str = ''):
    kb = ReplyKeyboardBuilder()
    kb.button(text='Отмена')
    return kb.as_markup(
        input_field_placeholder=placeholder,
        resize_keyboard=True
    )


def circle_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.button(text='Загрузить в классификатор')
    kb.button(text='Отмена')
    kb.adjust(1)
    return kb.as_markup(
        resize_keyboard=True
    )
