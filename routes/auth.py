from flask import Blueprint, render_template, redirect, request, session
import requests

from config import (
    CLIENT_ID,
    CLIENT_SECRET,
    GOOGLE_AUTH_URL,
    GOOGLE_TOKEN_URL,
    GOOGLE_USERINFO_URL,
    REDIRECT_URI,
)

from db.models import cur, conn, is_session_set

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login")
def login():
    print(CLIENT_ID, CLIENT_SECRET, GOOGLE_AUTH_URL)
    if is_session_set():
        return redirect("/")
    else:
        if CLIENT_ID and CLIENT_SECRET: 
            return render_template("login.html")
        else:
            return render_template("login.html", no_client=True)


@auth_bp.route("/auth/google")
def google_auth():
    if not CLIENT_ID or not CLIENT_SECRET:
        return render_template('error.html')

    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }

    request_url = requests.Request(
        "GET",
        GOOGLE_AUTH_URL,
        params=params
    ).prepare().url

    return redirect(request_url)


@auth_bp.route("/callback")
def callback():
    code = request.args.get("code")

    if not CLIENT_SECRET or not CLIENT_ID or not code:
        return render_template('error.html')

    token_data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    token_response = requests.post(GOOGLE_TOKEN_URL, data=token_data)
    token_json = token_response.json()

    access_token = token_json.get("access_token")

    userinfo_response = requests.get(
        GOOGLE_USERINFO_URL,
        headers={"Authorization": f"Bearer {access_token}"}
    )

    userinfo = userinfo_response.json()

    try:
        cur.execute("select * from users where role = 'admin'")
        if cur.fetchone() is None:
            cur.execute(
                """INSERT INTO users (google_id, email, name, given_name, profile_picture_url, role)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    userinfo.get('id'),
                    userinfo.get('email'),
                    userinfo.get('name'),
                    userinfo.get('given_name'),
                    userinfo.get('picture'),
                    'admin',
                )
            )
        else:
            cur.execute(
                """INSERT INTO users (google_id, email, name, given_name, profile_picture_url)
                VALUES (?, ?, ?, ?, ?)
                """, (
                    userinfo.get('id'),
                    userinfo.get('email'),
                    userinfo.get('name'),
                    userinfo.get('given_name'),
                    userinfo.get('picture'),
                )
            )
        conn.commit()
    except Exception as e:
        print(f"Error registering: {e}")
    else:
        print("Successfully Registered")

    try:
        cur.execute(
            "SELECT * FROM users WHERE google_id = ?",
            (userinfo.get('id'),)
        )
        user = cur.fetchone()

        session["user"] = {
            "id": user["id"],
            "email": user["email"],
            "name": user["given_name"],
            "role": user["role"],
            "picture": user["profile_picture_url"],
        }

    except Exception:
        return render_template('error.html')
    else:
        return redirect("/")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")