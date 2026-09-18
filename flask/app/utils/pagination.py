#funcoes compartilhadas para paginacao no servidor (avaliacoes, atas,
#documentacao e tabela detalhada do dashboard)

PADRAO_POR_PAGINA = 20
MAXIMO_POR_PAGINA = 100


#normaliza os parametros de pagina/quantidade recebidos via querystring
def resolve_pagination(pagina, por_pagina, padrao_por_pagina=PADRAO_POR_PAGINA, maximo_por_pagina=MAXIMO_POR_PAGINA):
    try:
        pagina = int(pagina) if pagina not in (None, "") else 1
    except (TypeError, ValueError):
        raise ValueError("A página informada é inválida.")

    try:
        por_pagina = int(por_pagina) if por_pagina not in (None, "") else padrao_por_pagina
    except (TypeError, ValueError):
        raise ValueError("A quantidade de registros por página informada é inválida.")

    if pagina < 1:
        pagina = 1

    if por_pagina < 1:
        por_pagina = padrao_por_pagina

    por_pagina = min(por_pagina, maximo_por_pagina)

    return pagina, por_pagina


#monta o bloco de metadados de paginacao devolvido junto da lista de registros
def build_pagination_meta(pagina, por_pagina, total):
    total_paginas = max(1, -(-total // por_pagina)) if por_pagina else 1

    return {
        "pagina": pagina,
        "porPagina": por_pagina,
        "totalPaginas": total_paginas,
    }
