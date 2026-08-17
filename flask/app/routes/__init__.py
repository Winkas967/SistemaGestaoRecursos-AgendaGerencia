from routes.system_routes import system_bp
from routes.auth_routes import auth_bp
from routes.sectors_routes import sectors_bp
from routes.sector_permissions_routes import sector_permissions_bp

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