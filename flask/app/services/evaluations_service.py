from datetime import date

from models.evaluations_model import Evaluation, EvaluationModel
from models.providers_model import ProviderModel

#contem regras dos processos de avaliacao
class EvaluationService:
    
    #converte uma avaliacao para o formato usado pelo front
    @staticmethod
    def to_dict(evaluation):
        if not evaluation:
            return None
        
        return {
            "id": evaluation["id"],
            "prestadorId": evaluation["prestador_id"],
            "anoReferencia": evaluation["ano_referencia"],
            "prestadorNome": evaluation["prestador_nome"],
            "categoriaId": evaluation["categoria_id"],
            "categoriaNome": evaluation["categoria_nome"],
            "categoriaSlug": evaluation["categoria_slug"],
            "etapaAtual": evaluation["etapa_atual"],
            "status": evaluation["status"],
            "iniciadoPorId": evaluation["iniciado_por_id"],
            "iniciadoEm": evaluation["iniciado_em"],
            "concluidoEm": evaluation["concluido_em"],
            "atualizadoEm": evaluation["atualizado_em"],
        }


    #lista todas as avaliacoes
    @staticmethod
    def get_all():
        evaluations = EvaluationModel.get_all()
        
        return [
            EvaluationService.to_dict(evaluation)
            for evaluation in evaluations
        ]
        
        
    #busca uma avaliacao pelo identificador
    @staticmethod
    def get_by_id(evaluation_id):
        try:
            evaluation_id = int(evaluation_id)
            
        except (TypeError, ValueError):
            raise ValueError("A avaliação informada é inválida.")
        
        evaluation = EvaluationModel.get_by_id(evaluation_id)
        
        if not evaluation:
            raise ValueError("A avaliação não foi encontrada.")
        
        return EvaluationService.to_dict(evaluation)
    
    
    #lista os cadastros disponiveis para uma nova avaliacao
    @staticmethod
    def get_available_providers():
        providers = ProviderModel.get_all()
        evaluations = EvaluationModel.get_all()
        
        providers_in_progress = {
            evaluation["prestador_id"]
            for evaluation in evaluations
            #sem_posicionamento e sem_visita fecham o fluxo mas continuam editaveis, então o
            #cadastro segue "ocupado" até o posicionamento/a visita ser definida
            if evaluation["status"] in ("em_andamento", "sem_posicionamento", "sem_visita")
        }
        
        available = []
        
        for provider in providers:
            if provider.situacao != "ativo":
                continue
            
            if provider.id in providers_in_progress:
                continue
            
            available.append({
                "id": provider.id,
                "nome": provider.nome,
                "categoriaNome": provider.categoria_nome,
                "categoriaSlug": provider.categoria_slug
            })
            
        return available
    
    
    #inicia uma nova avaliacao para um cadastro
    @staticmethod
    def create(provider_id, reference_year, user_id):
        try:
            provider_id = int(provider_id)
            
        except (TypeError, ValueError):
            raise ValueError("O cadastro informado é inválido.")

        current_year = date.today().year

        if reference_year in (None, ""):
            reference_year = current_year
        else:
            try:
                reference_year = int(reference_year)
            except (TypeError, ValueError):
                raise ValueError("O ano de referência informado é inválido.")

        if reference_year < 2000 or reference_year > current_year + 1:
            raise ValueError(
                "O ano de referência deve estar entre "
                f"2000 e {current_year + 1}."
            )
        
        provider = ProviderModel.get_by_id(provider_id)
        
        if not provider:
            raise ValueError("O cadastro não foi encontrado.")
        
        if provider.situacao != "ativo":
            raise ValueError("Não é possivel avaliar um cadastro descredenciado.")
        
        active_evaluation = (
            EvaluationModel.get_active_by_provider(provider_id)
        )
        
        if active_evaluation:
            raise ValueError("Este cadastro já possui uma avaliação em andamento.")
        
        evaluation = Evaluation(
            prestador_id=provider.id,
            ano_referencia=reference_year,
            iniciado_por_id=user_id,
            etapa_atual="termo_adesao",
            status="em_andamento"
        )
        
        evaluation_id = EvaluationModel.create(evaluation)

        return EvaluationService.get_by_id(evaluation_id)


    #finaliza a avaliacao quando todos os checklists concluidos ja tiverem feedback
    @staticmethod
    def complete(evaluation_id):
        # importado aqui para evitar import circular com checklists_service
        from services.checklists_service import ChecklistService

        evaluation = EvaluationService.get_by_id(evaluation_id)

        if evaluation["status"] != "em_andamento":
            raise ValueError("Esta avaliação não está em andamento.")

        checklists = ChecklistService.get_all_by_evaluation(evaluation["id"])["checklists"]
        completed_checklists = [item for item in checklists if item["status"] == "concluido"]

        if not completed_checklists:
            raise ValueError("Conclua ao menos um checklist antes de finalizar a avaliação.")

        pending = [
            item for item in completed_checklists
            if not (item["feedback"] and item["feedback"]["status"] == "concluido")
            and item["permiteConcluirFeedback"] is not False
        ]

        if pending:
            raise ValueError(
                "Existem checklists concluídos com feedback pendente. "
                "Conclua o feedback de todos antes de finalizar a avaliação."
            )

        updated = EvaluationModel.complete(evaluation["id"])

        if not updated:
            raise ValueError("Não foi possível finalizar a avaliação.")

        return EvaluationService.get_by_id(evaluation["id"])


    #normaliza/valida o ano de referencia informado nos filtros do dashboard
    @staticmethod
    def _resolve_dashboard_year(year):
        current_year = date.today().year

        if year in (None, ""):
            return current_year

        try:
            return int(year)
        except (TypeError, ValueError):
            raise ValueError("O ano informado é inválido.")


    #monta o resumo do dashboard de avaliacoes, agregado por categoria, para um ano de referencia
    @staticmethod
    def get_dashboard(year=None):
        year = EvaluationService._resolve_dashboard_year(year)

        rows = EvaluationModel.get_dashboard_summary(year)

        categorias = []
        totais = {
            "totalPrestadores": 0,
            "adesao": 0,
            "naoAdesao": 0,
            "naoPosicionaram": 0,
            "semVisita": 0,
            "visitaSemDocumento": 0,
            "estrelas5": 0,
            "estrelas4": 0,
            "estrelas3": 0,
            "estrelas2": 0,
            "estrelas1": 0,
            "estrelas0": 0,
        }

        for row in rows:
            item = {
                "categoriaId": row["categoria_id"],
                "categoriaNome": row["categoria_nome"],
                "categoriaSlug": row["categoria_slug"],
                "totalPrestadores": int(row["total_prestadores"] or 0),
                "adesao": int(row["adesao"] or 0),
                "naoAdesao": int(row["nao_adesao"] or 0),
                "naoPosicionaram": int(row["nao_posicionaram"] or 0),
                "semVisita": int(row["sem_visita"] or 0),
                "visitaSemDocumento": int(row["visita_sem_documento"] or 0),
                "estrelas5": int(row["estrelas_5"] or 0),
                "estrelas4": int(row["estrelas_4"] or 0),
                "estrelas3": int(row["estrelas_3"] or 0),
                "estrelas2": int(row["estrelas_2"] or 0),
                "estrelas1": int(row["estrelas_1"] or 0),
                "estrelas0": int(row["estrelas_0"] or 0),
            }
            categorias.append(item)
            for key in totais:
                totais[key] += item[key]

        media_adesao = (
            round(totais["adesao"] / totais["totalPrestadores"] * 100, 2)
            if totais["totalPrestadores"] else 0
        )

        return {
            "anoReferencia": year,
            "categorias": categorias,
            "totais": totais,
            "mediaAdesaoPercentual": media_adesao,
        }


    #traduz o status de adesao para o rotulo exibido ao usuario
    @staticmethod
    def _dashboard_status_adesao_label(status_adesao):
        labels = {
            "aceitou": "Aceitou",
            "recusou": "Recusou",
            "sem_posicionamento": "Não se posicionou",
        }
        return labels.get(status_adesao, status_adesao or "—")


    #traduz o status da avaliacao para o rotulo exibido ao usuario
    @staticmethod
    def _dashboard_avaliacao_status_label(status):
        if not status:
            return "Sem avaliação iniciada"

        labels = {
            "em_andamento": "Em andamento",
            "concluida": "Concluída",
            "recusada": "Recusada",
            "sem_posicionamento": "Sem posicionamento (aguardando termo)",
            "sem_visita": "Encerrado sem visita",
        }
        return labels.get(status, status)


    #monta o detalhamento por prestador do dashboard (linha a linha), usado
    #pela tabela detalhada em tela e pela exportacao em excel
    @staticmethod
    def get_dashboard_details(year=None):
        year = EvaluationService._resolve_dashboard_year(year)

        rows = EvaluationModel.get_dashboard_details(year)

        registros = [
            {
                "prestadorNome": row["prestador_nome"],
                "categoriaNome": row["categoria_nome"],
                "statusAdesao": EvaluationService._dashboard_status_adesao_label(row["status_adesao"]),
                "statusAvaliacao": EvaluationService._dashboard_avaliacao_status_label(row["avaliacao_status"]),
                "teveVisita": bool(row["teve_visita"]) if row["teve_visita"] is not None else None,
                "estrelas": int(row["classificacao_estrelas"]) if row["classificacao_estrelas"] is not None else None,
                "resultadoPercentual": float(row["resultado_percentual"]) if row["resultado_percentual"] is not None else None,
                "iniciadoEm": row["iniciado_em"],
                "concluidoEm": row["concluido_em"],
                "checklistConcluidoEm": row["checklist_concluido_em"],
            }
            for row in rows
        ]

        return {
            "anoReferencia": year,
            "registros": registros,
            "total": len(registros),
        }
