from flask import Blueprint, render_template

from utils.auth import page_permission_required


# Cria o grupo de páginas de relatórios
reports_pages_bp = Blueprint(
    "reports_pages",
    __name__,
)


# Exibe a página de relatórios
@reports_pages_bp.route("/relatorios", methods=["GET"])
@page_permission_required("relatorios")
def relatorios():
    return render_template("relatorios.html", tema="light")
