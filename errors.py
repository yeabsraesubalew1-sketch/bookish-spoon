from flask import render_template, jsonify
from db.models import is_session_set
from flask import session


def register_error_handlers(app):

    @app.errorhandler(404)
    def page_not_found(e):
        error = {
            "error": "Page Not Found",
            "error_message": str(e),
            "error_code": "404"
        }

        if is_session_set():
            return render_template(
                "error.html",
                title="Not Found",
                error=error,
                user=session.get("user")
            )

        return render_template(
            "error.html",
            title="Not Found",
            error=error
        )


    @app.errorhandler(405)
    def method_not_allowed(e):
        error = {
            "error": "Method Not Allowed",
            "error_message": str(e),
            "error_code": "405"
        }

        if is_session_set():
            return render_template(
                "error.html",
                title="Unavailable Method",
                error=error,
                user=session.get("user")
            )

        return render_template(
            "error.html",
            title="Unavailable Method",
            error=error
        )


    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify({
            "error": "Server Error",
            "error_message": str(e)
        }), 500