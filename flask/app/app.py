from flask import Flask

from conexao import db
from route import main
from waitress import serve

app = Flask(__name__)

app.secret_key = "minha_chave_super_secreta"

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:1234@localhost:5432/gestaorecursos"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

app.register_blueprint(main)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    # app.run(debug=True)
    serve(app, host='0.0.0.0', port=5000)