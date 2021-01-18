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
            number = random.randint(0, len(photo_link_array) - 1)
            photo_link = photo_link_array[number][1]

            return photo_link

    def update_category(self, user_id, category):
        with self.connection:
            return self.cursor.execute("UPDATE `subscriptions` SET `category` = ? WHERE `user_id` = ?",
                                       (category, user_id))

    def delete_category(self, category):
        with self.connection:
            return self.cursor.execute("DELETE FROM `photo_links` WHERE `category` = ?", (category,))

    def clear_dbase(self, table='sub_photo_links'):
        with self.connection:
            return self.cursor.execute("DELETE FROM {0}".format(table))

    def fill_photo_links(self):
        for category in self.image.get_categories():
            count = 0
            print(category)
            for link in self.image.get_img_link(category):
                if not self.link_exists(link, category) and count < 100:
                    self.insert_photo_link(link, category)
                    count += 1

    def link_exists(self, link, category=''):
        with self.connection:
            if category == '':
                result = self.cursor.execute('SELECT * FROM `photo_links` WHERE `link` = ?', (link,)).fetchall()
                return bool(len(result))
            else:
                result = self.cursor.execute('SELECT * FROM `photo_links` WHERE `link` = ? AND `category` = ?',
                                             (link, category)).fetchall()
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

    def copy_sub_to_main(self):
        with self.connection:
            return self.cursor.execute("INSERT INTO `photo_links` SELECT * FROM `sub_photo_links`")


# test = SQLighter()
# test.fill_photo_links()
# test.clear_dbase()
'''
    def check_amount_of_links(self):
        with self.connection:
            for cat in self.cursor.execute("SELECT * FROM ``"):
                amount = self.cursor.execute("SELECT * FROM `photo_links` WHERE 'category' = ?",
                                         (cat,)).fetchall())
'''
# Если категории уже нет, но пользователь ее выбрал, то сбросить до /photos
# Сделать /photos
