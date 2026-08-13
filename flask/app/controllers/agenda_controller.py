from datetime import datetime, timedelta

from io import BytesIO

from flask import jsonify, redirect, render_template, request, send_file, session, url_for
from werkzeug.utils import secure_filename

from conexao import db
from controllers import main
from model import AgendaCompromisso
from services.agenda_pdf import gerar_pdf_agenda_mensal
from services.atas_service import criar_ata, excluir_ata, listar_atas, obter_ata
from services.documentacao_rede_service import (
    atualizar_documentacao_medico,
    atualizar_situacao_medico_credenciado,
    carregar_documentacao_rede,
    criar_medico_credenciado,
    criar_documentacao_medico,
    excluir_documentacao_medico,
    excluir_documentacao_medico_em_lote,
    excluir_medico_credenciado,
    obter_arquivo_descredenciamento,
    obter_arquivo_documentacao,
    salvar_arquivo_documentacao,
)


STATUS_VALIDOS = {"agendado", "andamento", "concluido", "cancelado"}
EXTENSOES_ATAS = {"pdf", "doc", "docx"}
TAMANHO_MAXIMO_ATA = 15 * 1024 * 1024
EXTENSOES_DESCREDENCIAMENTO = {"pdf", "doc", "docx"}
TAMANHO_MAXIMO_DESCREDENCIAMENTO = 15 * 1024 * 1024


def pode_usar_agenda():
    return session.get("role", "").lower() in ["gerencia", "admin"]


def exigir_agenda():
    if "usuario" not in session:
        return redirect(url_for("main.login_page"))

    if not pode_usar_agenda():
        return "Acesso negado", 403

    return None


def compromisso_json(compromisso):
    return {
        "id": compromisso.id,
        "titulo": compromisso.titulo,
        "data": compromisso.data.isoformat(),
        "horaInicio": compromisso.hora_inicio.strftime("%H:%M"),
        "horaFim": compromisso.hora_fim.strftime("%H:%M") if compromisso.hora_fim else "",
        "responsavel": compromisso.responsavel or "",
        "local": compromisso.local or "",
        "descricao": compromisso.descricao or "",
        "status": status_compromisso(compromisso),
    }


def status_compromisso(compromisso):
    status = (compromisso.status or "").strip().lower()
    return status if status in STATUS_VALIDOS else "agendado"


def ler_data(valor):
    return datetime.strptime(valor, "%Y-%m-%d").date()


def ler_hora(valor):
    if not valor:
        return None

    return datetime.strptime(valor, "%H:%M").time()


def erro_json(mensagem, status=400):
    return jsonify({"erro": mensagem}), status


def payload_compromisso():
    dados = request.get_json(silent=True) or request.form

    titulo = (dados.get("titulo") or "").strip()
    data_texto = (dados.get("data") or "").strip()
    hora_inicio_texto = (dados.get("horaInicio") or dados.get("hora_inicio") or "").strip()
    hora_fim_texto = (dados.get("horaFim") or dados.get("hora_fim") or "").strip()
    status = (dados.get("status") or "agendado").strip().lower()

    if not titulo:
        raise ValueError("Informe o titulo do compromisso.")
    if not data_texto:
        raise ValueError("Informe a data do compromisso.")
    if not hora_inicio_texto:
        raise ValueError("Informe a hora de inicio.")
    if status not in STATUS_VALIDOS:
        raise ValueError("Status invalido.")

    data = ler_data(data_texto)
    hora_inicio = ler_hora(hora_inicio_texto)
    hora_fim = ler_hora(hora_fim_texto)

    if not hora_fim:
        hora_fim = (datetime.combine(data, hora_inicio) + timedelta(hours=1)).time().replace(second=0, microsecond=0)

    if hora_fim and hora_fim <= hora_inicio:
        raise ValueError("A hora fim precisa ser maior que a hora de inicio.")

    return {
        "titulo": titulo,
        "data": data,
        "hora_inicio": hora_inicio,
        "hora_fim": hora_fim,
        "responsavel": (dados.get("responsavel") or "").strip() or None,
        "local": (dados.get("local") or "").strip() or None,
        "descricao": (dados.get("descricao") or "").strip() or None,
        "status": status,
    }


