from datetime import date, datetime, timedelta
import re
from sqlalchemy import inspect, text

from conexao import db
from model import DocumentacaoMedicoCredenciado, MedicoCredenciado


COLUNAS_MEDICO_CREDENCIADO = [
    "NOME DO MÉDICO CREDENCIADO",
    "DOCUMENTO",
    "DATA DE VENCIMENTO",
    "DATA MÁXIMA PARA NOTIFICAÇÃO",
    "STATUS",
    "STATUS 60 DIAS DE ATRASO",
    "",
    "Documentação",
]
CAMPOS_TEXTO = {"nome_medico", "documento", "documentacao"}
CAMPOS_DATA = {"data_vencimento", "data_maxima_notificacao"}
STATUS_PRE_DEFINIDOS = {"CONFORME", "PENDENTE", "NOTIFICADO"}
TIPOS_PRE_DEFINIDOS = {"credenciado", "cooperado", "laboratorio", "hospital"}


def garantir_coluna_tipo_medico():
    db.create_all()
    colunas = {coluna["name"] for coluna in inspect(db.engine).get_columns("medicos_credenciados")}
    if "tipo" in colunas:
        return

    db.session.execute(text(
        "ALTER TABLE medicos_credenciados "
        "ADD COLUMN tipo VARCHAR(20) NOT NULL DEFAULT 'credenciado'"
    ))
    db.session.commit()


def garantir_colunas_arquivo_documentacao():
    db.create_all()
    nome_tabela = "documentacao_medicos_credenciados"
    colunas = {coluna["name"] for coluna in inspect(db.engine).get_columns(nome_tabela)}
    alteracoes = {
        "arquivo_nome": "ADD COLUMN arquivo_nome VARCHAR(255) NULL",
        "arquivo_mime": "ADD COLUMN arquivo_mime VARCHAR(120) NULL",
        "arquivo_dados": "ADD COLUMN arquivo_dados MEDIUMBLOB NULL",
    }
    for coluna, comando in alteracoes.items():
        if coluna not in colunas:
            db.session.execute(text(f"ALTER TABLE {nome_tabela} {comando}"))
    db.session.commit()


def limpar_texto(valor):
    if valor is None:
        return ""

    return str(valor).strip()


def percentual_para_texto(conformes, total):
    if total <= 0:
        return "0,00%"

    percentual = (conformes / total) * 100
    return f"{percentual:.2f}".replace(".", ",") + "%"


def ler_data_vencimento(valor):
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor

    texto = limpar_texto(valor)
    if not texto:
        return None

    formatos = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%m-%d-%Y"]
    for formato in formatos:
        try:
            return datetime.strptime(texto[:10], formato).date()
        except ValueError:
            pass

    encontrado = re.search(r"(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})", texto)
    if encontrado:
        dia, mes, ano = encontrado.groups()
        if len(ano) == 2:
            ano = "20" + ano
        try:
            return date(int(ano), int(mes), int(dia))
        except ValueError:
            return None

    return None


def calcular_status_automatico(data_vencimento, sem_validade=False):
    if sem_validade:
        return "CONFORME"

    data = ler_data_vencimento(data_vencimento)
    if not data:
        return "PENDENTE"

    hoje = date.today()
    if data < hoje:
        return "PENDENTE"
    return "CONFORME"


def aplicar_status_automatico(registro):
    status_atual = limpar_texto(registro.status).upper()

    if registro.sem_validade or registro.data_vencimento is None:
        registro.sem_validade = True
        registro.status = "CONFORME"
        registro.status_manual = False
        return

    if registro.status_manual and status_atual in STATUS_PRE_DEFINIDOS:
        registro.status = status_atual
        return

    registro.status = calcular_status_automatico(registro.data_vencimento, registro.sem_validade)
    registro.status_manual = False


def data_para_texto(valor):
    return valor.isoformat() if valor else ""


