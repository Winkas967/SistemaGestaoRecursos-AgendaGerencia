from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models.roles_model import RoleModel
from models.sectors_model import SectorModel
from services.users_service import UserService


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


# Exibe e processa o cadastro público de usuários employee
@auth_pages_bp.route("/cadastro", methods=["GET", "POST"])
def cadastro_page():
    sectors = SectorModel.get_all()

    if request.method == "POST":
        employee_role = RoleModel.get_by_name("employee")
        if not employee_role or not employee_role.ativo:
            flash("O cadastro está temporariamente indisponível.", "erro")
        else:
            try:
                UserService.create({
                    "usuario": request.form.get("usuario"),
                    "senha": request.form.get("senha"),
                    "role_id": employee_role.id,
                    "setor_id": request.form.get("setor_id"),
                })
                flash("Cadastro realizado. Você já pode entrar.", "sucesso")
                return redirect(url_for("auth_pages.login_page"))
            except ValueError as error:
                flash(str(error), "erro")

    return render_template(
        "cadastro.html",
        tema="light",
        setores=sectors,
    )
