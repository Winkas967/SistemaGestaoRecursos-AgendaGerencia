from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file

from utils.auth import page_permission_required
from services.report_services import ReportService
from services.report_export_service import ReportExportService

# Cria o grupo de páginas de relatórios
reports_pages_bp = Blueprint(
    "reports_pages",
    __name__,
)


# Exibe a página de relatórios
@reports_pages_bp.route("/relatorios", methods=["GET"])
@page_permission_required("relatorios")
def relatorios():
    # Lê os filtros enviados pela página
    filtros = {
        "dataInicio": str(
            request.args.get("dataInicio") or ""
        ).strip(),
        "dataFim": str(
            request.args.get("dataFim") or ""
        ).strip(),
        "setor": str(
            request.args.get("setor") or ""
        ).strip(),
    }

    try:
        stats = ReportService.get_summary(filtros)
        rankings = ReportService.get_rankings(filtros)
        charts = ReportService.get_all_charts(filtros)
        
    except ValueError as error:
        flash(str(error), "erro")
        
        return redirect(
            url_for("reports_pages.relatorios")
        )

    dados_recurso = charts["recurso"]
    dados_setor = charts["setor"]
    dados_status = charts["status"]
    dados_responsavel = charts["responsavel"]
    dados_hora = charts["hora"]
    dados_periodo = charts["periodo"]

    return render_template(
        "relatorios.html",
        tema="light",
        filtros=filtros,
        stats=stats,
        rankings=rankings,
        dados_setor=dados_setor,
        dados_periodo=dados_periodo,
        dados_recurso=dados_recurso,
        dados_status=dados_status,
        dados_hora=dados_hora,
        dados_responsavel=dados_responsavel,
    )
    
    
#exporta os relatorios para excel
@reports_pages_bp.route("/relatorios/exportar/excel", methods=["GET"])
@page_permission_required("relatorios")
def export_excel():
    #le filtros enviados pela pagina
    filtros = {
        "dataInicio": str(
            request.args.get("dataInicio") or ""
        ).strip(),
        
        "dataFim": str(
            request.args.get("dataFim") or ""
        ).strip(),
        
        "setor": str(
            request.args.get("setor") or ""
        ).strip(),
    }
    
    try:
        #cria o arquivo excel na memoria
        excel_file = (
            ReportExportService.generate_excel(
                filtros
            )
        )
    
    except ValueError as error:
        #mostra erro de validacao
        flash(str(error), "erro")
        
        return redirect(url_for("reports_pages.relatorios"))
    
    #envia o arquivo para dowload
    return send_file(
        excel_file,
        mimetype=(
            "apllication/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        ),
        as_attachment=True,
        download_name="relatorio_reserva.xlsx",    
    )
