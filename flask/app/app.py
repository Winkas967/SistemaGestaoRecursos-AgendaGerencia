import os
from flask import Flask
from dotenv import load_dotenv

#carrega variaveis do arquivo .env
load_dotenv()

from config import Config

from routes import register_routes
from services.email_notifications_scheduler import start_email_notifications_scheduler

#cria e configura a aplicacao
def create_app():
    #cria a aplicacao Flask
    app = Flask(__name__)
    
    #carrega as config
    app.config.from_object(Config)
    
    #impede o sistema de iniciar sem uma chave secreta
    if not app.config["SECRET_KEY"]:
        raise RuntimeError("SECRET_KEY não foi configurada no arquivo .env.")
    
    #registra blueprints
    register_routes(app)

    #verifica os vencimentos ao iniciar e repete enquanto o sistema estiver ativo
    start_email_notifications_scheduler(app)
    
    #retorna a aplicacao pronta
    return app

#inicia a aplicacao semoente quando este arquivo for executado
if __name__ == "__main__":
    # cria a aplicacao
    app = create_app()
    
    #le as configuracoes do servidor
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "5002"))
    debug = os.getenv("FLASK_DEBUG", "false").lower() in {
        "1",
        "true",
        "sim",
        "on",
    }
    
    #inicia o servidor de desenvolvimento
    app.run(
        host=host,
        port=port,
        debug=debug,
    )
    
