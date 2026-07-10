from flask import Blueprint, request, jsonify, render_template, abort, session
import urllib.request
import datetime
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from extensions import socketio
from db.models import cur, conn, is_session_set
from services.scraper import (
    get_product_description,
    split_num_text,
    insert_product,
)

scrape_bp = Blueprint("scrape", __name__)

@scrape_bp.route("/scrape", methods=["POST", "GET"])
def scrape():
    socketio.emit('progress', {'message': 'loading...', 'progress': "Scraping in progress..."})

    if not is_session_set() or not session["user"].get("role") == "admin":
        abort(404)

    if request.method == "POST":
        data = []

        if request.is_json:
            payload = request.get_json(silent=True) or {}
            url = payload.get("url")
            category = payload.get("category")
        else:
            url = request.form.get("url")
            category = request.form.get("category")

        if not url:
            return jsonify({"error": "url is required"})

        try:
            html = urllib.request.urlopen(url).read().decode('utf-8')
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": f"unable to open 'url' : '{url}'"})

        parsed_url = urlparse(url)

        cur.execute(
            "SELECT * FROM allowed_websites WHERE domain = ?",
            (parsed_url.netloc,)
        )
        scrape_classes = cur.fetchone()
        if not scrape_classes:
            return jsonify({"error": "This website is not allowed"})

        scrape_classes = dict(scrape_classes)
        soup = BeautifulSoup(html, "html.parser")

        try:
            divs = soup.select(scrape_classes["product_container_selector"])

            socketio.emit('progress', {'message': 'Getting Descriptions...'})

            for i, div in enumerate(divs):
                socketio.emit(
                    'progress',
                    {'progress': f"Getting Description Of {i + 1}/{len(divs)}..."}
                )

                link_el = div.select_one(scrape_classes["link_selector"])
                de = urlparse(link_el["href"])

                if not all([de.scheme, de.netloc]):
                    div_url = f"{parsed_url.scheme}://{parsed_url.netloc}{link_el['href']}"
                else:
                    div_url = link_el["href"]

                get_description = (
                    False if scrape_classes["description_selector"] == 'none'
                    else get_product_description(div_url, scrape_classes["description_selector"])
                )

                description = get_description if get_description else "No description"
                currency, price = split_num_text(
                    div.select_one(scrape_classes["price_selector"]).text
                )

                d = {
                    "title": div.select_one(scrape_classes["title_selector"]).text,
                    "price": price,
                    "currency": currency,
                    "category": category,
                    "source": parsed_url.netloc.split(".")[0],
                    "product_url": div_url,
                    "image_url": div.select_one(
                        scrape_classes["image_selector"]
                    )["srcset"].split(' ')[0],
                    "description": description,
                    "timestamp": datetime.datetime.now(),
                }

                data.append(d)

        except AttributeError:
            return jsonify({"error": "Wrong or non existent selector (DB issue)"})
        except Exception as e:
            return jsonify({"error": f"{e}"})
        else:
            return jsonify(data)

    else:
        if is_session_set():
            return render_template("scrape.html", user=session["user"])
        return render_template("scrape.html")

@scrape_bp.post("/submit-json")
def submit_json():
    if request.is_json:
        textarea = request.get_json(silent=True)
    else:
        textarea = request.form.get("edit-textarea")

    if not textarea:
        return jsonify({"error": "nothing was submitted"})

    if isinstance(textarea, str):
        return jsonify({"error": "expected JSON array of products"})
    if not isinstance(textarea, list):
        return jsonify({"error": "invalid payload format"})

    invalid_products = []
    categories = set()
    source = ''

    socketio.emit('progress', {'message': 'Inserting products...', 'progress': ""})

    for i, product in enumerate(textarea):
        insert_response = insert_product(product)
        if insert_response:
            invalid_products.append(insert_response)
        else:
            categories.add(product.get("category", 'others'))
            source = product.get("source", 'Unknown')

        socketio.emit(
            'progress',
            {'progress': f"Attempting to insert product {i}/{len(textarea)}..."}
        )

    if invalid_products:
        return jsonify(invalid_products)

    try:
        ca = ",".join(categories)
        cur.execute(
            "INSERT INTO scrape_logs (source, category, scraped_count) VALUES (?, ?, ?)",
            (source, ca, len(textarea))
        )
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")

    return jsonify({"success": True})