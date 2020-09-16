import sqlite3
from parser_file import Image
import random


class SQLighter:

    def __init__(self, database='dbase.db'):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()
        self.image = Image()

    def get_photo_link(self, user_id):
        with self.connection:
            cat = self.cursor.execute("SELECT * FROM `subscriptions` WHERE `user_id` = ?",
                                      (user_id,)).fetchall()[0][4]
            photo_link_array = self.cursor.execute("SELECT * FROM `photo_links` WHERE `category` = ?",
                                      (cat,)).fetchall()
            number = random.randint(0, len(photo_link_array)-1)
            photo_link = photo_link_array[number][1]

            return photo_link

    def update_category(self, user_id, category):
        with self.connection:
            return self.cursor.execute("UPDATE `subscriptions` SET `category` = ? WHERE `user_id` = ?",
                                       (category, user_id))

    def fill_photo_links(self):
        for category in self.image.get_categories():
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
