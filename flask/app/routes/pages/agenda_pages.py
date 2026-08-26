from flask import Blueprint, flash, redirect, render_template, request, send_file, session, url_for

from services.agenda_pdf_service import AgendaPdfService
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


# Exporta os compromissos do mês selecionado em PDF
@agenda_pages_bp.route("/agenda/pdf", methods=["GET"])
@page_permission_required("agenda")
def export_month_pdf():
    try:
        year = int(request.args.get("ano", ""))
        month = int(request.args.get("mes", ""))
        pdf_file = AgendaPdfService.generate_month(year, month)
    except (TypeError, ValueError) as error:
        flash(str(error), "erro")
        return redirect(url_for("agenda_pages.agenda"))

    return send_file(
        pdf_file,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"agenda-{year}-{month:02d}.pdf",
    )
