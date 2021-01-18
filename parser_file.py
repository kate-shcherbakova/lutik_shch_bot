import requests
from bs4 import BeautifulSoup as BS
import re
from urllib.parse import urlparse
import os.path


class Image:
    HOST = 'https://burst.shopify.com'
    URL = ''
    HEADERS = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'
    }
    img_links = []  # массив ссылок на картинки

    def __init__(self):
        pass

    # возвращает количество страниц в категории
    def get_number_of_pages(self, url):
        # url - https://burst.shopify.com/photos(category)
        r = requests.get(url, headers=self.HEADERS, params='')
        html = BS(r.content, 'html.parser')
        try:
            link = html.find('span', class_='last').find('a')['href']
            pages_number = re.search(r'(\d)+', link).group(0)
        except:
            pages_number = 1
        return int(pages_number)

    # возвращает массив из названий всех категорий '/food'
    def get_categories(self, url='https://burst.shopify.com/free-images'):
        result = self.parse(url, 'div', 'grid__item', 'div', 'tile', 'a', 'href')
        return result

    # парсит страницу по ссылке.
    '''
    self.parse(self.URL, 'div', 'grid__item', 'div', 'ratio-box', 'img', 'src')
    <div class="grid__item ...>
        <div class="ratio-box" ...>
            <img sizes="100vw" ...  
                src="https://burst.shopifycdn.com/photos/studying-alone.jpg?
    <div class="grid__item ...>
    Достанет массив из ссылок на картинки
    '''

    def parse(self, url, type1, class1, type2, class2, find1, find2):
        result = []
        r = requests.get(url, headers=self.HEADERS, params='')
        html = BS(r.content, 'html.parser')
        items = html.find_all(type1, class_=class1)
        for el in items:
            try:
                raw_link = el.find(type2, class_=class2).find(find1)[find2]
                if raw_link:
                    result.append(raw_link)
            except:
                pass
        return result

    # возвращает массив из ссылок на картинки со всех страниц категории
    def get_img_link(self, category='/photos'):
        self.URL = self.HOST + category
        pages = self.get_number_of_pages(self.URL)
        self.img_links = []
        self.img_links.clear()
        for page in range(pages):
            self.URL = self.HOST + category
            if page != 0:
                self.URL = self.URL + '?page=' + str(page + 1)

            raw_array = self.parse(self.URL, 'div', 'grid__item', 'div', 'ratio-box', 'img', 'src')
            for el in raw_array:
                link_of_img = re.match(r'https\:\/\/.*\.jpg', el)
                try:
                    self.img_links.append(link_of_img.group(0))
                except:
                    pass
        print(len(self.img_links))
        return self.img_links

    # создает файл, скачивает туда картинку по ее ссылке
    def download_img(self, link):
        r = requests.get(link, allow_redirects=True)
        a = urlparse(link)
        # разбивает ссылку на части
        # scheme='http', netloc='www.cwi.nl:80', path='остальное',params='', query='', fragment=''
        filename = os.path.basename(a.path)
        open(filename, 'wb').write(r.content)
        return filename

    # удаляет файл по его названию
    def remove_img(self, path):
        try:
            os.remove(path)
        except FileExistsError or FileNotFoundError:
            print('FILE ERROR')


test = Image()
print(test.get_categories())
#print(test.get_img_link('/holidays'))
