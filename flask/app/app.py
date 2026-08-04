from flask import Flask
from dotenv import load_dotenv

load_dotenv()

from conexao import db
from route import main
from services.passwords import proteger_senhas_existentes
from services.email_scheduler import iniciar_agendador_email
from services.usuarios_email import garantir_coluna_email_usuario
from waitress import serve

app = Flask(__name__)

app.secret_key = "minha_chave_super_secreta"

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:1234@localhost:3306/gestaorecursos"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

app.register_blueprint(main)

with app.app_context():
    db.create_all()
    garantir_coluna_email_usuario()
    proteger_senhas_existentes()


if __name__ == "__main__":
    iniciar_agendador_email(app)
    app.run(debug=True, use_reloader=False)
    # serve(app, host='0.0.0.0', port=5002)
