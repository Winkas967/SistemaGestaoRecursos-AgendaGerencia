from flask import Blueprint, render_template

from utils.auth import page_permission_required


# Cria o grupo de páginas de recursos e reservas
resources_pages_bp = Blueprint(
    "resources_pages",
    __name__,
)


# Exibe a página de equipamentos
@resources_pages_bp.route("/equipamentos", methods=["GET"])
@page_permission_required("recursos")
def equipamentos():
    return render_template("equipamentos.html", tema="light")


# Exibe a página de reservas
@resources_pages_bp.route("/reserva", methods=["GET"])
@page_permission_required("recursos")
def reserva():
    return render_template("reserva.html", tema="light")
