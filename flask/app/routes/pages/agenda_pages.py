from flask import Blueprint, render_template, session

from utils.auth import page_permission_required


# Cria o grupo de páginas de agenda, documentação e atas
agenda_pages_bp = Blueprint(
    "agenda_pages",
    __name__,
)


# Exibe a página da agenda
@agenda_pages_bp.route("/agenda", methods=["GET"])
@page_permission_required("agenda", "documentacao", "atas")
def agenda():
    visible_modules = {
        permission.get("modulo_codigo")
        for permission in session.get("permissions", [])
        if permission.get("pode_visualizar")
    }
    initial_view = next(
        (
            module_code
            for module_code in ("agenda", "documentacao", "atas")
            if module_code in visible_modules
        ),
        "agenda",
    )

    return render_template(
        "agenda.html",
        tema="light",
        modulos_visiveis=visible_modules,
        visualizacao_inicial=initial_view,
    )
