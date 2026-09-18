from flask import Blueprint, jsonify, request

from services.next_visits_service import NextVisitsService
from utils.auth import permission_required

# Cria o grupo de rotas das proximas visitas — calculadas a partir dos
# feedbacks concluidos dos checklists de avaliacao, por isso reutiliza a
# mesma permissao de modulo das avaliacoes
next_visits_bp = Blueprint(
    "next_visits",
    __name__,
    url_prefix="/api/agenda/proximas-visitas",
)


# Lista as proximas visitas previstas, com busca por prestador e paginacao no servidor
@next_visits_bp.route("", methods=["GET"])
@permission_required("avaliacao", "visualizar")
def get_next_visits():
    try:
        resultado = NextVisitsService.get_all(
            pagina=request.args.get("pagina"),
            por_pagina=request.args.get("porPagina"),
            busca=request.args.get("busca"),
        )

        return jsonify(resultado), 200

    except ValueError as error:
        return jsonify({"erro": str(error)}), 400
