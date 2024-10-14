from aiogram.fsm.state import State, StatesGroup


class NewsCreationStates(StatesGroup):
    """Создание новости"""
    GET_NEWS_URL = State()
    GET_NEWS_TITLE = State()
    GET_NEWS_DATE = State()
