import config
# импортируем файл с Api Token бота
from parser_file import Image
# импортируем файл парсера
import logging
# 1 - мы импортируем встроенную библиотеку logging
# для того чтобы вышло сообщение с юзернеймом бота (в нашем случае, только для этого)
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
p = Image()
name_of_cat = p.get_categories()  # 50
length_of_block = len(name_of_cat) // 4  # 12
n_of_blocks = 4 + bool(len(name_of_cat) % 4)  # 5


def edit_category_name(category_name):
    category_name = category_name.strip('/')
    category_name = category_name.replace('-', ' ')
    category_name = category_name.capitalize()
    return category_name


# команда активации подписки
@dp.message_handler(commands=['subscribe'])
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


# пасхалка
@dp.message_handler(commands=['misha'])
async def misha(message: types.Message):
    await message.answer('Удачной тренировки!')


# команда создания ReplyKeyboardMarkup
def reply(text):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    item = KeyboardButton(text)
    markup.add(item)
    return markup


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
        markup_item2 = InlineKeyboardButton('Показать ещё', callback_data='/show_more')
        markup.add(markup_item2)

    return markup


# команда отображения всех категорий with inline keyboard
@dp.message_handler(commands=['categories'])
async def categories(message: types.Message):
    markup = create_block(5)
    await message.answer('Выберите категорию фото:', reply_markup=markup)
    # await message.answer('...', reply_markup=reply('Показать еще'))
    # print(message.message_id, message.text)
    # await bot.delete_message(message.chat.id, message.message_id + 2)


# команда обработки нажатия на кнопку inline keyboard
@dp.callback_query_handler(lambda callback_query: True)
async def reply_to_button(call: types.CallbackQuery):
    try:
        cat = call.data
        dbase.update_category(call.from_user.id, cat)
    except Exception as exc:
        print('ERROR' + repr(exc))


# команда отписки
@dp.message_handler(commands=['unsubscribe'])
async def unsubscribe(message: types.Message):
    if not dbase.subscriber_exists(message.from_user.id) or not dbase.status(message.from_user.id):
        dbase.add_subscriber(message.from_user.id, message.from_user.username, False)
        await message.answer("Вы итак не подписаны")
    else:
        dbase.update_subscription(message.from_user.id, False)
        await message.answer("Вы отписаны от рассылки")


# команда проверки статуса
@dp.message_handler(commands=['status'])
async def status(message: types.Message):
    if dbase.status(message.from_user.id):
        await message.answer("Вы подписаны")
    else:
        await message.answer("Вы не подписаны")


# команда старт
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Привет {0}!".format(message.from_user.first_name))
    await message.answer(
        "Вот мои команды:\n/start - начало работы бота\n/categories - показать все категории\n/photo - получить фото\n/subscribe - подписаться на рассылку\n/unsubscribe - отписаться от рассылки\n/status - проверить статус подписки" \
            .format(message.from_user.first_name))


# команда отправки фото
@dp.message_handler(commands=['photo'])
async def photo(message: types.Message):
    p = Image()
    # link - ссылка на картинку .jpg
    link = p.get_img_link()
    filename = p.download_img(link)
    with open(filename, 'rb') as photo:
        await bot.send_photo(
            message.from_user.id,
            photo,
            caption='PICTURE',
            disable_notification=True
        )
        p.remove_img(filename)


# хэндлер для принятия остальных сообщений
@dp.message_handler()
async def smth(message: types.Message):
    await message.answer("Я не знаю этой команды (")


if __name__ == '__main__':
    # лонг поллинг
    executor.start_polling(dp, skip_updates=True)
