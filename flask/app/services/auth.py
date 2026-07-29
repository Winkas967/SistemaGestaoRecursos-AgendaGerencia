from flask import redirect, session, url_for

from model import Usuario


def role_atual():
    return (session.get("role") or "").strip().lower()


def usuario_tecnico():
    return role_atual() == "tecnico"


def usuario_gerencia():
    return role_atual() == "gerencia"


def usuario_rh():
    return role_atual() == "rh"


def usuario_gerencia_ou_rh():
    return role_atual() in ["gerencia", "rh"]


def pode_ver_relatorios():
    return role_atual() in ["gerencia", "rh", "tecnico"]


def pode_ver_historico_geral():
    return role_atual() in ["gerencia", "rh", "tecnico"]


def exigir_tecnico():
    if "usuario" not in session:
        return redirect(url_for("main.login_page"))

    if not usuario_tecnico():
        return "Acesso negado", 403

    return None


def exigir_historico_geral():
    if "usuario" not in session:
        return redirect(url_for("main.login_page"))

    if not pode_ver_historico_geral():
        return "Acesso negado", 403

    return None


def usuario_logado():
    if "usuario" not in session:
        return None

    return Usuario.query.filter_by(usuario=session["usuario"]).first()
