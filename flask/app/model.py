from datetime import datetime

from conexao import db

class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(100), nullable=False)
    senha = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="usuario")

    reservas = db.relationship("Reserva", back_populates="usuario")


class TipoRecurso(db.Model):
    __tablename__ = "tipos_recursos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    recursos = db.relationship("Recurso", back_populates="tipo_recurso")


class Setor(db.Model):
    __tablename__ = "setores"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)


class Recurso(db.Model):
    __tablename__ = "recursos"

    id = db.Column(db.Integer, primary_key=True)
    tipo_recurso_id = db.Column(db.Integer, db.ForeignKey("tipos_recursos.id"), nullable=False)
    nome = db.Column(db.String(120), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), nullable=False, default="disponivel")
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    tipo_recurso = db.relationship("TipoRecurso", back_populates="recursos")
    reservas = db.relationship("Reserva", back_populates="recurso")


class Reserva(db.Model):
    __tablename__ = "reservas"

    id = db.Column(db.Integer, primary_key=True)
    recurso_id = db.Column(db.Integer, db.ForeignKey("recursos.id"), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    responsavel = db.Column(db.String(100), nullable=True)
    setor = db.Column(db.String(100), nullable=True)
    motivo = db.Column(db.String(150), nullable=True)
    data_reserva = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fim = db.Column(db.Time, nullable=True)
    observacao = db.Column(db.Text, nullable=True)
    viagem = db.Column(db.Boolean, nullable=False, default=False)
    status = db.Column(db.String(30), nullable=False, default="reservado")
    criado_em = db.Column(db.DateTime, server_default=db.func.current_timestamp(), nullable=False)
    atualizado_em = db.Column(db.DateTime, nullable=True)

    recurso = db.relationship("Recurso", back_populates="reservas")
    usuario = db.relationship("Usuario", back_populates="reservas")

    @property
    def inicio_datetime(self):
        return datetime.combine(self.data_reserva, self.hora_inicio)

    @property
    def fim_datetime(self):
        if not self.hora_fim:
            return None

        return datetime.combine(self.data_reserva, self.hora_fim)

    @property
    def devolucao_iso(self):
        if not self.fim_datetime:
            return ""

        return self.fim_datetime.isoformat(timespec="minutes")

    @property
    def status_calculado(self):
        if self.status in ["devolvido", "cancelado"]:
            return self.status

        agora = datetime.now()

        if self.viagem and not self.hora_fim:
            return "viagem"

        if self.fim_datetime and agora > self.fim_datetime:
            return "atrasado"

        if agora >= self.inicio_datetime:
            return "usando"

        return "reservado"

    @property
    def status_label(self):
        labels = {
            "reservado": "Reservado",
            "usando": "Usando",
            "atrasado": "Atrasado",
            "devolvido": "Devolvido",
            "cancelado": "Cancelado",
            "viagem": "Viagem",
        }

        return labels.get(self.status_calculado, self.status_calculado.title())
