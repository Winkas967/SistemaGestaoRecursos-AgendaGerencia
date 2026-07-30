from datetime import date, datetime

from sqlalchemy.exc import IntegrityError

from conexao import db
from model import AtaReuniao


TIPOS_ATAS = {
    "conselho-administrativo": "Ata do Conselho Administrativo",
    "conselho-fiscal": "Ata do Conselho Fiscal",
    "conselho-etica": "Ata do Conselho de Ética",
    "relacionamento-cooperado": "Ata do Relacionamento ao Cooperado",
    "cgi": "Ata do CGI",
    "comite-governanca": "Ata do Comitê de Governança",
    "age-ago-unimed-sete-meia": "Ata das AGE/AGO/Unimed Sete e Meia",
}


def limpar_texto(valor):
    return str(valor or "").strip()


def ler_data(valor):
    try:
        return date.fromisoformat(limpar_texto(valor))
    except ValueError:
        return None


def ata_json(ata):
    return {
        "id": ata.id,
        "numero": ata.numero_ata,
        "data": ata.data_reuniao.isoformat(),
        "dataTexto": ata.data_reuniao.strftime("%d/%m/%Y"),
        "ano": ata.data_reuniao.year,
        "tipo": ata.tipo_ata,
        "tipoTexto": TIPOS_ATAS.get(ata.tipo_ata, ata.tipo_ata),
        "pauta": ata.pauta,
        "participantes": ata.participantes,
        "arquivo": {
            "nome": ata.arquivo_nome,
            "url": f"/api/agenda/atas/{ata.id}/arquivo",
        },
        "criadoEm": ata.criado_em.isoformat() if ata.criado_em else None,
    }


def listar_atas():
    db.create_all()
    atas = AtaReuniao.query.order_by(
        AtaReuniao.data_reuniao.desc(),
        AtaReuniao.id.desc(),
    ).all()
    registros = [ata_json(ata) for ata in atas]
    return {
        "registros": registros,
        "total": len(registros),
        "anos": sorted({item["ano"] for item in registros}, reverse=True),
        "ultimaAtualizacao": registros[0]["dataTexto"] if registros else None,
        "tipos": [{"valor": valor, "texto": texto} for valor, texto in TIPOS_ATAS.items()],
    }


def criar_ata(dados, arquivo_nome, arquivo_mime, arquivo_dados):
    db.create_all()
    numero = limpar_texto(dados.get("numero"))
    data_reuniao = ler_data(dados.get("data"))
    tipo = limpar_texto(dados.get("tipo"))
    pauta = limpar_texto(dados.get("pauta"))
    participantes = limpar_texto(dados.get("participantes"))

    if not numero:
        raise ValueError("Informe o número da ata.")
    if not data_reuniao:
        raise ValueError("Informe uma data válida para a reunião.")
    if tipo not in TIPOS_ATAS:
        raise ValueError("Selecione um tipo de ata válido.")
    if not pauta:
        raise ValueError("Informe a pauta da reunião.")
    if not participantes:
        raise ValueError("Informe os participantes da reunião.")
    if AtaReuniao.query.filter(db.func.lower(AtaReuniao.numero_ata) == numero.lower()).first():
        raise ValueError("Já existe uma ata cadastrada com este número.")

    ata = AtaReuniao(
        numero_ata=numero[:50],
        data_reuniao=data_reuniao,
        tipo_ata=tipo,
        pauta=pauta,
        participantes=participantes,
        arquivo_nome=limpar_texto(arquivo_nome)[:255],
        arquivo_mime=limpar_texto(arquivo_mime)[:120] or "application/octet-stream",
        arquivo_dados=arquivo_dados,
        atualizado_em=datetime.now(),
    )
    db.session.add(ata)
    try:
        db.session.commit()
    except IntegrityError as erro:
        db.session.rollback()
        raise ValueError("Já existe uma ata cadastrada com este número.") from erro
    return ata_json(ata)


def obter_ata(id):
    db.create_all()
    return AtaReuniao.query.get_or_404(id)


def excluir_ata(id):
    ata = obter_ata(id)
    db.session.delete(ata)
    db.session.commit()
    return {"ok": True}
