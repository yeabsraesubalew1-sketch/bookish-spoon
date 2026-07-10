# E-Commerce Web Application

---

## Project Title
**E-Commerce Web Application with Scraping Support**

---

## Project Overview  
This project is a full-stack e-commerce web application built using **Python Flask**.  
It demonstrates how Python can be used as a backend framework to handle authentication, product management, web scraping, and database-driven features.

**What it does:**
- Allows users to browse, search, and view products
- Supports user authentication (including Google OAuth)
- Enables admins to scrape products from supported e-commerce websites
- Provides a shopping cart system per user

---

## Key Features / Functionalities
- User authentication (session-based + Google OAuth)
- Product browsing and detailed product pages
- Product search with live suggestions
- Shopping cart (add, view, remove items)
- Admin-only product scraping and insertion
- Role-based access control (admin vs member)
- SQLite-backed CRUD operations
- Server-side rendering using Jinja templates
- Error handling and access protection

---

## Scraping & Product Aggregation
The backend supports scraping products from approved e-commerce websites.  
Allowed websites and their selectors are configured in the database, making the scraper **extensible without code changes**.

The scraping process:
- Fetches listing pages
- Extracts product data using stored selectors
- Normalizes products into a unified schema
- Inserts valid products into the database
- Logs scraping activity

---

## Unified Product Data Schema
All scraped and stored products follow this structure:

```json
{
  "title": "string",
  "price": "number",
  "currency": "ETB",
  "category": "string",
  "source": "string",
  "image_url": "string",
  "product_url": "string",
  "description": "string",
  "timestamp": "ISO 8601"
}

```

## API & Route Overview

Main application routes include:

* `GET /` - Home page
* `GET /login`, `GET /logout` - Authentication
* `GET /auth/google`, `GET /callback` - Google OAuth
* `GET /product/<id>` - Product detail page
* `DELETE /product` - Delete product (admin only)
* `GET /search` - Product search page
* `GET /get-search-results` - Live search API
* `GET /my-cart` - View cart
* `POST /my-cart` - Add item to cart
* `DELETE /my-cart` - Remove item from cart
* `POST /scrape` - Scrape products (admin only)
* `POST /submit-json` - Insert scraped products

---


## How to Run

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set environment variables (see `.env.example`)
4. Run the application:

```bash
flask run
```

