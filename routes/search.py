from flask import Blueprint, request, jsonify, render_template, session

from db.models import cur, is_session_set

search_bp = Blueprint("search", name)

@search_bp.get("/search")
def search():
    q = request.args.get("q")
    if q is None:
        return jsonify({"error": "search can not be empty"})

    search_term = "%" + q + "%"

    try:
        cur.execute(
            """
            SELECT id,
                   title,
                   currency  ' '  printf('%,.2f', price) AS price,
                   source,
                   image_url,
                   created_at
            FROM products
            WHERE title LIKE ?
            LIMIT 20
            """,
            (search_term,)
        )
        results = cur.fetchall()
        results = [dict(row) for row in results]
    except Exception as e:
        print(f"Error: {e}")
        results = []

    if is_session_set():
        return render_template(
            "search.html",
            user=session["user"],
            products=results,
            q=q
        )

    return render_template("search.html", products=results, q=q)

@search_bp.get("/get-search-results")
def search_results():
    q = request.args.get("q")
    if q is None:
        return jsonify({"error": "search can not be empty"})

    search_term = "%" + q + "%"

    try:
        cur.execute(
            "SELECT * FROM products WHERE title LIKE ? LIMIT 5",
            (search_term,)
        )
        results = cur.fetchall()
        results = [dict(row) for row in results]
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Error fetching products"})
    else:
        return jsonify(results)