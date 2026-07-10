import urllib.request
import datetime
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from db.models import cur, conn


def get_product_description(url, selector):
    try:
        html = urllib.request.urlopen(url).read().decode('utf-8')
        soup = BeautifulSoup(html, "html.parser")
    except Exception:
        return f"Error trying to get description: {url}"
    else:
        return soup.select_one(selector).text


def split_num_text(s):
    text = "".join(re.findall(r"[A-Za-z]+", s))
    number = "".join(re.findall(r"[0-9.]+", s))
    try:
        number = float(number)
    except Exception:
        number = None

    return text, number


def insert_product(product):
    title = product.get("title", '')
    currency = product.get("currency", 'ETB')
    source = product.get("source", 'Unknown')
    timestamp = product.get("timestamp")
    product_url = product.get("product_url", '')
    price = product.get("price")
    image_url = product.get("image_url", '')
    description = product.get("description", 'No description')
    category = product.get("category", 'others')

    if not (title and price is not None and product_url and image_url):
        product['error'] = "invalid product"
        print(product)
        return product

    try:
        iso = None

        if isinstance(timestamp, datetime.datetime):
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=datetime.timezone.utc)
            iso = timestamp.astimezone(datetime.timezone.utc).isoformat().replace("+00:00", "Z")

        elif isinstance(timestamp, str) and timestamp:
            try:
                dt = datetime.datetime.strptime(
                    timestamp,
                    "%a, %d %b %Y %H:%M:%S %Z"
                )
                dt = dt.replace(tzinfo=datetime.timezone.utc)
                iso = dt.isoformat().replace("+00:00", "Z")
            except Exception:
                iso = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")

        else:
            iso = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")

        cur.execute(
            """
            INSERT INTO products
            (title, price, currency, category, source, image_url, product_url, description, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (title, price, currency, category, source, image_url, product_url, description, iso)
        )

        return False

    except Exception as e:
        print(f"Error: {e}")
        product["error"] = "database insert failed"
        product["error_message"] = str(e)
        print(product)
        return product