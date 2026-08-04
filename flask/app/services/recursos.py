from unicodedata import normalize

from conexao import db
from model import Recurso, Setor
from services.auth import role_atual, usuario_tecnico


def normalizar_texto(texto):
    return normalize("NFKD", texto or "").encode("ascii", "ignore").decode("ascii").strip().lower()


def recurso_eh_veiculo(recurso):
    if not recurso or not recurso.tipo_recurso:
        return False

    tipo = normalizar_texto(recurso.tipo_recurso.nome)
    return tipo.startswith("veiculo")


def recurso_eh_auditorio(recurso):
    if not recurso or not recurso.tipo_recurso:
        return False

    tipo = normalizar_texto(recurso.tipo_recurso.nome)
    return tipo.startswith("auditorio")


def recurso_controlado_pela_gerencia(recurso):
    if not recurso or not recurso.tipo_recurso:
        return False

    return recurso_eh_auditorio(recurso) or recurso_eh_veiculo(recurso)


def recurso_eh_creta(recurso):
    if not recurso:
        return False

    nome = normalizar_texto(recurso.nome)
    return nome == "creta" or nome.startswith("creta ")


def recurso_visivel_para_perfil(recurso):
    role = role_atual()

    if recurso_eh_creta(recurso):
        return role in ["gerencia", "tecnico", "admin"]

    if usuario_tecnico():
        return True

    if role == "user":
        return recurso_eh_veiculo(recurso)

    if role == "gerencia":
        return recurso_controlado_pela_gerencia(recurso)

    if role == "rh":
        return recurso_eh_veiculo(recurso)

    return False


def filtrar_recursos_por_perfil(recursos):
    return [recurso for recurso in recursos if recurso_visivel_para_perfil(recurso)]


def recurso_disponivel_para_reserva(recurso):
    if not recurso or not recurso.ativo:
        return False

    return normalizar_texto(recurso.status) == "disponivel"


def consulta_recursos_disponiveis():
    return (
        Recurso.query.filter_by(ativo=True)
        .filter(db.func.lower(db.func.trim(Recurso.status)) == "disponivel")
        .order_by(Recurso.nome.asc())
    )


def recursos_disponiveis_do_perfil():
    return filtrar_recursos_por_perfil(consulta_recursos_disponiveis().all())


def consulta_setores_ativos():
    return Setor.query.filter_by(ativo=True).order_by(Setor.nome.asc())
