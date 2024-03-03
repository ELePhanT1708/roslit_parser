import logging

import bs4
import requests
import json
import pandas as pd

EXCEL_PATH = 'URLS.xlsx'


def read_excel_articul():
    file = pd.read_excel(EXCEL_PATH)
    articuls = file['Артикул']
    return articuls


def read_excel_url():
    file = pd.read_excel(EXCEL_PATH)
    urls = file['Ссылка']
    return urls


def get_link(block):
    try:
        return str(block.get('href'))
    except:
        return "ССЫЛКИ НЕТ"


def get_title(text: str):
    soup = bs4.BeautifulSoup(text, 'lxml')
    container = soup.css.select('h1')
    print(container)
    if container:
        for title in container:
            return title.text


def get_image_urls(text: str):
    soup = bs4.BeautifulSoup(text, 'lxml')
    container = soup.css.select('div.product-item-detail-slider-controls-block')
    if container:
        links = []
        items = container[0].select('div.product-item-detail-slider-controls-image')
        for item in items:
            links.append(item.select('img')[0].get('src'))
        return [f'https://www.roslit.ru{link}' for link in links]
    else:  # One image case
        image_url = soup.css.select('div.product-item-detail-slider-image')
        for item in image_url:
            return f"https://www.roslit.ru{item.select('img')[0].get('src')}"


def get_properties(text: str):
    if text == "EMPTY LINK":
        return {}
    soup = bs4.BeautifulSoup(text, 'lxml')
    container = soup.css.select('li.product-item-detail-properties__item')
    properties = {
        "Автор": "",
        "Издательство": "",
        "Год издания": "",
        "Артикул": "",
        "Входит в УМК": "",
        "Федеральный перечень": "",
        "Класс": "",
        "Предмет": "",
        "Тип материала": "",
        "Учебная система": "",
        "Группа литературы": "",
        "Количество страниц": "",
        "Серия издательства": "",
        "ISBN": "",
        "ФГОС": "",
        "Размеры (Д × Ш × В) в см": "",
    }
    if container:
        for property in container:
            if ":" in property.text:
                pass
            else:
                prop = property.text.replace("\n", "").replace("\t", "").strip()
                for name in properties.keys():
                    if name in prop:
                        properties[name] = prop.split(name)[1]
        return properties

    else:
        ### TODO think about how to fix it (catch a lot 500 errors during work)
        return "TITLE GONE"


class Client:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/109.0.0.0 Safari/537.36',
        }

    def get_page(self, url: int) -> str:
        try:
            res = self.session.get(url=url)
            print(res.status_code)
            res.raise_for_status()
            return res.text
        except:
            return "EMPTY LINK"


if __name__ == '__main__':
    parser = Client()
    urls = read_excel_url()
    res = {}
    for url in urls:
        page = parser.get_page(url)
        title = get_title(page)
        properties = get_properties(page)
        image_url = get_image_urls(page)
        res[url] = {
            "Title": title,
            "Автор": properties.get("Автор", "DEFAULT"),
            "МЕДИА": image_url,
            "Издательство": properties.get("Издательство", "DEFAULT"),
            "Год издания": properties.get("Год издания", "DEFAULT"),
            "Артикул": properties.get("Артикул", "DEFAULT"),
            "Входит в УМК": properties.get("Входит в УМК", "DEFAULT"),
            "Федеральный перечень": properties.get("Федеральный перечень", "DEFAULT"),
            "Класс": properties.get("Класс", "DEFAULT"),
            "Предмет": properties.get("Предмет", "DEFAULT"),
            "Тип материала": properties.get("Тип материала", "DEFAULT"),
            "Учебная система": properties.get("Учебная система", "DEFAULT"),
            "Группа литературы": properties.get("Группа литературы", "DEFAULT"),
            "Количество страниц": properties.get("Количество страниц", "DEFAULT"),
            "Серия издательства": properties.get("Серия издательства", "DEFAULT"),
            "ISBN": properties.get("ISBN", "DEFAULT"),
            "ФГОС": properties.get("ФГОС", "DEFAULT"),
            "Размеры (Д × Ш × В) в см": properties.get("Размеры (Д × Ш × В) в см", "DEFAULT"),
        }
    with open('result.json', 'w') as json_file:
        json.dump(res, json_file)
    with open('result.json', 'r') as json_file:
        res = json.load(json_file)
    df = pd.DataFrame(res)
    df.to_excel('Result_2.xlsx')