def existe_conflito(data, hora_inicio, hora_fim=None, ignorar_id=None):
    fim_novo = hora_fim or hora_inicio

    consulta = AgendaCompromisso.query.filter(
        AgendaCompromisso.data == data,
        AgendaCompromisso.status != "cancelado",
    )

    if ignorar_id:
        consulta = consulta.filter(AgendaCompromisso.id != ignorar_id)

    for compromisso in consulta.all():
        fim_existente = compromisso.hora_fim or compromisso.hora_inicio

        if hora_inicio == fim_novo or compromisso.hora_inicio == fim_existente:
            if hora_inicio == compromisso.hora_inicio:
                return True
            continue

        if hora_inicio < fim_existente and fim_novo > compromisso.hora_inicio:
            return True

    return False


@main.route("/agenda")
def agenda():
    bloqueio = exigir_agenda()
    if bloqueio:
        return bloqueio

    return render_template("agenda.html")


@main.route("/agenda/pdf")
def exportar_agenda_mensal_pdf():
    bloqueio = exigir_agenda()
    if bloqueio:
        return bloqueio

    ano = request.args.get("ano", datetime.now().year, type=int)
    mes = request.args.get("mes", datetime.now().month, type=int)

    if not 1 <= mes <= 12 or not 2000 <= ano <= 2100:
        return "Período inválido", 400

    inicio = datetime(ano, mes, 1).date()
    fim = datetime(ano + 1, 1, 1).date() if mes == 12 else datetime(ano, mes + 1, 1).date()
    compromissos = (
        AgendaCompromisso.query
        .filter(AgendaCompromisso.data >= inicio, AgendaCompromisso.data < fim)
        .order_by(AgendaCompromisso.data.asc(), AgendaCompromisso.hora_inicio.asc())
        .all()
    )

    return gerar_pdf_agenda_mensal(compromissos, ano, mes, status_compromisso)


@main.route("/api/agenda/compromissos", methods=["GET"])
def listar_compromissos_agenda():
    bloqueio = exigir_agenda()
    if bloqueio:
        return bloqueio

    compromissos = (
        AgendaCompromisso.query
        .order_by(AgendaCompromisso.data.asc(), AgendaCompromisso.hora_inicio.asc())
        .all()
    )

    return jsonify([compromisso_json(compromisso) for compromisso in compromissos])


@main.route("/api/agenda/documentacao", methods=["GET"])
def listar_documentacao_rede():
    bloqueio = exigir_agenda()
    if bloqueio:
        return bloqueio

    return jsonify(carregar_documentacao_rede())


@main.route("/api/agenda/documentacao", methods=["POST"])
def criar_documentacao_rede():
    bloqueio = exigir_agenda()
    if bloqueio:
        return bloqueio

    dados = request.get_json(silent=True) or {}
    try:
        registro = criar_documentacao_medico(dados)
    except ValueError as erro:
        return erro_json(str(erro))
    return jsonify(registro), 201


@main.route("/api/agenda/medicos", methods=["POST"])
def criar_medico_documentacao_rede():
    bloqueio = exigir_agenda()
    if bloqueio:
        return bloqueio

    try:
        medico = criar_medico_credenciado(request.get_json(silent=True) or {})
    except ValueError as erro:
        return erro_json(str(erro))

    return jsonify(medico), 201


@main.route("/api/agenda/medicos/<int:id>", methods=["DELETE"])
def excluir_medico_credenciado_rede(id):
    bloqueio = exigir_agenda()
    if bloqueio:
        return bloqueio

    dados = request.get_json(silent=True) or {}
    return jsonify(excluir_medico_credenciado(id, dados.get("ids")))


@main.route("/api/agenda/medicos/<int:id>", methods=["PATCH"])
def atualizar_situacao_medico_documentacao_rede(id):
    bloqueio = exigir_agenda()
    if bloqueio:
        return bloqueio

    arquivo_dados = None
    if request.mimetype == "multipart/form-data":
        dados = request.form.to_dict()
        arquivo = request.files.get("arquivo")
        if arquivo and arquivo.filename:
            nome_seguro = secure_filename(arquivo.filename)
            extensao = nome_seguro.rsplit(".", 1)[-1].lower() if "." in nome_seguro else ""
            if extensao not in EXTENSOES_DESCREDENCIAMENTO:
                return erro_json("Anexe um arquivo PDF, DOC ou DOCX.")
            conteudo = arquivo.read()
            if len(conteudo) > TAMANHO_MAXIMO_DESCREDENCIAMENTO:
                return erro_json("O anexo deve ter no máximo 15 MB.")
            arquivo_dados = {
                "nome": nome_seguro,
                "mime": arquivo.mimetype,
                "dados": conteudo,
            }
    else:
        dados = request.get_json(silent=True) or {}

    try:
        medico = atualizar_situacao_medico_credenciado(
            id,
            dados,
            arquivo_dados,
        )
    except ValueError as erro:
        return erro_json(str(erro))
    return jsonify(medico)


