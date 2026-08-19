from flask import Blueprint, render_template, session

from utils.auth import page_permission_required
from services.resources_services import ResourceService

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
    )


# Exibe a página de reservas
@resources_pages_bp.route("/reserva", methods=["GET"])
@page_permission_required("recursos")
def reserva():
    return render_template("reserva.html", tema="light")
