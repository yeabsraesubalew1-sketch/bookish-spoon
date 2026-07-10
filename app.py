from flask import Flask
from config import SECRET_KEY
from extensions import socketio
from routes.auth import auth_bp
from routes.scrape import scrape_bp
from routes.cart import cart_bp
from routes.products import products_bp
from routes.search import search_bp
from errors import register_error_handlers




app = Flask(__name__, template_folder="pages")
app.secret_key = SECRET_KEY

socketio.init_app(app)

# -------Blueprints----------
app.register_blueprint(auth_bp)
app.register_blueprint(scrape_bp)
app.register_blueprint(cart_bp)
app.register_blueprint(products_bp)
app.register_blueprint(search_bp)

# -------Errors--------------
register_error_handlers(app)