@main.route("/api/agenda/medicos/<int:id>/descredenciamento/arquivo", methods=["GET"])
def baixar_arquivo_descredenciamento_rede(id):
    bloqueio = exigir_agenda()
    if bloqueio:
        return bloqueio

    medico = obter_arquivo_descredenciamento(id)
    if not medico.descredenciamento_arquivo_dados or not medico.descredenciamento_arquivo_nome:
        return erro_json("Este cadastro não possui anexo de descredenciamento.", 404)

    return send_file(
        BytesIO(medico.descredenciamento_arquivo_dados),
        mimetype=medico.descredenciamento_arquivo_mime or "application/octet-stream",
        as_attachment=True,
        download_name=medico.descredenciamento_arquivo_nome,
    )


@main.route("/api/agenda/documentacao/<int:id>", methods=["PATCH"])
def atualizar_documentacao_rede(id):
    bloqueio = exigir_agenda()
    if bloqueio:
        return bloqueio

    dados = request.get_json(silent=True) or {}
    try:
        registro = atualizar_documentacao_medico(id, dados)
    except ValueError as erro:
        return erro_json(str(erro))
    return jsonify(registro)


@main.route("/api/agenda/documentacao/<int:id>/arquivo", methods=["POST"])
def anexar_arquivo_documentacao_rede(id):
    bloqueio = exigir_agenda()
    if bloqueio:
        return bloqueio

    arquivo = request.files.get("arquivo")
    if not arquivo or not arquivo.filename:
        return erro_json("Selecione um arquivo.")

    nome = secure_filename(arquivo.filename)
    if not nome:
        return erro_json("Nome de arquivo inválido.")

    dados = arquivo.read(10 * 1024 * 1024 + 1)
    if len(dados) > 10 * 1024 * 1024:
        return erro_json("O arquivo deve ter no máximo 10 MB.", 413)
    if not dados:
        return erro_json("O arquivo está vazio.")

    registro = salvar_arquivo_documentacao(
        id,
        nome,
        arquivo.mimetype or "application/octet-stream",
        dados,
    )
    return jsonify(registro)


@main.route("/api/agenda/documentacao/<int:id>/arquivo", methods=["GET"])
def baixar_arquivo_documentacao_rede(id):
    bloqueio = exigir_agenda()
    if bloqueio:
        return bloqueio

    registro = obter_arquivo_documentacao(id)
    if not registro.arquivo_nome or not registro.arquivo_dados:
        return erro_json("Este documento não possui arquivo anexado.", 404)

    return send_file(
        BytesIO(registro.arquivo_dados),
        mimetype=registro.arquivo_mime or "application/octet-stream",
        as_attachment=True,
        download_name=registro.arquivo_nome,
    )


@main.route("/api/agenda/documentacao/<int:id>", methods=["DELETE"])
def excluir_documentacao_rede(id):
    bloqueio = exigir_agenda()
    if bloqueio:
        return bloqueio

    return jsonify(excluir_documentacao_medico(id))


@main.route("/api/agenda/documentacao/medico", methods=["DELETE"])
def excluir_medico_documentacao_rede():
    bloqueio = exigir_agenda()
    if bloqueio:
        return bloqueio

    dados = request.get_json(silent=True) or {}
    return jsonify(excluir_documentacao_medico_em_lote(dados.get("ids")))


@main.route("/api/agenda/atas", methods=["GET"])
def listar_atas_reunioes():
    bloqueio = exigir_agenda()
    if bloqueio:
        return bloqueio
    return jsonify(listar_atas())


