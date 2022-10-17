from re import U
from tkinter import E
import requests
from bs4 import BeautifulSoup as BS
import lxml
import json
import fake_useragent
from geopy.geocoders import Yandex


def requester(link: str) -> lxml:  # does request for the link
    r = requests.get(link, headers={
        "User-Agent": fake_useragent.UserAgent().random,
    })
    html = BS(r.content, 'lxml')
    print(link)
    return html


def get_link_from_page(page: lxml) -> list:  # all shop links from page
    return [x['href'] for x in page.find_all('a', 'card-list__link')]


def data_from_shops(link: str):  # data from sites to dict
    data = []
    html_data = requester(link)
    links = get_link_from_page(html_data)
    nam = [x.text.split() for x in html_data.find_all('h2')][0]
    name = ' '.join(nam[len(nam) - 2:])
    address = [x.text.translate(x.text.maketrans('', '', '\t\r\n'))
               for x in html_data.find_all('p', 'card-list__description')]
    for x in links:
        a = requester('https://naturasiberica.ru' + x)
        work = 'пн-вс ' + a.find_all('div', 'original-shops__schedule')[0].text
        phone = a.find_all(
            'p', 'original-shops__phone')[0].text + '74992719642'  # возникли сложности с получением номера телефона, приходит пустой тег
        for add in address:
            data.append(
                {
                    'address': add,
                    'latlon': location(add),
                    'name': name,
                    'phones': [phone],
                    'working_hours': [work]

                }
            )
    return writer(data)


def location(place) -> list:  # retuens list with coordinates
    lt = Yandex(api_key='64c9bd8c-7db4-4e63-9710-d4819fb0fb95',
                user_agent=fake_useragent.UserAgent().random).geocode(place)
    return [float(lt.latitude), float(lt.longitude)]


def writer(data: list):
    data = json.dumps(data)
    data = json.loads(str(data))
    with open('data3.json', 'w', encoding='UTF-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    return 'Data has been added to data2.json'


print(data_from_shops('https://naturasiberica.ru/our-shops/'))
