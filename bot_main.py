import schedule
import time
import config
# импортируем файл с Api Token бота
import asyncio
from parser_file import Image
# импортируем файл парсера
import logging
# 1 - мы импортируем встроенную библиотеку logging
# для того чтобы вышло сообщение с юзернеймом бота (в нашем случае, только для этого)
from datetime import datetime
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
# 2 - Мы импортируем объекты для работы бота
from sqlighter import SQLighter

logging.basicConfig(level=logging.INFO)
# 4 - Эта строчка кода необходима для выведения сообщения о работе нашего бота и его юзернейма.
bot = Bot(token=config.TOKEN)
# 5 - Здесь мы создаем основу бота, где указываем что его токен равен нашей переменной.
dp = Dispatcher(bot)
# 6 - Диспетчер. Понадобится для принятия будущих сообщений.
# инициализируем соединение с БД
dbase = SQLighter('dbase.db')

block_number = 0
picture = Image()
name_of_cat = picture.get_categories()  # 50
length_of_block = len(name_of_cat) // 4  # 12
n_of_blocks = 4 + bool(len(name_of_cat) % 4)  # 5
com = ['/📷Фото', '/☰Категории', '/☺Подписаться', '/😢Отписаться', '/❓Статус']


# возвращает Inline Keyboard - блок категорий под номером
def create_block(number):
    markup = InlineKeyboardMarkup(row_width=3)
    if number == 1:
        markup_item0 = InlineKeyboardButton('All photos', callback_data='/photos')
        markup.add(markup_item0)

    index = (number - 1) * length_of_block
    index2 = number * length_of_block
    if number == n_of_blocks:
        index2 = len(name_of_cat)
    while (index < index2):
        text1 = edit_category_name(name_of_cat[index])
        markup_item1 = InlineKeyboardButton(text1, callback_data=name_of_cat[index])
        text2 = edit_category_name(name_of_cat[index + 1])
        markup_item2 = InlineKeyboardButton(text2, callback_data=name_of_cat[index + 1])
        markup.add(markup_item1, markup_item2)
        index += 2

    if number != n_of_blocks:
        markup_item2 = InlineKeyboardButton('Показать ещё', callback_data='show_more')
        markup.add(markup_item2)

    return markup


# команда обработки нажатия на кнопку inline keyboard
@dp.callback_query_handler(lambda callback_query: True)
async def reply_to_button(call: types.CallbackQuery):
    try:
        if call.data == 'show_more':
            if config.global_number == n_of_blocks:
                config.global_number = 1
            else:
                config.global_number += 1
            markup = create_block(config.global_number)
            await bot.send_message(call.message.chat.id, 'Выберите категорию фото:', reply_markup=markup)
        else:
            cat = call.data
            dbase.update_category(call.from_user.id, cat)
            await bot.send_message(call.message.chat.id, 'Вы выбрали категорию {0}'.format(edit_category_name(cat)))
    except Exception as exc:
        print('ERROR' + repr(exc))


# /photo-cat.jpeg = Photo cat
def edit_category_name(category_name, flag=False):
    if flag:
        category_name = category_name.strip('.jpg')
    category_name = category_name.strip('/')
    category_name = category_name.replace('-', ' ')
    category_name = category_name.capitalize()
    return category_name


async def send_photo(user_id):
    # link - ссылка на картинку .jpg
    link = dbase.get_photo_link(user_id)
    filename = picture.download_img(link)
    try:
        with open(filename, 'rb') as photo:
            await bot.send_photo(
                user_id,
                photo,
                caption=edit_category_name(filename, True),
                disable_notification=True
            )
        picture.remove_img(filename)
    except:
        pass


async def send_smth(chat_id):
    await bot.send_message(chat_id=chat_id, text="HELLO")


# команда отправки фото
@dp.message_handler(commands=['📷Фото'])
async def photo(message: types.Message):
    a: types.Message
    a = await message.answer('Подожди немножко. Я ищу лучшее фото...')
    m_id = a.message_id
    await send_photo(message.from_user.id)
    await bot.delete_message(message.chat.id, m_id)


# команда старт
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    # создание ReplyKeyboardMarkup
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for command in com:
        item = KeyboardButton(command)
        markup.add(item)

    await message.answer("Привет {0}!".format(message.from_user.first_name))
    await message.answer(config.start_text.format(message.from_user.first_name), reply_markup=markup)


# команда отображения всех категорий with inline keyboard
@dp.message_handler(commands=['☰Категории'])
async def categories(message: types.Message):
    config.global_number = 1
    markup = create_block(config.global_number)
    await message.answer('Выберите категорию фото:', reply_markup=markup)


# команда активации подписки
@dp.message_handler(commands=['☺Подписаться'])
async def subscribe(message: types.Message):
    if not dbase.subscriber_exists(message.from_user.id):
        # если юзера нет в базе, добавляем его
        dbase.add_subscriber(message.from_user.id, message.from_user.username)
        await message.answer("Вы успешно подписаны на рассылку")
    elif dbase.status(message.from_user.id):
        # если он уже есть и подписан
        await message.answer("Вы итак подписаны")
    else:
        # если он уже есть но не подписан то обновляем статус подписки
        dbase.update_subscription(message.from_user.id, True)
        await message.answer("Вы успешно подписаны на рассылку")
    # user_id = message.from_user.id


# команда отписки
@dp.message_handler(commands=['😢Отписаться'])
async def unsubscribe(message: types.Message):
    if not dbase.subscriber_exists(message.from_user.id) or not dbase.status(message.from_user.id):
        dbase.add_subscriber(message.from_user.id, message.from_user.username, False)
        await message.answer("Вы итак не подписаны")
    else:
        dbase.update_subscription(message.from_user.id, False)
        await message.answer("Вы отписаны от рассылки")


# команда проверки статуса
@dp.message_handler(commands=['❓Статус'])
async def status(message: types.Message):
    if dbase.status(message.from_user.id):
        await message.answer("Вы подписаны")
    else:
        await message.answer("Вы не подписаны")


# хэндлер для принятия остальных сообщений
@dp.message_handler()
async def smth(message: types.Message):
    await message.answer("Я не знаю этой команды (")


if __name__ == '__main__':
    # лонг поллинг
    executor.start_polling(dp, skip_updates=True)
