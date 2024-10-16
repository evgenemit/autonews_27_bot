from aiogram import Router, F
from aiogram.filters.command import Command

from core.handlers import basic, news
from core.states.news_states import NewsStates, CircleStates


core_router = Router()

core_router.message.register(basic.start, Command('start'))
core_router.message.register(basic.main_menu, F.text == 'Отмена')
core_router.message.register(news.create_news, F.text == 'Создать новость')
core_router.message.register(news.circle_start, F.text == 'По цепочке')
core_router.message.register(news.get_news_url, NewsStates.GET_NEWS_URL)
core_router.message.register(news.get_news_title, NewsStates.GET_NEWS_TITLE)
core_router.message.register(news.get_news_date, NewsStates.GET_NEWS_DATE)
core_router.message.register(news.get_circle, CircleStates.GET_CIRCLE)
core_router.message.register(news.get_images, CircleStates.GET_IMAGES)
core_router.message.register(news.circle_load_images, CircleStates.LOAD_IMAGES)
