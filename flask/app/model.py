from conexao import db

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), nullable=False)
    senha = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="usuario")

class DataShow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    responsavel = db.Column(db.String(100), nullable=True)
    requerente = db.Column(db.String(100), nullable=True)
    data = db.Column(db.Date, nullable=True)
    horaInicio = db.Column(db.String(100), nullable=True)
    setor = db.Column(db.String(100), nullable=True)
    localUso = db.Column(db.String(100), nullable=True)
    observacao = db.Column(db.String(255), nullable=True)
