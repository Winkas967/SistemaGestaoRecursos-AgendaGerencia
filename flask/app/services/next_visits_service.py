from datetime import date, datetime

from models.checklist_feedbacks_model import ChecklistFeedbackModel
from utils.pagination import build_pagination_meta, resolve_pagination


# Contem as regras da lista de Proximas Visitas: a data prevista e sempre
# calculada a partir da data da visita digitada pelo usuario no checklist
# (data_visita + retorno_meses da classificacao) — nao existe campo proprio
# no banco nem edicao manual, para evitar que a data fique desatualizada.
class NextVisitsService:

    # Calcula os dias restantes ate a data prevista (negativo quando ja passou)
    @staticmethod
    def _dias_restantes(proxima_visita_em):
        if isinstance(proxima_visita_em, datetime):
            referencia = proxima_visita_em.date()
        elif isinstance(proxima_visita_em, date):
            referencia = proxima_visita_em
        else:
            return None

        return (referencia - date.today()).days

    # Converte um registro de prestador+feedback para o formato usado pelo front
    @staticmethod
    def _to_dict(record):
        return {
            "prestadorId": record["prestador_id"],
            "prestadorNome": record["prestador_nome"],
            "categoria": record["categoria_nome"],
            "dataVisitaEm": record["data_visita"],
            "retornoMeses": record["retorno_meses"],
            "proximaVisitaEm": record["proxima_visita_em"],
            "diasRestantes": NextVisitsService._dias_restantes(record["proxima_visita_em"]),
        }

    # Mantem somente o feedback concluido mais recente de cada prestador — a
    # consulta ja vem ordenada por prestador e por data_visita decrescente,
    # entao o primeiro registro encontrado para cada prestador e o mais recente
    @staticmethod
    def _mais_recente_por_prestador(records):
        registros_por_prestador = {}
        for record in records:
            prestador_id = record["prestador_id"]
            if prestador_id not in registros_por_prestador:
                registros_por_prestador[prestador_id] = record
        return list(registros_por_prestador.values())

    # Lista as proximas visitas previstas, ordenadas pela data mais proxima,
    # com busca por nome do prestador e paginacao no servidor
    @staticmethod
    def get_all(pagina=None, por_pagina=None, busca=None):
        pagina, por_pagina = resolve_pagination(pagina, por_pagina)

        registros = ChecklistFeedbackModel.get_completed_with_next_visit()
        registros = NextVisitsService._mais_recente_por_prestador(registros)

        busca_normalizada = str(busca or "").strip().lower()
        if busca_normalizada:
            registros = [
                record for record in registros
                if busca_normalizada in str(record["prestador_nome"] or "").lower()
            ]

        registros.sort(key=lambda record: record["proxima_visita_em"])

        total = len(registros)
        inicio = (pagina - 1) * por_pagina
        registros_pagina = registros[inicio:inicio + por_pagina]

        return {
            "registros": [NextVisitsService._to_dict(record) for record in registros_pagina],
            "total": total,
            **build_pagination_meta(pagina, por_pagina, total),
        }
