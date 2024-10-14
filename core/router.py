from aiogram import Router, F
from aiogram.filters.command import Command

from core.handlers import basic, news
from core.states.news_states import NewsCreationStates


core_router = Router()

core_router.message.register(basic.start, Command('start'))
core_router.message.register(news.create_news, F.text == 'Создать новость')
core_router.message.register(news.get_news_url, NewsCreationStates.GET_NEWS_URL)
core_router.message.register(news.get_news_title, NewsCreationStates.GET_NEWS_TITLE)
core_router.message.register(news.get_news_date, NewsCreationStates.GET_NEWS_DATE)
