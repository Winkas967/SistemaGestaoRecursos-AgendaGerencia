from models.checklist_feedbacks_model import ChecklistFeedbackModel
from models.checklists_model import ChecklistModel
from services.evaluations_service import EvaluationService


# Contém as regras dos feedbacks individuais dos checklists
class ChecklistFeedbackService:

    # Converte o feedback para o formato usado pelo front
    @staticmethod
    def to_dict(feedback):
        if not feedback:
            return None

        return {
            "id": feedback["id"],
            "checklistId": feedback["checklist_avaliacao_id"],
            "conteudo": feedback["conteudo"],
            "classificacaoEstrelas": feedback["classificacao_estrelas"],
            "retornoMeses": feedback["retorno_meses"],
            "arquivoRelatorioId": feedback["arquivo_relatorio_id"],
            "arquivoCertificadoId": feedback["arquivo_certificado_id"],
            "documentosGeradosEm": feedback["documentos_gerados_em"],
            "status": feedback["status"],
            "registradoPorId": feedback["registrado_por_id"],
            "concluidoEm": feedback["concluido_em"],
            "criadoEm": feedback["criado_em"],
            "atualizadoEm": feedback["atualizado_em"],
        }

    # Valida se o checklist pertence à avaliação
    @staticmethod
    def get_checklist(evaluation_id, checklist_id):
        EvaluationService.get_by_id(evaluation_id)
        checklist = ChecklistModel.get_by_id(evaluation_id, checklist_id)

        if not checklist:
            raise ValueError("O checklist não foi encontrado nesta avaliação.")

        return checklist

    # Busca e valida a regra calculada para o checklist
    @staticmethod
    def get_classification_rule(checklist):
        stars = checklist["classificacao_estrelas"]
        if stars is None:
            raise ValueError("O checklist ainda não possui uma classificação.")

        rule = ChecklistFeedbackModel.get_classification(stars)
        if not rule:
            raise ValueError("Não existe uma regra configurada para esta classificação.")

        return rule

    # Busca o feedback do checklist
    @staticmethod
    def get(evaluation_id, checklist_id):
        checklist = ChecklistFeedbackService.get_checklist(evaluation_id, checklist_id)
        feedback = ChecklistFeedbackService.to_dict(
            ChecklistFeedbackModel.get_by_checklist(checklist_id)
        )
        rule = None
        if checklist["classificacao_estrelas"] is not None:
            classification = ChecklistFeedbackService.get_classification_rule(checklist)
            rule = {
                "estrelas": classification["estrelas"],
                "retornoMeses": classification["retorno_meses"],
                "permiteConclusao": bool(classification["permite_conclusao"]),
            }
        return {"feedback": feedback, "classificacao": rule}

    # Salva o rascunho do feedback
    @staticmethod
    def save(evaluation_id, checklist_id, data, user_id):
        checklist = ChecklistFeedbackService.get_checklist(
            evaluation_id,
            checklist_id,
        )

        if checklist["status"] != "concluido":
            raise ValueError("Conclua o checklist antes de preencher o feedback.")

        existing = ChecklistFeedbackModel.get_by_checklist(checklist_id)
        if existing and existing["status"] == "concluido":
            raise ValueError("Este feedback já foi concluído.")

        content = str((data or {}).get("conteudo") or "").strip()
        return ChecklistFeedbackService.to_dict(
            ChecklistFeedbackModel.save(checklist_id, content or None, user_id)
        )

    # Conclui o feedback do checklist
    @staticmethod
    def complete(evaluation_id, checklist_id, data, user_id):
        checklist = ChecklistFeedbackService.get_checklist(
            evaluation_id,
            checklist_id,
        )

        if checklist["status"] != "concluido":
            raise ValueError("Conclua o checklist antes de concluir o feedback.")

        rule = ChecklistFeedbackService.get_classification_rule(checklist)
        if not rule["permite_conclusao"]:
            raise ValueError(
                "Checklists com zero estrelas não permitem concluir o feedback, "
                "gerar relatório, emitir certificado ou enviar e-mail."
            )

        existing = ChecklistFeedbackModel.get_by_checklist(checklist_id)
        if existing and existing["status"] == "concluido":
            raise ValueError("Este feedback já foi concluído.")

        content = str((data or {}).get("conteudo") or "").strip()
        if not content:
            raise ValueError("Escreva o feedback antes de concluí-lo.")

        return ChecklistFeedbackService.to_dict(
            ChecklistFeedbackModel.complete(
                checklist_id,
                content,
                rule["estrelas"],
                rule["retorno_meses"],
                user_id,
            )
        )
