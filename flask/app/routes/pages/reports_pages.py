from flask import Blueprint, render_template

from utils.auth import page_permission_required
from services.report_services import ReportService


# Cria o grupo de páginas de relatórios
reports_pages_bp = Blueprint(
    "reports_pages",
    __name__,
)


# Exibe a página de relatórios
@reports_pages_bp.route("/relatorios", methods=["GET"])
@page_permission_required("relatorios")
def relatorios():
    stats = {
        "total": 0,
        "pendentes": 0,
        "atrasados": 0,
        "taxaDevolucao": 0,
        "recursoTop": "-",
        "setorTop": "-",
        "mediaDiaria": 0,
        "diasComUso": 0,
        "emUso": 0,
        "reservados": 0,
        "viagens": 0,
        "devolvidos": 0,
    }
    
    rankings = {
        "recursos": [],
        "setores": [],
        "responsaveis": [],
    }
    
    filtros = {
        "dataInicio": "",
        "dataFim": "",
        "setor": "",
    }
    
    #busca dados do grafico de recursos
    dados_recurso = (
        ReportService.get_reservations_by_resource()
    )
    
    return render_template(
        "relatorios.html",
        tema="light",
        filtros=filtros,
        stats=stats,
        rankings=rankings,
        dados_setor=None,
        dados_periodo=None,
        dados_recurso=dados_recurso,
        dados_status=None,
        dados_hora=None,
        dados_responsavel=None
        )

