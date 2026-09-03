from models.checklists_model import ChecklistModel
from services.evaluations_service import EvaluationService
from datetime import date


#contem as regras de carregamento dos checklists
class ChecklistService:
    
    #converte valores do banco para boolean
    @staticmethod
    def to_boolean(value):
        return bool(value)
    
    #organiza as perguntas dentro de suas secoes
    @staticmethod
    def organize_structure(structure, answers):
        answers_by_question = {
            answer["pergunta_id"]: answer
            for answer in answers
        }
        
        sections = {}
        
        for item in structure:
            section_id = item["secao_id"]
            
            if section_id not in sections:
                sections[section_id] = {
                    "id": section_id,
                    "nome": item["secao_nome"],
                    "ordem": item["secao_ordem"],
                    "perguntas": []
                }
                
            answer = answers_by_question.get(item["pergunta_id"])
            
            sections[section_id]["perguntas"].append({
                "id": item["pergunta_id"],
                "numero": item["numero"],
                "pergunta": item["pergunta"],
                "permiteObservacao": (
                    ChecklistService.to_boolean(item["permite_observacao"])
                ),
                "ordem": item["pergunta_ordem"],
                "resposta": (
                    answer["resposta"]
                    if answer
                    else None
                ),
                "observacao": (
                    answer["observacao"]
                    if answer
                    else None
                ),
            })
            
        return list(sections.values())
    
    
    #carrega o checklist correspondente a avaliacao
    @staticmethod
    def get_by_evaluation(evaluation_id):
        evaluation = EvaluationService.get_by_id(evaluation_id)
        
        checklist = ChecklistModel.get_by_evaluation(evaluation["id"])
        
        if checklist:
            model = {
                "id": checklist["modelo_id"],
                "nome": checklist["modelo_nome"],
                "slug": checklist["modelo_slug"],
                "versao": checklist["modelo_versao"]
            }
            
            answers = ChecklistModel.get_answers(checklist["id"])
            
        else:
            model_record = (
                ChecklistModel.get_model_by_category(evaluation["categoriaId"])
            )
            
            if not model_record:
                raise ValueError(
                    "Não existe um checklist configurado "
                    "para a categoria deste cadastro."
                )
                
            model = {
                "id": model_record["id"],
                "nome": model_record["nome"],
                "slug": model_record["slug"],
                "versao": model_record["versao"],
            }
            
            answers = []
            
        structure = ChecklistModel.get_structure(model["id"])
        
        sections = ChecklistService.organize_structure(structure,answers)
        
        return {
            "avaliacaoId": evaluation["id"],
            "anoReferencia": evaluation["anoReferencia"],
            "checklistId": (
                checklist["id"]
                if checklist
                else None
            ),
            
            "cadastro": {
                "id": evaluation["prestadorId"],
                "nome": evaluation["prestadorNome"],
                "categoriaId": evaluation["categoriaId"],
                "categoriaNome": evaluation["categoriaNome"],
                "categoriaSlug": evaluation["categoriaSlug"],
            },
            "modelo": model,
            "status": (
                checklist["status"]
                if checklist
                else "nao_iniciado"
            ),
            "dataVisita": (
                checklist["data_visita"]
                if checklist
                else None
            ),
            "dataEntregaRelatorio": (
                checklist["data_entrega_relatorio"]
                if checklist
                else None
            ),
            "observacoesGerais": (
                checklist["observacoes_gerais"]
                if checklist
                else None
            ),
            "resultadoPercentual": (
                checklist["resultado_percentual"]
                if checklist
                else None
            ),
            "classificacaoEstrelas": (
                checklist["classificacao_estrelas"]
                if checklist
                else None
            ),
            "secoes": sections,
        }
        
    #define as respostas aceitas pelo checklist
    VALID_ANSWERS = {
        "conforme",
        "parcialmete_conforme",
        "nao_conforme",
        "nao_se_aplica"
    }
    
    #valida uma data recebida pelo front
    @staticmethod
    def validate_date(value, field_name):
        value = str(value or "").strip()
        
        if not value:
            return None
        
        try:
            return date.fromisoformat(value)
        
        except ValueError:
            raise ValueError(f"{field_name} possui uma data inválida.")
        
        
    #valida as repostas enviadas pelo front
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
                question_id = int(
                    answer.get("perguntaId")
                )

            except (TypeError, ValueError):
                raise ValueError(
                    "Uma das perguntas informadas é inválida."
                )

            if question_id not in valid_question_ids:
                raise ValueError(
                    "Uma das perguntas não pertence "
                    "ao checklist desta avaliação."
                )

            if question_id in received_question_ids:
                raise ValueError(
                    "Uma pergunta foi enviada mais de uma vez."
                )

            response = str(
                answer.get("resposta") or ""
            ).strip().lower()

            if response not in ChecklistService.VALID_ANSWERS:
                raise ValueError(
                    "Selecione uma resposta válida "
                    "para todas as perguntas enviadas."
                )

            observation = str(
                answer.get("observacao") or ""
            ).strip()

            validated.append({
                "pergunta_id": question_id,
                "resposta": response,
                "observacao": observation or None,
            })

            received_question_ids.add(question_id)

        return validated