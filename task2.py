import requests
from bs4 import BeautifulSoup as BS
import lxml
import json
import fake_useragent


# changes cookies to change city
def change_reg_connerter(link: str, id_city: str) -> list:
    my_cookie = {
        "version": 0,
        "name": 'BITRIX_SM_CITY_ID',
        "value": id_city,
        "port": None,
        "domain": '.som1.ru',
        "path": '/',
        "secure": False,
        "expires": None,
        "discard": False,
        "comment": None,
        "comment_url": None,
        "rest": {},
        "rfc2109": False
    }
    s = requests.Session()
    s.cookies.set(**my_cookie)
    conn = s.get(link, headers={
        "User-Agent": fake_useragent.UserAgent().random,
    })
    html = BS(conn.content, 'lxml')
    return [x.a['href'] for x in html.find_all('div', 'shops-col shops-button')]


# creates dict with nanes_of_city and id of this city
def get_dict_id_city(link: str) -> dict:
    s = requests.get(link, headers={
        "User-Agent": fake_useragent.UserAgent().random,
    })
    get_site = BS(s.content, 'lxml')
    l = get_site.find_all('label')
    name_city = [x.text for x in l if 'data-paren' in str(x)]
    id = [i['id'] for i in [x for x in l if 'data-paren' in str(x)]]
    return dict(zip(name_city, id))


def get_links_shops(link: str) -> list:  # returns list of shop links
    dict_with_id = get_dict_id_city(link)
    all_shops = []
    for name, id in dict_with_id.items():
        all_shops.extend(change_reg_connerter(link, id))
    return all_shops


def get_data_from_shop(shop_link) -> lxml:  # data from each shop
    cor_link = 'https://som1.ru' + shop_link
    r = requests.get(cor_link, headers={
        "User-Agent": fake_useragent.UserAgent().random,
    })
    r.encoding = 'UTF-8'
    result = BS(r.content, 'lxml')
    print(cor_link)
    return result


def data_from_shop(link: str):  # finds data to give to dict
    tuple_links = get_links_shops(link)
    list_dict = []
    for x in tuple_links:
        html = get_data_from_shop(x)
        cor = [x.text for x in html.find_all(
            'script') if 'showShopsMap' in str(x)][0]
        cor = [float(x.replace("'", "")) for x in cor[cor.index(
            ':') + 3: cor.rindex(',') - 2].split(',')]
        name = html.title.text
        cont_data = html.find_all('table', 'shop-info-table')
        data_list = [x.text.split('\n') for x in cont_data]
        data = list((filter(lambda x: x != '', data_list[0])))
        address = data[1]
        work = data[-1].lower().replace(':', '', 1)
        phon = [x[:11] for x in [x.translate(x.maketrans(
            '', '', '() -+доб.')) for x in data[3:-2][0].split(',')]]

        list_dict.append(
            {
                'address': address,
                'latlon': cor,
                'name': name,
                'phones': phon,
                'working_hours': [work]
            }
        )
    return writer(list_dict)


def writer(data: list):
    data = json.dumps(data)
    data = json.loads(str(data))
    with open('data2.json', 'w', encoding='UTF-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    return 'Data has been added to data2.json'


print(data_from_shop('https://som1.ru/shops'))
