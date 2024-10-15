import emoji
import time
import aiofiles
import aiofiles.os
from aiogram import types, Bot
from aiogram.fsm.context import FSMContext

from core.states.news_states import NewsCreationStates, CircleStates
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
    if msg.caption:
        await state.update_data({'caption': msg.caption})
        await msg.answer(
            'Заголовок: ',
            reply_markup=reply.cancle_keyboard('Заголовок новости')
        )
        await state.set_state(NewsCreationStates.GET_NEWS_TITLE)
    if msg.photo:
        file_name = f'data/{str(time.time()).replace('.', '')}.jpg'
        await bot.download(file=msg.photo[-1].file_id, destination=file_name)


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
        await msg.answer(
            f'{emoji.emojize(":green_circle:")} <b>Успешно создано</b>'
        )
    else:
        await msg.answer(
            f'{emoji.emojize(":red_circle:")} <b>{res["message"]}</b>'
        )
    await msg.answer('Меню', reply_markup=reply.main_keyboard())
    await state.clear()


async def circle_start(msg: types.Message, state: FSMContext):
    """Запрашивает цепочку классификаторов"""
    if not await aiofiles.os.path.exists('data/'):
        await aiofiles.os.mkdir('data')
    for file_path in await aiofiles.os.listdir('data'):
        await aiofiles.os.remove(f'data/{file_path}')
    await msg.answer(
        'Цепочка классификаторв (разедлитель ", ")',
        reply_markup=reply.cancle_keyboard('Актуально, Сервисы')
    )
    await state.set_state(CircleStates.GET_CIRCLE)


async def get_circle(msg: types.Message, state: FSMContext):
    """Сохраняет цепочку классификаторов и запрашивает изображения"""
    await state.update_data({'circle': msg.text.split(', ')})
    await msg.answer(
        'Изображения',
        reply_markup=reply.cancle_keyboard('Отправь картинки')
    )
    await state.set_state(CircleStates.GET_IMAGES)


async def get_images(msg: types.Message, bot: Bot, state: FSMContext):
    """Сохраняет изображения"""
    if msg.photo:
        file_name = f'data/{str(time.time()).replace('.', '')}.jpg'
        await bot.download(file=msg.photo[-1].file_id, destination=file_name)
    await msg.answer(
        'Загружено',
        reply_markup=reply.circle_keyboard()
    )
    await state.set_state(CircleStates.LOAD_IMAGES)


async def circle_load_images(msg: types.Message, state: FSMContext):
    """Загружает изображения в классификатор по цепочке"""
    data = await state.get_data()
    images_count = len(await aiofiles.os.listdir('data'))
    async with AutoNews() as an:
        try:
            res = await an.circle(
                data.get('circle'),
                images_count
            )
        except Exception as e:
            res = {'status': False, 'message': f'Ошибка. {e}'}
            await add_logs(f'Error {e}')
            raise e
    if res['status']:
        await msg.answer(
            f'{emoji.emojize(":green_circle:")} <b>Успешно загружено</b>'
        )
    else:
        await msg.answer(
            f'{emoji.emojize(":red_circle:")} <b>{res["message"]}</b>'
        )
    await msg.answer(
        'Меню',
        reply_markup=reply.main_keyboard()
    )
    await state.clear()
