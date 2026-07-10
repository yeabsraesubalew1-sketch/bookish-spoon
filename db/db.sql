-- the queries are made for for sqlite so it might look a bit buggy
CREATE TABLE allowed_websites (
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
INSERT INTO allowed_websites(
        domain,
        product_container_selector,
        title_selector,
        price_selector,
        description_selector,
        image_selector,
        link_selector
    )
VALUES (
        'jiji.com.et',
        '.masonry-item',
        'div.b-advert-title-inner--div',
        '.qa-advert-price',
        ".qa-description-text",
        'source',
        'a'
    );
INSERT INTO allowed_websites(
        domain,
        product_container_selector,
        title_selector,
        price_selector,
        description_selector,
        image_selector,
        link_selector
    )
VALUES (
        'ethiosuq.com',
        '.product-item__outer',
        '.woocommerce-loop-product__title',
        'bdi',
        ".electro-description p",
        'img',
        '.woocommerce-loop-product__link'
    );