def registro_json(registro, medico_nome=None):
    nome = medico_nome if medico_nome is not None else (registro.nome_medico or "")
    valores = [
        nome,
        registro.documento or "",
        data_para_texto(registro.data_vencimento),
        data_para_texto(registro.data_maxima_notificacao),
        registro.status or "",
        "MANUAL" if registro.status_manual else "",
        "",
        registro.documentacao or "",
    ]

    return {
        "id": registro.id,
        "linha": None,
        "valores": valores,
        "nome": valores[0],
        "medico": nome,
        "documento": valores[1],
        "status": valores[4],
        "status60": valores[5],
        "semValidade": bool(registro.sem_validade),
        "documentacao": valores[7],
        "arquivo": {
            "nome": registro.arquivo_nome,
            "url": f"/api/agenda/documentacao/{registro.id}/arquivo",
        } if registro.arquivo_nome and registro.arquivo_dados else None,
    }


def carregar_documentacao_rede():
    db.create_all()
    garantir_coluna_tipo_medico()
    garantir_colunas_arquivo_documentacao()

    registros = (
        DocumentacaoMedicoCredenciado.query
        .order_by(DocumentacaoMedicoCredenciado.nome_medico.asc(), DocumentacaoMedicoCredenciado.id.asc())
        .all()
    )
    for registro in registros:
        if registro.data_vencimento and registro.data_maxima_notificacao is None:
            registro.data_maxima_notificacao = registro.data_vencimento + timedelta(days=60)
        if registro.data_vencimento is None:
            registro.sem_validade = True
        aplicar_status_automatico(registro)
    db.session.commit()

    registros_json = []
    medico_atual = ""
    for registro in registros:
        if registro.nome_medico:
            medico_atual = registro.nome_medico

        registros_json.append(registro_json(registro, medico_atual or "Sem médico informado"))
    total = len(registros_json)
    conformes = sum(1 for item in registros_json if item["status"].strip().upper() == "CONFORME")
    pendentes = sum(1 for item in registros_json if item["status"].strip().upper() == "PENDENTE")
    notificados = sum(1 for item in registros_json if item["status"].strip().upper() == "NOTIFICADO")
    status60 = sum(1 for item in registros_json if item["status60"].strip())

    medicos_cadastrados = MedicoCredenciado.query.order_by(MedicoCredenciado.nome.asc()).all()

    return {
        "colunas": COLUNAS_MEDICO_CREDENCIADO,
        "titulo": "Documentação da Rede Prestadora",
        "percentualLabel": "Porcentagem de Documentação Atualizada",
        "percentualValor": conformes / total if total else 0,
        "percentualTexto": percentual_para_texto(conformes, total),
        "registros": registros_json,
        "medicos": [
            {"id": medico.id, "nome": medico.nome, "tipo": medico.tipo}
            for medico in medicos_cadastrados
        ],
        "resumo": {
            "total": total,
            "conformes": conformes,
            "pendentes": pendentes,
            "notificados": notificados,
            "status60": status60,
        },
    }


def criar_medico_credenciado(dados):
    db.create_all()
    garantir_coluna_tipo_medico()

    nome = limpar_texto((dados or {}).get("nome"))
    tipo = limpar_texto((dados or {}).get("tipo")).lower() or "credenciado"
    if not nome:
        raise ValueError("Informe o nome do médico.")
    if tipo not in TIPOS_PRE_DEFINIDOS:
        raise ValueError("Categoria inválida.")

    existente = MedicoCredenciado.query.filter(
        db.func.lower(MedicoCredenciado.nome) == nome.lower()
    ).first()
    nome_em_documentos = DocumentacaoMedicoCredenciado.query.filter(
        db.func.lower(DocumentacaoMedicoCredenciado.nome_medico) == nome.lower()
    ).first()
    if existente or nome_em_documentos:
        raise ValueError("Já existe um cadastro com esse nome. Use outro nome ou remova o cadastro existente.")

    medico = MedicoCredenciado(nome=nome, tipo=tipo)
    db.session.add(medico)
    db.session.commit()
    return {"id": medico.id, "nome": medico.nome, "tipo": medico.tipo}


