-- the queries are made for for sqlite so it might look a bit buggy

CREATE TABLE IF NOT EXISTS allowed_websites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain VARCHAR(255) NOT NULL UNIQUE,

    product_container_selector VARCHAR(255) NOT NULL,
    title_selector VARCHAR(255) NOT NULL,
    price_selector VARCHAR(255) NOT NULL,
    description_selector VARCHAR(255) NOT NULL,
    image_selector VARCHAR(255) DEFAULT "img",
    link_selector VARCHAR(255) DEFAULT "a",

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO allowed_websites(
    domain, product_container_selector, title_selector, price_selector, description_selector, image_selector, link_selector
) VALUES (
        'jiji.com.et', '.masonry-item', 'div.b-advert-title-inner--div', '.qa-advert-price', ".qa-description-text", 'source', 'a'
);

INSERT OR IGNORE INTO allowed_websites(
    domain, product_container_selector, title_selector, price_selector, description_selector, image_selector, link_selector
) VALUES (
        'ethiosuq.com', '.product-item__outer', '.woocommerce-loop-product__title', 'bdi', ".electro-description p", 'img', '.woocommerce-loop-product__link'
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    title TEXT NOT NULL,
    price REAL,
    currency TEXT DEFAULT 'ETB',

    category TEXT,
    source TEXT NOT NULL,

    image_url TEXT,
    product_url TEXT UNIQUE,

    description TEXT,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    google_id TEXT UNIQUE NOT NULL,

    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    given_name TEXT NOT NULL DEFAULT 'User',
    profile_picture_url TEXT,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
    role TEXT NOT NULL DEFAULT 'member'
);

CREATE TABLE IF NOT EXISTS cart_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER DEFAULT 1,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS scrape_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    source TEXT NOT NULL,
    category TEXT,
    scraped_count INTEGER,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);