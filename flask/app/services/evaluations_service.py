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
            if evaluation["status"] == "em_andamento"
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

        try:
            reference_year = int(reference_year)

        except (TypeError, ValueError):
            raise ValueError("O ano de referência informado é inválido.")

        current_year = date.today().year

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
