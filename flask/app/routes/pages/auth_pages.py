from flask import Blueprint, redirect, render_template, session, url_for


# Cria o grupo de páginas de autenticação
auth_pages_bp = Blueprint(
    "auth_pages",
    __name__,
)


# Exibe a página de login
@auth_pages_bp.route("/", methods=["GET"])
def login_page():
    if session.get("user_id"):
        return redirect(url_for("home_pages.home"))

    return render_template(
        "login.html",
        tema="light",
    )
