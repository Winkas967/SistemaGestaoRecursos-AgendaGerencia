from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from models.checklist_feedbacks_model import ChecklistFeedbackModel
from models.checklists_model import ChecklistModel
from services.evaluations_service import EvaluationService


# Contém as regras de carregamento dos checklists
class ChecklistService:
    VALID_ANSWERS = {
        "conforme", "parcialmente_conforme", "nao_conforme", "nao_se_aplica"
    }

    # Organiza as perguntas dentro de suas seções
    @staticmethod
    def organize_structure(structure, answers):
        answers_by_question = {answer["pergunta_id"]: answer for answer in answers}
        sections = {}
        for item in structure:
            section_id = item["secao_id"]
            if section_id not in sections:
                sections[section_id] = {
                    "id": section_id,
                    "nome": item["secao_nome"],
                    "ordem": item["secao_ordem"],
                    "perguntas": [],
                }
            answer = answers_by_question.get(item["pergunta_id"])
            sections[section_id]["perguntas"].append({
                "id": item["pergunta_id"],
                "numero": item["numero"],
                "pergunta": item["pergunta"],
                "permiteObservacao": bool(item["permite_observacao"]),
                "ordem": item["pergunta_ordem"],
                "resposta": answer["resposta"] if answer else None,
                "observacao": answer["observacao"] if answer else None,
            })
        return list(sections.values())

    # Converte um checklist para o formato usado pelo front
    @staticmethod
    def to_dict(evaluation, checklist):
        structure = ChecklistModel.get_structure(checklist["modelo_id"])
        answers = ChecklistModel.get_answers(checklist["id"])
        feedback = ChecklistFeedbackModel.get_by_checklist(checklist["id"])
        classification = None
        if checklist["classificacao_estrelas"] is not None:
            classification = ChecklistFeedbackModel.get_classification(
                checklist["classificacao_estrelas"]
            )
        return {
            "avaliacaoId": evaluation["id"],
            "checklistId": checklist["id"],
            "numero": checklist["numero"],
            "anoReferencia": evaluation["anoReferencia"],
            "cadastro": {
                "id": evaluation["prestadorId"],
                "nome": evaluation["prestadorNome"],
                "categoriaId": evaluation["categoriaId"],
                "categoriaNome": evaluation["categoriaNome"],
                "categoriaSlug": evaluation["categoriaSlug"],
            },
            "modelo": {
                "id": checklist["modelo_id"],
                "nome": checklist["modelo_nome"],
                "slug": checklist["modelo_slug"],
                "versao": checklist["modelo_versao"],
            },
            "status": checklist["status"],
            "dataVisita": checklist["data_visita"],
            "dataEntregaRelatorio": checklist["data_entrega_relatorio"],
            "observacoesGerais": checklist["observacoes_gerais"],
            "resultadoPercentual": checklist["resultado_percentual"],
            "classificacaoEstrelas": checklist["classificacao_estrelas"],
            "retornoMeses": (
                classification["retorno_meses"] if classification else None
            ),
            "permiteConcluirFeedback": (
                bool(classification["permite_conclusao"])
                if classification else None
            ),
            "criadoEm": checklist["criado_em"],
            "concluidoEm": checklist["concluido_em"],
            "feedback": {
                "id": feedback["id"],
                "conteudo": feedback["conteudo"],
                "classificacaoEstrelas": feedback["classificacao_estrelas"],
                "retornoMeses": feedback["retorno_meses"],
                "status": feedback["status"],
                "concluidoEm": feedback["concluido_em"],
            } if feedback else None,
            "secoes": ChecklistService.organize_structure(structure, answers),
        }

    # Lista todos os checklists de uma avaliação
    @staticmethod
    def get_all_by_evaluation(evaluation_id):
        evaluation = EvaluationService.get_by_id(evaluation_id)
        records = ChecklistModel.get_all_by_evaluation(evaluation["id"])
        return {
            "avaliacaoId": evaluation["id"],
            "cadastro": {
                "id": evaluation["prestadorId"],
                "nome": evaluation["prestadorNome"],
                "categoriaId": evaluation["categoriaId"],
                "categoriaNome": evaluation["categoriaNome"],
                "categoriaSlug": evaluation["categoriaSlug"],
            },
            "checklists": [ChecklistService.to_dict(evaluation, item) for item in records],
        }

    # Busca um checklist específico da avaliação
    @staticmethod
    def get_by_id(evaluation_id, checklist_id):
        evaluation = EvaluationService.get_by_id(evaluation_id)
        checklist = ChecklistModel.get_by_id(evaluation["id"], checklist_id)
        if not checklist:
            raise ValueError("O checklist não foi encontrado nesta avaliação.")
        return ChecklistService.to_dict(evaluation, checklist)

    # Cria um novo checklist usando o modelo atual da categoria
    @staticmethod
    def create(evaluation_id, user_id=None):
        evaluation = EvaluationService.get_by_id(evaluation_id)
        if evaluation["status"] != "em_andamento":
            raise ValueError("Esta avaliação não está em andamento.")
        if evaluation["etapaAtual"] == "termo_adesao":
            raise ValueError("Conclua o termo de adesão antes de criar um checklist.")
        model = ChecklistModel.get_model_by_category(evaluation["categoriaId"])
        if not model:
            raise ValueError("Não existe um checklist configurado para esta categoria.")
        checklist_id = ChecklistModel.create_evaluation_checklist(
            evaluation_id=evaluation["id"],
            model_id=model["id"],
            model_version=model["versao"],
            user_id=user_id,
        )
        return ChecklistService.get_by_id(evaluation["id"], checklist_id)

    # Valida uma data recebida pelo front
    @staticmethod
    def validate_date(value, field_name):
        value = str(value or "").strip()
        if not value:
            return None
        try:
            return date.fromisoformat(value)
        except ValueError:
            raise ValueError(f"{field_name} possui uma data inválida.")

    # Valida as respostas enviadas pelo front
    @staticmethod
    def validate_answers(answers, valid_question_ids):
        if answers is None:
            return []
        if not isinstance(answers, list):
            raise ValueError("As respostas do checklist são inválidas.")
        validated = []
        received_question_ids = set()
        for answer in answers:
            if not isinstance(answer, dict):
                raise ValueError("Uma das respostas possui formato inválido.")
            try:
                question_id = int(answer.get("perguntaId"))
            except (TypeError, ValueError):
                raise ValueError("Uma das perguntas informadas é inválida.")
            if question_id not in valid_question_ids:
                raise ValueError("Uma pergunta não pertence a este checklist.")
            if question_id in received_question_ids:
                raise ValueError("Uma pergunta foi enviada mais de uma vez.")
            response = str(answer.get("resposta") or "").strip().lower()
            if response not in ChecklistService.VALID_ANSWERS:
                raise ValueError("Selecione uma resposta válida para cada pergunta.")
            observation = str(answer.get("observacao") or "").strip()
            validated.append({
                "pergunta_id": question_id,
                "resposta": response,
                "observacao": observation or None,
            })
            received_question_ids.add(question_id)
        return validated

    # Atualiza um checklist e suas respostas
    @staticmethod
    def save(evaluation_id, checklist_id, data, user_id=None):
        if not isinstance(data, dict):
            raise ValueError("Os dados do checklist são inválidos.")
        evaluation = EvaluationService.get_by_id(evaluation_id)
        if evaluation["status"] != "em_andamento":
            raise ValueError("Esta avaliação não está em andamento.")
        checklist = ChecklistModel.get_by_id(evaluation["id"], checklist_id)
        if not checklist:
            raise ValueError("O checklist não foi encontrado nesta avaliação.")
        if checklist["status"] == "concluido":
            raise ValueError("Um checklist concluído não pode ser alterado.")

        structure = ChecklistModel.get_structure(checklist["modelo_id"])
        valid_question_ids = {item["pergunta_id"] for item in structure}
        answers = ChecklistService.validate_answers(data.get("respostas"), valid_question_ids)
        checklist_data = {
            "nome_fantasia": str(data.get("nomeFantasia") or "").strip() or None,
            "cnpj": str(data.get("cnpj") or "").strip() or None,
            "endereco": str(data.get("endereco") or "").strip() or None,
            "numero_endereco": str(data.get("numeroEndereco") or "").strip() or None,
            "bairro": str(data.get("bairro") or "").strip() or None,
            "municipio": str(data.get("municipio") or "").strip() or None,
            "responsavel": str(data.get("responsavel") or "").strip() or None,
            "telefone": str(data.get("telefone") or "").strip() or None,
            "data_visita": ChecklistService.validate_date(data.get("dataVisita"), "Data da visita"),
            "data_entrega_relatorio": ChecklistService.validate_date(data.get("dataEntregaRelatorio"), "Data da entrega do relatório"),
            "observacoes_gerais": str(data.get("observacoesGerais") or "").strip() or None,
            "acordo": str(data.get("acordo") or "").strip() or None,
            "auditor_nome": str(data.get("auditorNome") or "").strip() or None,
            "auditado_nome": str(data.get("auditadoNome") or "").strip() or None,
            "auditado_cargo": str(data.get("auditadoCargo") or "").strip() or None,
            "testemunha_1_nome": str(data.get("testemunha1Nome") or "").strip() or None,
            "testemunha_2_nome": str(data.get("testemunha2Nome") or "").strip() or None,
        }
        ChecklistModel.update_evaluation_checklist(checklist["id"], checklist_data, user_id)
        ChecklistModel.save_answers(checklist["id"], answers)
        return ChecklistService.get_by_id(evaluation["id"], checklist["id"])

    # Calcula o percentual e a classificação do checklist
    @staticmethod
    def calculate_result(summary):
        total_questions = int(summary["total_perguntas"] or 0)
        total_answers = int(summary["total_respondidas"] or 0)
        total_conforming = int(summary["total_conformes"] or 0)
        total_partial = int(summary["total_parciais"] or 0)
        total_not_applicable = int(summary["total_nao_aplicaveis"] or 0)
        if total_answers < total_questions:
            raise ValueError("Todas as perguntas devem ser respondidas antes de concluir o checklist.")
        applicable_questions = total_questions - total_not_applicable
        if applicable_questions <= 0:
            raise ValueError("Todas as perguntas foram marcadas como não aplicáveis.")
        points = Decimal(total_conforming) + Decimal(total_partial) * Decimal("0.5")
        percentage = (points / Decimal(applicable_questions) * Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        if percentage >= Decimal("95"):
            stars = 5
        elif percentage >= Decimal("85"):
            stars = 4
        elif percentage >= Decimal("70"):
            stars = 3
        elif percentage >= Decimal("60"):
            stars = 2
        elif percentage >= Decimal("50"):
            stars = 1
        else:
            stars = 0
        return {"percentual": percentage, "estrelas": stars, "totalAplicaveis": applicable_questions}

    # Conclui somente o checklist informado
    @staticmethod
    def complete(evaluation_id, checklist_id, user_id):
        evaluation = EvaluationService.get_by_id(evaluation_id)
        if evaluation["status"] != "em_andamento":
            raise ValueError("Esta avaliação não está em andamento.")
        checklist = ChecklistModel.get_by_id(evaluation["id"], checklist_id)
        if not checklist:
            raise ValueError("O checklist não foi encontrado nesta avaliação.")
        if checklist["status"] == "concluido":
            raise ValueError("Este checklist já foi concluído.")
        result = ChecklistService.calculate_result(ChecklistModel.get_result_summary(checklist["id"]))
        ChecklistModel.complete(checklist["id"], result["percentual"], result["estrelas"], user_id)
        return ChecklistService.get_by_id(evaluation["id"], checklist["id"])
