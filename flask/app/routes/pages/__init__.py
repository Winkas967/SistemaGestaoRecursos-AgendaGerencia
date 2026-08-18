from routes.pages.agenda_pages import agenda_pages_bp
from routes.pages.auth_pages import auth_pages_bp
from routes.pages.home_pages import home_pages_bp
from routes.pages.reports_pages import reports_pages_bp
from routes.pages.resources_pages import resources_pages_bp


# Reúne os blueprints responsáveis por entregar os templates
page_blueprints = (
    auth_pages_bp,
    home_pages_bp,
    resources_pages_bp,
    reports_pages_bp,
    agenda_pages_bp,
)
