import aiohttp
import aiofiles
import aiofiles.os
from environs import Env
from aiogram import types, Bot
from aiogram.fsm.context import FSMContext

from core.states.news_states import NewsCreationStates
from core.services.database import Database
from core.services.autonews import AutoNews
from core.services.logs import add_logs
from core.keyboards import reply


async def create_news(msg: types.Message, state: FSMContext):
    """Удаляет старые изображения из ./data и запрашивает telegram пост"""
    if not await aiofiles.os.path.exists('data/'):
        await aiofiles.os.mkdir('data')
    for file_path in await aiofiles.os.listdir('data'):
        await aiofiles.os.remove(f'data/{file_path}')

    await msg.answer(
        'Пост из канала: ',
        reply_markup=reply.cancle_keyboard('Перешли пост из канала')
    )
    await state.set_state(NewsCreationStates.GET_NEWS_URL)


async def get_news_url(msg: types.Message, bot: Bot,  state: FSMContext):
    """Загружает изображения и текст из telegram поста"""
    env = Env()
    env.read_env('.env')
    token = env.str('TOKEN')
    if msg.caption:
        await state.update_data({'caption': msg.caption})
        await msg.answer('Заголовок: ')
        await state.set_state(NewsCreationStates.GET_NEWS_TITLE)
    if msg.photo:
        photo = msg.photo[-1]
        file_path = (await bot.get_file(photo.file_id)).file_path
        file_url = f'https://api.telegram.org/file/bot{token}/{file_path}'

        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as response:
                files_count = len(await aiofiles.os.listdir('data'))
                file_name = f'data/{files_count + 1}.jpg'
                async with aiofiles.open(file_name, mode='wb') as f:
                    await f.write(await response.read())


async def get_news_title(msg: types.Message, state: FSMContext):
    """Сохраняет заголовок новости и запрашивает дату"""
    await state.update_data({'title': msg.text})
    await msg.answer('Дата:', reply_markup=reply.date_keyboard())
    await state.set_state(NewsCreationStates.GET_NEWS_DATE)


async def get_news_date(msg: types.Message, state: FSMContext):
    """Создаёт новость"""
    data = await state.get_data()
    images_count = len(await aiofiles.os.listdir('data'))
    await msg.answer(
        f'Создание новости\nКоличество картинок: {images_count}',
        reply_markup=types.ReplyKeyboardRemove()
    )

    async with AutoNews() as an:
        try:
            res = await an.create_news(
                images_count,
                data.get('caption'),
                data.get('title'),
                msg.text
            )
        except Exception as e:
            res = {'status': False, 'message': f'Ошибка. {e}'}
            await add_logs(f'Error {e}')
            raise e
    if res['status']:
        await msg.answer('Успешно создано')
    else:
        await msg.answer(f'Ошибка создания: {res["message"]}')
    await msg.answer('Меню', reply_markup=reply.main_keyboard())
    await state.clear()
