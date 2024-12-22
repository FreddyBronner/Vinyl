import requests
from bs4 import BeautifulSoup
import re
import time
import json

def parse_vinyl_list_page(url):
    """Парсит страницу со списком виниловых пластинок."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        vinyls = []
        items = soup.find_all("div", class_="uss_shop_list_view_item")
        for item in items:
            try:
                name_a = item.find("div", class_="uss_shop_name").find('a')
                name = name_a.text.strip() if name_a else None
                link = name_a['href'] if name_a else None
                code_text = item.find("div", class_="uss_shop_uid").text.strip() if item.find("div", class_="uss_shop_uid") else None
                code_match = re.search(r"Код:\s*(\d+)", code_text) if code_text else None
                code = code_match.group(1) if code_match else None

                params = item.find_all("div", class_="uss_shop_param")
                artist = None
                album = None
                firm = None
                country = None
                year = None
                genre = None
                type_ = None

                for param in params:
                    text = param.text.strip()
                    artist_match = re.match(r"(?:Artist|Исполнитель):\s*(.+)", text)
                    if artist_match:
                        artist = artist_match.group(1).strip()
                    album_match = re.match(r"(?:Альбом|Album):\s*(.+)", text)
                    if album_match:
                        album = album_match.group(1).strip()
                    firm_match = re.match(r"(?:Фирма|Label):\s*(.+)", text)
                    if firm_match:
                        firm = firm_match.group(1).strip()
                    country_match = re.match(r"(?:Страна|Country):\s*(.+)", text)
                    if country_match:
                        country = country_match.group(1).strip()
                    year_match = re.match(r"(?:Год|Year):\s*(\d+)", text)
                    if year_match:
                        year = year_match.group(1).strip()
                    genre_match = re.match(r"(?:Жанр|Genre):\s*(.+)", text)
                    if genre_match:
                        genre = genre_match.group(1).strip()
                    type_match = re.match(r"(?:Тип|Type):\s*(.+)", text)
                    if type_match:
                        type_ = type_match.group(1).strip()

                description = item.find("div", class_="uss_shop_description").text.strip() if item.find("div", class_="uss_shop_description") else None
                price_span = item.find("span", class_="actual_price")
                price_em = price_span.find("em", class_="price_class") if price_span else None
                price = price_em["data-clear-price"] if price_em and "data-clear-price" in price_em.attrs else None

                vinyls.append({
                    "name": name,
                    "link": link,
                    "code": code,
                    "artist": artist,
                    "album": album,
                    "firm": firm,
                    "country": country,
                    "year": year,
                    "genre": genre,
                    "type": type_,
                    "description": description,
                    "price": price
                })
            except AttributeError as e:
                print(f"Error parsing item: {e}")
                continue #Продолжаем парсинг даже если один элемент не распарсился
        return vinyls
    except requests.exceptions.RequestException as e:
        print(f"Error requesting page: {e}")
        return None

base_url = "https://melomania.online/store/vinilovye-plastinki/?page="
all_vinyls = []
max_pages = 1060 # Максимальное количество страниц для парсинга (для теста). Установите больше при необходимости.

for page in range(1, max_pages + 1):
    url = f"{base_url}{page}" if page > 1 else base_url
    print(f"Парсинг страницы: {url}")
    vinyls = parse_vinyl_list_page(url)
    if vinyls:
        all_vinyls.extend(vinyls)
        time.sleep(2) # Задержка в 5 секунд между запросами
    else:
        print("Не удалось получить данные со страницы. Завершение парсинга.")
        break #Прерываем цикл, если страница не загрузилась
print(f"Всего спарсено {len(all_vinyls)} записей")
# Сохранение в JSON
with open("vinyls.json", "w", encoding='utf-8') as f:
    json.dump(all_vinyls, f, indent=4, ensure_ascii=False)

print("Данные сохранены в файл vinyls.json")