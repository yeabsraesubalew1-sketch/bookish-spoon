from flask import Flask, jsonify, request, render_template, redirect
from bs4 import BeautifulSoup
import urllib.request
from urllib.parse import urlparse
import datetime

# Point Flask at the custom templates directory
app = Flask(__name__, template_folder="pages")

scrape_status = {"message": "loading..."}

@app.route("/")
def home():
    # just untill we actually build the home page
    return """
home
<a href='/scrape'>scrape page</a>
"""

@app.route("/scrape-status")
def current_scrape_status():
    return jsonify(scrape_status)

def get_product_description(url):
    try:
        html = urllib.request.urlopen(url).read().decode('utf-8')
        soup = BeautifulSoup(html, "html.parser")
    except Exception:
        return f"Error trying to get description: {url}"
    else:
        return soup.select_one(".qa-description-text").text


@app.route("/scrape", methods=["POST", "GET"])
def echo():
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
            return jsonify({"error": "url is required"}) # , 400
        
        html = urllib.request.urlopen(url).read().decode('utf-8')
        soup = BeautifulSoup(html, "html.parser")

        divs = soup.select(".masonry-item")

        scrape_status["message"] = "Getting Descriptions..."

        for i, div in enumerate(divs):
            scrape_status["progress"] = f"Getting Description Of {i}/{len(divs)}..."
            parsed_url = urlparse(url)
            div_url = f"{parsed_url.scheme}://{parsed_url.netloc}{div.select_one("a")["href"]}"
            get_description = get_product_description(div_url)
            description = get_description if get_description else f"No description"
            d = {
                "title": div.select_one("div.b-advert-title-inner--div").text,
                "price": int(div.select_one(".qa-advert-price").text.split(' ')[1].replace(",", "")),
                "currency": div.select_one(".qa-advert-price").text.split(' ')[0],
                "category": category,
                "source": "jiji", # just for now
                "product_url": div_url,
                "image_url": div.select_one("source")["srcset"].split(' ')[0],
                "description": description,
                "timestamp": datetime.datetime.now()
            }
            data.append(d)
        return jsonify(data)
    else:
        return render_template("scrape.html")

if __name__ == "__main__":
    app.run(debug=True)