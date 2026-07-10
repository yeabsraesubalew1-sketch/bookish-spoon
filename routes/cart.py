from flask import Blueprint, request, jsonify, render_template, abort, session

from db.models import cur, conn, is_session_set

cart_bp = Blueprint("cart", __name__)

@cart_bp.route("/my-cart", methods=["POST", "GET", "DELETE"])
def my_cart():
    if request.method == "POST":
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
        else:
            return jsonify({'logged_in': False})

        try:
            cur.execute(
                "SELECT * FROM cart_items WHERE user_id = ? AND product_id = ?",
                (user.get("id"), product_id.get('product_id'))
            )
            in_cart = cur.fetchone()

            if in_cart is None:
                cur.execute(
                    "INSERT INTO cart_items (user_id, product_id) VALUES (?, ?)",
                    (user.get('id'), product_id.get('product_id'))
                )
                conn.commit()
            else:
                return jsonify({'error': "Item already in cart"})

        except Exception as ee:
            print(f"Error: {ee}")
            return jsonify({'error': "Error Inserting Item"})
        else:
            return jsonify({'success': "Successfully added To Cart"})

    elif request.method == "GET":
        if is_session_set():
            user = session["user"]
            try:
                cur.execute(
                    """
                    SELECT products.id AS id,
                           title,
                           currency || ' ' || printf('%,.2f', price) AS price,
                           source,
                           image_url,
                           product_url
                    FROM products
                    JOIN cart_items ON product_id = products.id
                    WHERE user_id = ?
                    ORDER BY cart_items.created_at DESC
                    LIMIT 15;
                    """,
                    (user.get('id'),)
                )
                incart = cur.fetchall()
            except Exception as e:
                print(f"Error: {e}")
                return render_template("mycart.html", user=user)
            else:
                return render_template("mycart.html", user=user, incart=incart)
        else:
            return render_template("mycart.html", notSignedin=True)

    elif request.method == "DELETE":
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
            try:
                cur.execute(
                    "DELETE FROM cart_items WHERE user_id = ? AND product_id = ?",
                    (user.get('id'), product_id.get('product_id'))
                )
                conn.commit()
            except Exception as e:
                print(f"Error: {e}")
                return jsonify({'error': 'Error Deleting'})
            else:
                return jsonify({'success': 'Successfully Removed'})
        else:
            return jsonify({'error': 'You are logged out'})

    else:
        abort(405)

@cart_bp.get("/fetch-from-cart")
def fetch_from_cart():
    offset = int(request.args.get("offset", 0))
    limit = int(request.args.get("limit", 15))

    try:
        if is_session_set():
            user = session['user']
            cur.execute(
                """
                SELECT products.id AS id,
                       title,
                       currency || ' ' || printf('%,.2f', price) AS price,
                       source,
                       image_url,
                       product_url
                FROM products
                JOIN cart_items ON product_id = products.id
                WHERE user_id = ?
                ORDER BY cart_items.created_at DESC
                LIMIT ? OFFSET ?;
                """,
                (user.get('id'), limit, offset)
            )

        products = cur.fetchall()
        products = [dict(row) for row in products]
        return jsonify(products)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)})