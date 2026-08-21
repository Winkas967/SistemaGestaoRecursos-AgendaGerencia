from flask import Blueprint, redirect, render_template, session, url_for

from services.sector_permissions_service import SectorPermissionService
from services.users_service import UserService
from services.reservations_service import ReservationService


# Cria o grupo de páginas da área inicial
home_pages_bp = Blueprint(
    "home_pages",
    __name__,
)


# Exibe a página inicial somente para usuários autenticados
@home_pages_bp.route("/home", methods=["GET"])
def home():
    if not session.get("user_id"):
        return redirect(url_for("auth_pages.login_page"))

    users = []
    sectors = []
    roles = []
    sector_permission_panels = []
    visible_modules = {
        permission.get("modulo_codigo")
        for permission in session.get("permissions", [])
        if permission.get("pode_visualizar")
    }

    # Carrega os dados administrativos somente para o administrador
    if str(session.get("role") or "").lower() == "admin":
        users = UserService.get_all()
        options = UserService.get_form_options()
        sectors = options["setores"]
        roles = options["roles"]
        modules = SectorPermissionService.get_modules()

        # Organiza as permissões para facilitar a exibição no HTML
        for sector in sectors:
            saved_permissions = SectorPermissionService.get_by_sector(
                sector["id"]
            )
            permissions_by_module = {
                permission["modulo_id"]: permission
                for permission in saved_permissions
            }
            permission_rows = []

            for module in modules:
                permission_rows.append({
                    "modulo": module,
                    "permissao": permissions_by_module.get(
                        module["id"],
                        {},
                    ),
                })

            sector_permission_panels.append({
                "setor": sector,
                "linhas": permission_rows,
            })
        
    #verifica se um usuario e admin
    is_admin = (
        str(session.get("role") or "").lower()
        == "admin"
    )
    
    #busca as reservas exibidas na pag inicial
    reservations = ReservationService.get_for_home(
        user_id=session.get("user_id"),
        is_admin=is_admin,
    )
    
    #separa os agendamentos que ainda podem ser fechados
    open_reservations = [
        reservation
        for reservation in reservations["items"]
        if reservation["status"] in ("reservado", "em_uso")
    ]

    return render_template(
        "home.html",
        tema="light",
        agendamentos=reservations,
        emprestimos_abertos=open_reservations,
        usuarios=users,
        setores=sectors,
        roles=roles,
        paineis_permissoes=sector_permission_panels,
        modulos_visiveis=visible_modules,
    )
