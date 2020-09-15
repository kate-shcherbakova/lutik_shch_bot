import sqlite3
from parser_file import Image


class SQLighter:

    def __init__(self, database='dbase.db'):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()
        self.image = Image()

    def update_category(self, user_id, category):
        with self.connection:
            return self.cursor.execute("UPDATE `subscriptions` SET `category` = ? WHERE `user_id` = ?",
                                       (category, user_id))

    def fill_photo_links(self):
        for category in self.image.get_categories():
            if category != '/work-from-home' and category != '/business' and category != '/shop-local' and category != \
                    '/womens-day' and category != '/video-call-backgrounds' and category != \
                    '/female-photographer' and category != '/spring' and category != '/fashion' and category != \
                    '/feel-good-photos' and category != '/retail' and category != '/background' and category != \
                    '/landscape' and category != '/food' and category != '/urban-life' and category != \
                    '/work' and category != '/home' and category != '/accessories' and category != \
                    '/people' and category != '/flowers' and category != '/beauty' and category != \
                    '/money':
                for link in self.image.get_img_link(category):
                    if not self.link_exists(link):
                        self.insert_photo_link(link, category)

    def link_exists(self, link):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `photo_links` WHERE `link` = ?', (link,)).fetchall()
            return bool(len(result))

    def insert_photo_link(self, link, category):
        with self.connection:
            return self.cursor.execute("INSERT INTO `photo_links` (`link`, `category`) VALUES(?,?)", (link, category))

    def get_subscriptions(self, status=True):
        """Получаем всех активных подписчиков бота"""
        with self.connection:
            return self.cursor.execute("SELECT * FROM `subscriptions` WHERE `status` = ?", (status,)).fetchall()

    def subscriber_exists(self, user_id):
        """Проверяем, есть ли уже юзер в базе"""
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `subscriptions` WHERE `user_id` = ?', (user_id,)).fetchall()
            return bool(len(result))

    def status(self, user_id):
        if not self.subscriber_exists(user_id):
            return False
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `subscriptions` WHERE `user_id` = ?',
                                         (user_id,)).fetchall()[0][2]
            return bool(result)

    def add_subscriber(self, user_id, username, status=True):
        """Добавляем нового подписчика"""
        with self.connection:
            return self.cursor.execute("INSERT INTO `subscriptions` (`user_id`, `status`, 'username') VALUES(?,?,?)",
                                       (user_id, status, username))

    def update_subscription(self, user_id, status):
        """Обновляем статус подписки пользователя"""
        with self.connection:
            return self.cursor.execute("UPDATE `subscriptions` SET `status` = ? WHERE `user_id` = ?", (status, user_id))

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()

# test = SQLighter()
# test.fill_photo_links()
