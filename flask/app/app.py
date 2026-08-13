import os
import secrets

from flask import Flask
from dotenv import load_dotenv

load_dotenv()

from conexao import db
from route import main
from services.passwords import proteger_senhas_existentes
from services.email_scheduler import iniciar_agendador_email
from services.usuarios_email import garantir_coluna_email_usuario
from services.documentacao_rede_service import garantir_coluna_descredenciado_medico
from waitress import serve

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY") or secrets.token_hex(32)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:1234@localhost:3306/gestaorecursos",
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 1800,
}
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.getenv(
    "SESSION_COOKIE_SECURE", "false"
).strip().lower() in {"1", "true", "sim", "on"}

db.init_app(app)

app.register_blueprint(main)

with app.app_context():
    db.create_all()
    garantir_coluna_email_usuario()
    garantir_coluna_descredenciado_medico()
    proteger_senhas_existentes()


if __name__ == "__main__":
    iniciar_agendador_email(app)
    debug = os.getenv("FLASK_DEBUG", "false").strip().lower() in {"1", "true", "sim", "on"}
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5002"))
    if debug:
        app.run(host=host, port=port, debug=True, use_reloader=False)
    else:
        serve(app, host=host, port=port)
