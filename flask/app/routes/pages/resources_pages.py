from flask import Blueprint, render_template, request, session

from utils.auth import page_permission_required
from services.resources_services import ResourceService
from services.reservations_service import ReservationService
from services.sectors_service import SectorService

# Cria o grupo de páginas de recursos e reservas
resources_pages_bp = Blueprint(
    "resources_pages",
    __name__,
)


# Exibe a página de equipamentos
@resources_pages_bp.route("/equipamentos", methods=["GET"])
@page_permission_required("recursos")
def equipamentos():
    resources = ResourceService.get_all()
    options = ResourceService.get_form_options()
    
    available_resources = [
        resource
        for resource in resources
        if resource["status"] == "disponivel"
    ]
    
    resource_permission = next(
        (
            permission
            for permission in session.get("permissions", [])
            if permission.get("modulo_codigo") == "recursos"
        ),
        {},
    )
    
    is_admin = (
        str(session.get("role") or "").lower() == "admin"
    )
    
    can_create_resource = (
        is_admin
        or resource_permission.get("pode_criar", False)
    )
    
    can_edit_resource = (
        is_admin
        or resource_permission.get("pode_editar", False)
    )
    
    can_delete_resource = (
        is_admin
        or resource_permission.get("pode_excluir", False)
    )
    
    #lista os modulos que o usuario pode visualizar
    visible_modules = {
        permission.get("modulo_codigo")
        for permission in session.get("permissions", [])
        if permission.get("pode_visualizar")
    }
    
    return render_template(
        "equipamentos.html", 
        tema="light", 
        recursos=resources, 
        recursos_disponiveis=available_resources, 
        recursos_gerencia=resources,
        tipos_recursos=options["tipos_recursos"],
        pode_criar_recurso=can_create_resource,
        pode_editar_recurso=can_edit_resource,
        pode_excluir_recurso=can_delete_resource,
        modulos_visiveis=visible_modules
    )


# Exibe a página de reservas
@resources_pages_bp.route("/reserva", methods=["GET"])
@page_permission_required("recursos")
def reserva():
    #busca somente os recursos disponiveis 
    resources = [
        resource
        for resource in ResourceService.get_all()
        if resource["status"] == "disponivel"
    ]
    
    #verifica se o usuario é admin
    is_admin = (
        str(session.get("role") or "").lower()
        == "admin"
    )
    
    #busca os setores cadastrados
    sectors = SectorService.get_all()
    
    #funcionarios visualizam somente o proprio setor
    if not is_admin:
        user_sector_id = session.get("setor_id")
        
        sectors = [
            sector
            for sector in sectors
            if sector["id"] == user_sector_id
        ]
        
    #obtem o recurso selecionado pela url
    selected_resource_id = request.args.get(
        "recurso_id",
        type=int,
    )
    
    #localiza os dados do recurso selecionado
    selected_resource = next(
        (
            resource
            for resource in resources
            if resource["id"] == selected_resource_id
        ),
        None,
    )
    
    #mantem a agenda vazia quando nenhum recurso foi realizado
    schedule = []
    
    #busca a agenda do recurso selecionado
    if selected_resource:
        schedule = ReservationService.get_schedule_by_resource(
            selected_resource["id"]
        )
        
        #lista os modulos que o usuario pode visualizar
    visible_modules = {
        permission.get("modulo_codigo")
        for permission in session.get("permissions", [])
        if permission.get("pode_visualizar")
    }
    
    return render_template(
        "reserva.html",
        tema="light",
        recursos=resources,
        setores=sectors,
        recurso_selecionado=selected_resource,
        agenda_ocupada=schedule,
        pode_viagem=True,
        modulos_visiveis=visible_modules
        )
