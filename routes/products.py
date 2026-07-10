from flask import Blueprint, request, jsonify, render_template, abort, session

from db.models import cur, conn, is_session_set

products_bp = Blueprint("products", __name__)

@products_bp.route("/")
def home():
    try:
        cur.execute(
            """
            SELECT id,
                   title,
                   currency || ' ' || printf('%,.2f', price) AS price,
                   source,
                   image_url,
                   created_at
            FROM products
            ORDER BY created_at DESC
            LIMIT 15
            """
        )
        products = cur.fetchall()
        products = [dict(row) for row in products]
    except Exception as e:
        print(f"Error: {e}")
        products = []

    if is_session_set():
        return render_template(
            "index.html",
            user=session["user"],
            products=products
        )

    return render_template("index.html", products=products)


@products_bp.delete("/product")
def delete_product():
    if request.is_json:
        product_id = request.get_json(silent=True)
    else:
        return jsonify({"error": "not supported input method"})

    if not product_id:
        return jsonify({"error": "nothing was submitted"})

    if not isinstance(product_id, dict):
        print(product_id)
        return jsonify({"error": "expected JSON array of products"})

    if is_session_set():
        user = session["user"]

        if user.get('role') == "admin":
            try:
                cur.execute(
                    "DELETE FROM products WHERE id = ?",
                    (product_id.get('product_id'),)
                )
                conn.commit()
            except Exception as e:
                print(f"Error: {e}")
                return jsonify({'error': 'Error Deleting'})
            else:
                return jsonify({'success': 'Successfully Removed'})
        else:
            return jsonify({'error': 'No privileges'})
    else:
        return jsonify({'error': 'You are logged out'})

@products_bp.get("/product/<int:id>")
def product_page(id):
    try:
        cur.execute(
            """
            SELECT id,
                   title,
                   currency || ' ' || printf('%,.2f', price) AS price,
                   source,
                   product_url,
                   description,
                   image_url,
                   created_at
            FROM products
            WHERE id = ?
            """,
            (id,)
        )
        product = cur.fetchone()
    except Exception as e:
        print(f"Error: {e}")
        abort(500)

    if product is None:
        abort(404)

    if is_session_set():
        return render_template("product.html", user=session["user"], product=product)

    return render_template("product.html", product=product)

@products_bp.get("/fetch-products")
def fetch_products():
    offset = int(request.args.get("offset", 0))
    limit = int(request.args.get("limit", 15))

    try:
        cur.execute(
            """
            SELECT id,
                   title,
                   currency || ' ' || printf('%,.2f', price) AS price,
                   source,
                   image_url,
                   created_at
            FROM products
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset)
        )
        products = cur.fetchall()
        products = [dict(row) for row in products]
        return jsonify(products)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)})