@main.route("/api/agenda/atas", methods=["POST"])
def adicionar_ata_reuniao():
    bloqueio = exigir_agenda()
    if bloqueio:
        return bloqueio

    arquivo = request.files.get("arquivo")
    if not arquivo or not arquivo.filename:
        return erro_json("Selecione o arquivo da ata.")

    nome = secure_filename(arquivo.filename)
    extensao = nome.rsplit(".", 1)[-1].lower() if "." in nome else ""
    if extensao not in EXTENSOES_ATAS:
        return erro_json("O arquivo deve estar no formato PDF, DOC ou DOCX.")

    conteudo = arquivo.read(TAMANHO_MAXIMO_ATA + 1)
    if len(conteudo) > TAMANHO_MAXIMO_ATA:
        return erro_json("O arquivo da ata deve ter no máximo 15 MB.", 413)
    if not conteudo:
        return erro_json("O arquivo selecionado está vazio.")

    try:
        ata = criar_ata(
            request.form,
            nome,
            arquivo.mimetype or "application/octet-stream",
            conteudo,
        )
    except ValueError as erro:
        return erro_json(str(erro))
    return jsonify(ata), 201


@main.route("/api/agenda/atas/<int:id>/arquivo", methods=["GET"])
def baixar_arquivo_ata(id):
    bloqueio = exigir_agenda()
    if bloqueio:
        return bloqueio

    ata = obter_ata(id)
    return send_file(
        BytesIO(ata.arquivo_dados),
        mimetype=ata.arquivo_mime or "application/octet-stream",
        as_attachment=True,
        download_name=ata.arquivo_nome,
    )


@main.route("/api/agenda/atas/<int:id>", methods=["DELETE"])
def excluir_ata_reuniao(id):
    bloqueio = exigir_agenda()
    if bloqueio:
        return bloqueio
    return jsonify(excluir_ata(id))


@main.route("/api/agenda/compromissos", methods=["POST"])
def criar_compromisso_agenda():
    bloqueio = exigir_agenda()
    if bloqueio:
        return bloqueio

    try:
        dados = payload_compromisso()
    except ValueError as erro:
        return erro_json(str(erro))

    if dados["status"] != "cancelado" and existe_conflito(
        dados["data"], dados["hora_inicio"], dados["hora_fim"]
    ):
        return erro_json("Ja existe compromisso nesse dia e horario.", 409)

    compromisso = AgendaCompromisso(**dados, criado_por_id=session.get("usuario_id"))
    db.session.add(compromisso)
    db.session.commit()

    return jsonify(compromisso_json(compromisso)), 201


@main.route("/api/agenda/compromissos/<int:id>", methods=["PUT"])
def atualizar_compromisso_agenda(id):
    bloqueio = exigir_agenda()
    if bloqueio:
        return bloqueio

    compromisso = AgendaCompromisso.query.get_or_404(id)

    try:
        dados = payload_compromisso()
    except ValueError as erro:
        return erro_json(str(erro))

    if dados["status"] != "cancelado" and existe_conflito(
        dados["data"], dados["hora_inicio"], dados["hora_fim"], ignorar_id=id
    ):
        return erro_json("Ja existe compromisso nesse dia e horario.", 409)

    for campo, valor in dados.items():
        setattr(compromisso, campo, valor)

    compromisso.atualizado_em = datetime.now()
    db.session.commit()

    return jsonify(compromisso_json(compromisso))


@main.route("/api/agenda/compromissos/<int:id>/status", methods=["PATCH"])
def atualizar_status_compromisso_agenda(id):
    bloqueio = exigir_agenda()
    if bloqueio:
        return bloqueio

    dados = request.get_json(silent=True) or {}
    status = (dados.get("status") or "").strip().lower()

    if status not in STATUS_VALIDOS:
        return erro_json("Status invalido.")

    compromisso = AgendaCompromisso.query.get_or_404(id)

    if status != "cancelado" and existe_conflito(
        compromisso.data,
        compromisso.hora_inicio,
        compromisso.hora_fim,
        ignorar_id=id,
    ):
        return erro_json("Ja existe compromisso nesse dia e horario.", 409)

    compromisso.status = status
    compromisso.atualizado_em = datetime.now()
    db.session.commit()

    return jsonify(compromisso_json(compromisso))


@main.route("/api/agenda/compromissos/<int:id>", methods=["DELETE"])
def excluir_compromisso_agenda(id):
    bloqueio = exigir_agenda()
    if bloqueio:
        return bloqueio

    compromisso = AgendaCompromisso.query.get_or_404(id)
    db.session.delete(compromisso)
    db.session.commit()

    return jsonify({"ok": True})
