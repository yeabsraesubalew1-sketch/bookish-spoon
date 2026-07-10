from flask import Flask, jsonify, request, render_template, redirect
from bs4 import BeautifulSoup
import urllib.request
from urllib.parse import urlparse
import datetime
import sqlite3
import os
import re

app = Flask(__name__, template_folder="pages")

db_path = "./db/e_commerce.db"
sql_init_file = "./db/db.sql"

p = not os.path.exists(db_path)

conn = sqlite3.connect(db_path, check_same_thread=False)
conn.row_factory = sqlite3.Row

if p:
    with open(sql_init_file, "r") as f:
        sql_script = f.read()
        conn.executescript(sql_script)
        conn.commit()

    print("Database created and initialized.")
else:
    print("Database already exists.")

cur = conn.cursor()


scrape_status = {"message": "loading..."}

@app.route("/")
def home():
    # just untill we actually build the home page
    return render_template("index.html")

@app.route("/scrape-status")
def current_scrape_status():
    return jsonify(scrape_status)

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
    except:
        number = None

    return text, number


@app.route("/scrape", methods=["POST", "GET"])
def scrape():
    global scrape_status
    scrape_status["message"], scrape_status["progress"] = "loading", "Scraping in progress..."
    if request.method == "POST":
        data = [] 
        if request.is_json:
            payload = request.get_json(silent=True) or {}
            url = payload.get("url")
            category = payload.get("category")
        else:
            url = request.form.get("url") # "https://jiji.com.et/shoes"
            category = request.form.get("category")
        if not url:
            return jsonify({"error": "url is required"})
        
        try:
            html = urllib.request.urlopen(url).read().decode('utf-8')
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": f"unable to open 'url' : '{url}'"})
        
        parsed_url = urlparse(url)

        cur.execute("select * from allowed_websites where domain = ?", (parsed_url.netloc,))
        scrape_classes = dict(cur.fetchone())
        if not scrape_classes:
            return jsonify({"error": "This website is not allowed"})
        print(scrape_classes)
        soup = BeautifulSoup(html, "html.parser")

        try:
            divs = soup.select(scrape_classes["product_container_selector"])

            scrape_status["message"] = "Getting Descriptions..."

            for i, div in enumerate(divs):
                scrape_status["progress"] = f"Getting Description Of {i}/{len(divs)}..."
                
                de = urlparse(div.select_one(scrape_classes["link_selector"])["href"])
                if not all([de.scheme, de.netloc]):
                    div_url = f"{parsed_url.scheme}://{parsed_url.netloc}{div.select_one(scrape_classes["link_selector"])["href"]}"
                else:
                    div_url = div.select_one(scrape_classes["link_selector"])["href"]

                get_description = False if scrape_classes["description_selector"] =='none' else get_product_description(div_url, scrape_classes["description_selector"])
                description = get_description if get_description else "No description"
                currency, price = split_num_text(div.select_one(scrape_classes["price_selector"]).text)
                d = {
                    "title": div.select_one(scrape_classes["title_selector"]).text,
                    "price": price,
                    "currency": currency,
                    "category": category,
                    "source": parsed_url.netloc.split(".")[0],
                    "product_url": div_url,
                    "image_url": div.select_one(scrape_classes["image_selector"])["srcset"].split(' ')[0],
                    "description": description,
                    "timestamp": datetime.datetime.now()
                }
                data.append(d)
        except AttributeError:
            return jsonify({"error": "Wrong or non existant class/id/tag name(problem in database)"})
        except Exception as e:
            return jsonify({"error": f"{e}"})
        else:
            return jsonify(data)
        
        
    else:
        return render_template("scrape.html")

# Catch all 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('not_found_pages.html')

@app.errorhandler(500)
def page_not_found(e):
    return "Server error"

if __name__ == "__main__":
    app.run(debug=True)