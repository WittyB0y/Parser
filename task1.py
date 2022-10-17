import requests
from bs4 import BeautifulSoup as BS
import lxml
import json


def requester(link: str) -> lxml:  # does request to the site and returns data from site
    r = requests.get(link)
    html = BS(r.content, 'lxml')
    print(link)
    return html


def getter_link(uncut_link: str) -> str:  # cut link
    cut_link = uncut_link[uncut_link.index('"') + 1:uncut_link.rindex('"')]
    return cut_link


def finder_link(link: str) -> dict:  # creates dict with links
    dict_link = {}
    data_from_site = requester(link)
    elements = data_from_site.find('ul', 'c-list c-accordion')
    counter = 0
    for elem in elements:
        links = [getter_link(m) for m in str(
            elem.next_element.find('ul')).split('\n') if 'href' in m]
        if len(links) == 0:
            continue
        dict_link[counter] = links
        counter += 1
    return dict_link


def domain(uncut_link: str) -> str:  # cuts domain
    slash = uncut_link.index('/') + 2
    result = uncut_link[slash: uncut_link[slash:].index('/') + slash]
    return f'https://{result}'


def get_info_from_site(link: str) -> list:
    links_names = finder_link(link)
    cut_domain = domain(link)
    list_data = []
    for k, v in links_names.items():
        for l in v:
            data_site = requester(f'{cut_domain}{l}')
            adr = address(data_site)
            nme = name(data_site)
            phone = get_phone(data_site)
            loc = location(data_site)
            work = work_hour(data_site)
            list_data.append({
                'address': adr,
                'latlon': loc,
                'name': nme,
                'phones': phone,
                'working_hours': work
            })
    return writer(list_data)


def address(data_site: lxml) -> lxml:  # returns adress
    result = data_site.find('div', 's-dato').p.span.text
    return result


def name(data_site: lxml) -> lxml:  # returns name
    result = data_site.title.text
    return result[result.rindex('-') + 1:].strip()


def writer(data: list):
    data = json.dumps(data)
    data = json.loads(str(data))
    with open('data.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    return 'Data has been added to data.json'


def get_phone(data_site: lxml) -> list:  # returns list of phones
    result1 = data_site.find('div', 's-dato').find_all('span')[1].text
    result1 = result1[:result1.index(
        '-') - 1] + result1[result1.index('-') + 1:]
    result2 = [str(x)[str(x).index('</i>') + 5: str(x).index('</a>')]
               for x in data_site.find_all('li', 'call')]

    def x(x): return x.replace(' ', '') if '+' in x else x
    return [result1] + list(map(x, result2))


def location(data_site: lxml) -> list:  # returns list of locations
    result1 = str(data_site.find('div', 's-mapa'))
    result2 = str(data_site.find('div', 's-mapa'))
    return [float(result1[result1.index('!2d') + 3: result1.index('!2d') + 12]), float(result2[result2.index('!3d') + 3: result2.index('!3d') + 13])]


def work_hour(data_site: lxml) -> list:
    def isfloat(num):
        try:
            float(num)
            return True
        except ValueError:
            return False
    result = data_site.find('div', 's-dato')
    list_with_time = [x.text.split() for x in result.find_all('span')[-2:]]
    time = [y.replace('.', ':') for y in list_with_time[0] +
            list_with_time[1] if isfloat(y)]
    str1 = [f'mon-thu {time[0] if time[0][0] != "0" else time[0][1:]} - {time[1] if time[1][0] != "0" else time[1][1:]} {time[2] if time[2][0] != "0" else time[2][1:]}-{time[3] if time[3][0] != "0" else time[3][1:]}']
    str2 = [f'fri {time[0] if time[0][0] != "0" else time[0][1:]} - {time[1] if time[1][0] != "0" else time[1][1:]} {time[2] if time[2][0] != "0" else time[2][1:]}-{time[3] if time[3][0] != "0" else time[3][1:]}']
    return str1 + str2


print(get_info_from_site('https://oriencoop.cl/sucursales.htm'))
