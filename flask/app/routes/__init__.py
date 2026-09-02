from routes.system_routes import system_bp
from routes.auth_routes import auth_bp
from routes.sectors_routes import sectors_bp
from routes.sector_permissions_routes import sector_permissions_bp
from routes.users_routes import users_bp
from routes.pages import page_blueprints
from routes.resources_routes import resources_bp
from routes.reservations_routes import reservations_bp
from routes.agenda_routes import agenda_bp
from routes.minutes_routes import minutes_bp
from routes.documents_routes import documents_bp
from routes.providers_routes import providers_bp
from routes.settings_routes import settings_bp
from routes.evaluations_routes import evaluations_bp

#registra todos os blueprints na aplicacao
def register_routes(app):
    #registra as rotas de diagnostico
    app.register_blueprint(system_bp)
    
    #registra as rotas de autenticacao
    app.register_blueprint(auth_bp)
    
    #registra as rotas administraticas dos setores
    app.register_blueprint(sectors_bp)
    
    #registra as rotas administrativas das permissoes
    app.register_blueprint(sector_permissions_bp)
    
    #registra as rotas administrativas dos usuarios
    app.register_blueprint(users_bp)
    
    #registra as rotas da gestao de recursos
    app.register_blueprint(resources_bp)
    
    #registra as rotas de reservas
    app.register_blueprint(reservations_bp)
    
    #registra as rotas dos compromissos da agenda
    app.register_blueprint(agenda_bp)
    
    #registra as rotas das atas
    app.register_blueprint(minutes_bp)

    #registra as rotas da documentacao
    app.register_blueprint(documents_bp)

    #registra as rotas dos prestadores
    app.register_blueprint(providers_bp)
    
    #registra as rotas das configuracoes gerais
    app.register_blueprint(settings_bp)
    
    #registra as rotas das avaliacoes
    app.register_blueprint(evaluations_bp)
    
    #registra as rotas que entregam os templates
    for blueprint in page_blueprints:
        app.register_blueprint(blueprint)