def excluir_medico_credenciado(id, ids_documentos):
    db.create_all()
    garantir_coluna_tipo_medico()

    medico = MedicoCredenciado.query.get_or_404(id)
    resultado = excluir_documentacao_medico_em_lote(ids_documentos)
    db.session.delete(medico)
    db.session.commit()
    return {"ok": True, "excluidos": resultado["excluidos"]}


def criar_documentacao_medico(dados):
    db.create_all()

    registro = DocumentacaoMedicoCredenciado()
    aplicar_dados_documentacao(registro, dados)

    if not registro.nome_medico:
        raise ValueError("Informe o médico do documento.")
    if not registro.documento:
        raise ValueError("Informe o nome do documento.")

    aplicar_status_automatico(registro)
    db.session.add(registro)
    db.session.commit()

    return registro_json(registro)


def salvar_arquivo_documentacao(id, nome, mime, dados):
    garantir_colunas_arquivo_documentacao()
    registro = DocumentacaoMedicoCredenciado.query.get_or_404(id)
    registro.arquivo_nome = limpar_texto(nome)[:255]
    registro.arquivo_mime = limpar_texto(mime)[:120] or "application/octet-stream"
    registro.arquivo_dados = dados
    registro.atualizado_em = datetime.now()
    db.session.commit()
    return registro_json(registro)


def obter_arquivo_documentacao(id):
    garantir_colunas_arquivo_documentacao()
    return DocumentacaoMedicoCredenciado.query.get_or_404(id)


def atualizar_documentacao_medico(id, dados):
    db.create_all()

    registro = DocumentacaoMedicoCredenciado.query.get_or_404(id)

    status_manual = limpar_texto((dados or {}).get("status")).upper()
    if status_manual in STATUS_PRE_DEFINIDOS:
        registro.status = status_manual
        registro.status_manual = True
        registro.atualizado_em = datetime.now()
        db.session.commit()
        return registro_json(registro)

    aplicar_dados_documentacao(registro, dados)

    aplicar_status_automatico(registro)
    registro.atualizado_em = datetime.now()
    db.session.commit()

    return registro_json(registro)


def aplicar_dados_documentacao(registro, dados):
    dados = dados or {}

    for campo in CAMPOS_TEXTO:
        if campo in dados:
            setattr(registro, campo, limpar_texto(dados.get(campo)))

    for campo in CAMPOS_DATA:
        if campo in dados:
            valor = limpar_texto(dados.get(campo))
            data_convertida = ler_data_vencimento(valor) if valor else None
            if valor and not data_convertida:
                raise ValueError(f"Data inválida para {campo}.")
            setattr(registro, campo, data_convertida)

    if (
        "data_vencimento" in dados
        and registro.data_vencimento
        and "data_maxima_notificacao" not in dados
    ):
        registro.data_maxima_notificacao = registro.data_vencimento + timedelta(days=60)

    if "sem_validade" in dados or "semValidade" in dados:
        valor = dados.get("sem_validade", dados.get("semValidade"))
        registro.sem_validade = valor is True or limpar_texto(valor).lower() in {"1", "true", "sim", "on"}
        if registro.sem_validade:
            registro.data_vencimento = None

    if registro.data_vencimento is None:
        registro.sem_validade = True
    elif "data_vencimento" in dados:
        registro.sem_validade = False


def excluir_documentacao_medico(id):
    db.create_all()

    registro = DocumentacaoMedicoCredenciado.query.get_or_404(id)
    db.session.delete(registro)
    db.session.commit()

    return {"ok": True}


def excluir_documentacao_medico_em_lote(ids):
    db.create_all()

    ids_validos = []
    for valor in ids or []:
        try:
            ids_validos.append(int(valor))
        except (TypeError, ValueError):
            continue

    if not ids_validos:
        return {"ok": True, "excluidos": 0}

    registros = DocumentacaoMedicoCredenciado.query.filter(
        DocumentacaoMedicoCredenciado.id.in_(ids_validos)
    ).all()

    for registro in registros:
        db.session.delete(registro)

    db.session.commit()
    return {"ok": True, "excluidos": len(registros)}
