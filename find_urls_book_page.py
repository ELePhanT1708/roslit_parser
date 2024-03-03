import logging

import bs4
import requests
import pandas as pd

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('roslit_parser')

EXCEL_PATH = "articuls.xlsx"


def get_link(block):
    try:
        return str(block.get('href'))
    except:
        return "ССЫЛКИ НЕТ"


def search_book_url(text: str):
    soup = bs4.BeautifulSoup(text, 'lxml')
    container = soup.css.select('a.product-item-image-wrapper[href]') or ["LINK NOT EXIST"]
    for block in container:
        return get_link(block)


class Client:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/109.0.0.0 Safari/537.36',
        }

    def search_page(self, articul: int) -> str:
        url = f'https://www.roslit.ru/catalog/?q={articul}&s='
        res = self.session.get(url=url)
        res.raise_for_status()
        return res.text

    def write_links(self, links):
        file = pd.read_excel(EXCEL_PATH)
        file['Ссылка'] = [f'https://www.roslit.ru{link}' for link in links]
        file.to_excel('Done.xlsx')
    @staticmethod
    def read_articuls():
        file = pd.read_excel(EXCEL_PATH)
        return file['Артикул']


if __name__ == '__main__':
    parser = Client()
    articuls = parser.read_articuls()
    links = []
    for articul in articuls:
        html_text = parser.search_page(articul)
        links.append(search_book_url(html_text))
    parser.write_links(links)

