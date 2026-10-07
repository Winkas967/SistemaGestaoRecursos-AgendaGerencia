from models.checklist_config_model import ChecklistConfigModel


# Contém as regras de configuração das perguntas do checklist por categoria e
# ano de referência. Duas decisões de produto guiam este serviço:
#
# 1) Se uma categoria+ano ainda não tem nenhuma configuração publicada, a
#    criação de checklist para essa categoria/ano fica bloqueada
#    (ver ChecklistService.create — isso é aplicado lá, lendo
#    checklist_modelo_anos.publicado).
# 2) Editar a estrutura de um modelo que já tem checklist(s) em uso nunca
#    altera esses checklists existentes — gera automaticamente uma nova
#    versão do modelo e aponta o vínculo categoria+ano para ela. Editar um
#    modelo que ainda não foi usado por nenhum checklist é feito em cima da
#    mesma linha ( sem criar versões descartaveis).
class ChecklistConfigService:

    # Valida e normaliza o ano de referência recebido
    @staticmethod
    def validate_year(value):
        try:
            year = int(value)
        except (TypeError, ValueError):
            raise ValueError("Informe um ano de referência válido.")
        if year < 2000 or year > 2100:
            raise ValueError("Informe um ano de referência válido.")
        return year

    # Valida e normaliza o identificador da categoria recebido
    @staticmethod
    def validate_category_id(value):
        try:
            category_id = int(value)
        except (TypeError, ValueError):
            raise ValueError("Informe uma categoria válida.")
        return category_id

    # Busca a categoria pelo id, entre as categorias ativas
    @staticmethod
    def get_category(category_id):
        category_id = ChecklistConfigService.validate_category_id(category_id)
        for category in ChecklistConfigModel.get_categorias():
            if category["id"] == category_id:
                return category
        raise ValueError("Categoria não encontrada.")

    # Lista as categorias disponíveis para configuração
    @staticmethod
    def list_categories():
        return ChecklistConfigModel.get_categorias()

    # Organiza as linhas de checklist_secoes/checklist_perguntas (join) em uma
    # árvore de seções com suas perguntas — uma seção sem perguntas ainda
    # aparece (vazia), pois o LEFT JOIN de ChecklistConfigModel.get_estrutura
    # garante isso
    @staticmethod
    def _organize_structure(rows):
        sections = {}
        order = []
        for row in rows:
            section_id = row["secao_id"]
            if section_id not in sections:
                sections[section_id] = {
                    "id": section_id,
                    "nome": row["secao_nome"],
                    "perguntas": [],
                }
                order.append(section_id)
            if row["pergunta_id"] is not None:
                sections[section_id]["perguntas"].append({
                    "id": row["pergunta_id"],
                    "numero": row["numero"],
                    "pergunta": row["pergunta"],
                    "permiteObservacao": bool(row["permite_observacao"]),
                })
        return [sections[section_id] for section_id in order]

    # Busca a configuração atual (publicada ou rascunho) de uma categoria+ano
    @staticmethod
    def get_config(category_id, reference_year):
        category = ChecklistConfigService.get_category(category_id)
        year = ChecklistConfigService.validate_year(reference_year)
        link = ChecklistConfigModel.get_vinculo(category["id"], year)

        if not link:
            suggested_year = ChecklistConfigModel.get_ano_publicado_mais_proximo(
                category["id"], year
            )
            return {
                "categoriaId": category["id"],
                "categoriaNome": category["nome"],
                "ano": year,
                "configurado": False,
                "publicado": False,
                "emUso": False,
                "anoSugeridoParaCopia": suggested_year,
                "secoes": [],
            }

        structure = ChecklistConfigModel.get_estrutura(link["modelo_id"])
        in_use = ChecklistConfigModel.tem_checklists_em_uso(link["modelo_id"])

        return {
            "categoriaId": category["id"],
            "categoriaNome": category["nome"],
            "ano": year,
            "configurado": True,
            "publicado": bool(link["publicado"]),
            "modeloId": link["modelo_id"],
            "versao": link["versao"],
            "emUso": in_use,
            "secoes": ChecklistConfigService._organize_structure(structure),
        }

    # Valida a estrutura de seções/perguntas enviada pelo front
    @staticmethod
    def validate_structure(sections_payload):
        if not isinstance(sections_payload, list) or not sections_payload:
            raise ValueError("Inclua ao menos uma seção no checklist.")

        validated_sections = []
        for section in sections_payload:
            if not isinstance(section, dict):
                raise ValueError("Uma das seções possui formato inválido.")

            name = str(section.get("nome") or "").strip()
            if not name:
                raise ValueError("Toda seção precisa de um nome.")

            questions_payload = section.get("perguntas")
            if not isinstance(questions_payload, list) or not questions_payload:
                raise ValueError(f'A seção "{name}" precisa de ao menos uma pergunta.')

            validated_questions = []
            for question in questions_payload:
                if not isinstance(question, dict):
                    raise ValueError("Uma das perguntas possui formato inválido.")

                text = str(question.get("pergunta") or "").strip()
                if not text:
                    raise ValueError(f'Uma pergunta da seção "{name}" está em branco.')

                validated_questions.append({
                    "pergunta": text,
                    "permite_observacao": bool(question.get("permiteObservacao")),
                })

            validated_sections.append({"nome": name, "perguntas": validated_questions})

        return validated_sections

    # Cria ou edita a estrutura de uma categoria+ano:
    # - sem vínculo ainda -> cria modelo novo (sempre como rascunho/não publicado)
    # - vínculo existe, modelo nunca usado -> edita a estrutura no próprio modelo
    # - vínculo existe, modelo já usado em algum checklist -> gera nova versão
    #   automaticamente e aponta o vínculo pra ela, preservando se estava
    #   publicado ou em rascunho
    @staticmethod
    def save_structure(category_id, reference_year, sections_payload):
        category = ChecklistConfigService.get_category(category_id)
        year = ChecklistConfigService.validate_year(reference_year)
        sections = ChecklistConfigService.validate_structure(sections_payload)

        link = ChecklistConfigModel.get_vinculo(category["id"], year)

        if not link:
            version = ChecklistConfigModel.proxima_versao(category["slug"])
            model_id = ChecklistConfigModel.criar_modelo(
                nome=f"{category['nome']} {year}",
                slug=category["slug"],
                versao=version,
                categoria_id=category["id"],
            )
            ChecklistConfigModel.substituir_estrutura(model_id, sections)
            ChecklistConfigModel.definir_vinculo(
                category["id"], year, model_id, publicado=False
            )
        else:
            in_use = ChecklistConfigModel.tem_checklists_em_uso(link["modelo_id"])
            if in_use:
                version = ChecklistConfigModel.proxima_versao(link["slug"])
                model_id = ChecklistConfigModel.criar_modelo(
                    nome=f"{category['nome']} {year}",
                    slug=link["slug"],
                    versao=version,
                    categoria_id=category["id"],
                )
                ChecklistConfigModel.substituir_estrutura(model_id, sections)
                ChecklistConfigModel.definir_vinculo(
                    category["id"], year, model_id, publicado=bool(link["publicado"])
                )
            else:
                ChecklistConfigModel.substituir_estrutura(link["modelo_id"], sections)

        return ChecklistConfigService.get_config(category["id"], year)

    # Publica a configuração em rascunho — a partir disso, novos checklists
    # dessa categoria/ano passam a usar essas perguntas. Idempotente: publicar
    # uma configuração já publicada não é um erro.
    @staticmethod
    def publish(category_id, reference_year):
        category = ChecklistConfigService.get_category(category_id)
        year = ChecklistConfigService.validate_year(reference_year)
        link = ChecklistConfigModel.get_vinculo(category["id"], year)

        if not link:
            raise ValueError(
                "Configure as perguntas do checklist antes de publicar."
            )

        if not link["publicado"]:
            ChecklistConfigModel.publicar_vinculo(category["id"], year)

        return ChecklistConfigService.get_config(category["id"], year)
