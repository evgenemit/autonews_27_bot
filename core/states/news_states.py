from aiogram.fsm.state import State, StatesGroup


class NewsStates(StatesGroup):
    """Создание новости"""
    GET_NEWS_URL = State()
    GET_NEWS_TITLE = State()
    GET_NEWS_DATE = State()


class CircleStates(StatesGroup):
    GET_CIRCLE = State()
    GET_IMAGES = State()
    LOAD_IMAGES = State()
