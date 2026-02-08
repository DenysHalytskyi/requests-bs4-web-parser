"""The script collects product data and stores it in a Postgres database."""

from load_django import *
from parser_app.models import *
import requests
from bs4 import BeautifulSoup
from django.core.exceptions import ValidationError
from django.db import DatabaseError


url = "https://brain.com.ua/ukr/Mobilniy_telefon_Apple_iPhone_16_Pro_Max_256GB_Black_Titanium-p1145443.html"
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'ru-UA,ru;q=0.9,uk-UA;q=0.8,uk;q=0.7,ru-RU;q=0.6,en-US;q=0.5,en;q=0.4',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
}

session = requests.session()

try:
    response = session.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')

    product_data = {}
    specs = {}
    images_list = []

    # Find full title
    try:
        product_data["Title"] = soup.find('span', class_='product-clean-name').text.strip()

    except AttributeError as e:
        product_data["Title"] = None

    # Find characteristics
    try:
        rows = soup.select(".br-pr-chr-item > div > div")
        for row in rows:
            spans = row.find_all('span', recursive=False)
            if len(spans) >= 2:
                key = " ".join(spans[0].get_text(strip=True).split())
                raw_value = spans[1].get_text(separator=" ", strip=True)
                value = " ".join(raw_value.split())
                specs[key] = value

        product_data["Characteristics"] = specs

    except (AttributeError, TypeError) as e:
        product_data["Characteristics"] = None


    try:
        product_data["Color"] = specs["Колір"]
    except AttributeError as e:
        product_data["Color"] = None
    try:
        product_data["Memory"] = specs["Вбудована пам'ять"]
    except AttributeError as e:
        product_data["Memory"] = None
    try:
        product_data["Producer"] = specs["Виробник"]
    except AttributeError as e:
        product_data["Producer"] = None
    try:
        product_data['Diagonal'] = specs['Діагональ екрану']
    except AttributeError as e:
        product_data['Diagonal'] = None
    try:
        product_data["Display_Resolution"] = specs['Роздільна здатність екрану']
    except AttributeError as e:
        product_data['Display_Resolution'] = None



    # Find price
    try:
        price_div = soup.find('div', class_='price-wrapper')
        if price_div:
            price = price_div.find('span').text.strip()
            product_data["Price"] = price.replace(' ', '')

    except AttributeError as e:
        product_data["Price"] = None

    # Find images
    try:
        all_images = soup.find_all('img', class_='br-main-img')
        for images in all_images:
            images_list.append(images.get('src'))

        product_data["Images"] = images_list

    except AttributeError as e:
        product_data["Images"] = None

    # Find product code
    try:
        product_code_div = soup.find('div', id = 'product_code')
        if product_code_div:
            product_code_span = product_code_div.find('span', class_='br-pr-code-val').text.strip()
            if product_code_span:
                product_data["Product_Code"] = product_code_span

    except AttributeError as e:
        product_data["Product_Code"] = None

    # Find reviews
    try:
        review = soup.find('a', href='#reviews-list').text.strip()
        if review:
            review_count = ''.join(filter(str.isdigit, review))
            product_data["Reviews"] = int(review_count)

    except AttributeError as e:
        product_data["Reviews"] = None


    data_to_save = {
            "title": product_data["Title"],
            "product_code": product_data["Product_Code"],
            "color": product_data.get("Color"),
            "memory": product_data.get("Memory"),
            "producer": product_data.get("Producer"),
            "price": product_data["Price"],
            "images": ", ".join(product_data.get('Images', [])),
            "review_count": product_data.get("Reviews"),
            "screen_diagonal": product_data.get("Diagonal"),
            "display_resolution": product_data.get("Display_Resolution"),
            "characteristics": product_data.get("Characteristics")
    }

    try:
        obj, created = Product.objects.get_or_create(**data_to_save)

        if created:
            print(f"Product {obj.title} ({obj.product_code}) successfully created.")
        else:
            print(f"Product {obj.title} already exists in this category.")

    except ValidationError as e:
        print(f"Database Integrity Error: {e}")
    except DatabaseError as e:
        print(f"Database Connection Error: {e}")
    except Exception as e:
        print(f"Unexpected error while saving to DB: {e}")




except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e}")
except requests.exceptions.ConnectionError as e:
    print(f"Connection Error: {e}")
except requests.exceptions.Timeout as e:
    print(f"Timeout Error: {e}")
except Exception as e:
    print(f"Unknown Error: {e}")
