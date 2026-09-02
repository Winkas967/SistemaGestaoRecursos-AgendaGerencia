from datetime import date

from models.adhesion_terms_model import AdhesionTerm, AdhesionTermModel
from models.evaluations_model import EvaluationModel
from services.file_storage_service import FileStorageService
from models.files_model import FileModel


#contem as regras do termo de adesao
class AdhesionTermService:
    
    VALID_POSITIONS = {
        "aceitou",
        "recusou",
        "sem_posicionamento"
    }
    
    ALLOWED_EXTENSIONS = {
        ".pdf",
        ".doc",
        ".docx",
        ".jpg",
        ".jpeg",
        ".png"
    }
    
    #busca e valida uma avaliacao
    @staticmethod
    def get_evaluation(evaluation_id):
        try:
            evaluation_id = int(evaluation_id)
            
        except (TypeError, ValueError):
            raise ValueError("A avaliação informada é inválida.")
        
        evaluation = EvaluationModel.get_by_id(evaluation_id)
        
        if not evaluation:
            raise ValueError("A avaliação não foi encontrada.")
        
        return evaluation
    
    
    #valida o posicionamento do termo
    @staticmethod
    def validate_position(position):
        position = str(position or "").strip().lower()
        
        if position not in (
            AdhesionTermService.VALID_POSITIONS
        ):
            raise ValueError("Selecione um posicionamento válido.")
        
        return position
    
    
    #converte o termo para o formato do frontend
    @staticmethod
    def to_dict(term):
        if not term:
            return None
        
        file_data = None
        
        if term.get("arquivo_id"):
            file_data = {
                "id": term["arquivo_id"],
                "nome": term["arquivo_nome"],
                "mimeType": term["arquivo_mime_type"],
                "tamanhoBytes": term["arquivo_tamanho"],
                "url": (
                    f"/api/avaliacoes/"
                    f"{term['avaliacao_id']}/termo/arquivo"
                ),
            }
            
        return {
            "id": term["id"],
            "avaliacaoId": term["avaliacao_id"],
            "posicionamento": term["posicionamento"],
            "arquivo": file_data,
            "registradoPorId": term["registrado_por_id"],
            "registradoEm": term["registrado_em"],
            "criadoEm": term["criado_em"],
            "atualizadoEm": term["atualizado_em"],
        }
        
        
    #busca o termo de uma avaliacao
    @staticmethod
    def get_by_evaluation(evaluation_id):
        evaluation = (
            AdhesionTermService.get_evaluation(evaluation_id)
        )
        
        term = AdhesionTermModel.get_by_evaluation(evaluation["id"])
        
        return AdhesionTermService.to_dict(term)
    
    
    #salva ou atualiza o termo de adesao
    @staticmethod
    def save(evaluation_id, data, uploaded_file, user_id=None):
        evaluation = (
            AdhesionTermService.get_evaluation(
                evaluation_id
            )
        )
        
        if evaluation["status"] != "em_andamento":
            raise ValueError("Esta avaliação não está em andamento.")
        
        
        position = (
            AdhesionTermService.validate_position(
                data.get("posicionamento")
            )
        )
        
        existing_term = (
            AdhesionTermModel.get_by_evaluation(
                evaluation["id"]
            )
        )
        
        has_new_file = bool(
            uploaded_file and uploaded_file.filename
        )
        
        if (
            not has_new_file and not existing_term
        ):
            raise ValueError("Anexe o documento do termo de adesão.")
        
        new_file = None
        old_file_id = (
            existing_term.get("arquivo_id")
            if existing_term
            else None
        )
        
        if has_new_file:
            new_file = FileStorageService.save(
                uploaded_file=uploaded_file,
                category="avaliacoes/termos",
                year=date.today().year,
                user_id=user_id,
                allowed_extensions=(AdhesionTermService.ALLOWED_EXTENSIONS),
            )
            
        file_id = (
            new_file.id
            if new_file
            else old_file_id
        )
        
        try:
            if existing_term:
                AdhesionTermModel.update(
                    term_id=existing_term["id"],
                    position=position,
                    file_id=file_id,
                    user_id=user_id
                )
                
                term_id = existing_term["id"]
                
            else:
                term = AdhesionTerm(
                    avaliacao_id=evaluation["id"],
                    posicionamento=position,
                    arquivo_id=file_id,
                    registrado_por_id=user_id
                )
                
                term_id = AdhesionTermModel.create(term)
                
            EvaluationModel.update_stage(
                evaluation["id"],
                "checklist"
            )
            
        except Exception:
            if new_file:
                FileStorageService.delete(new_file.id)
                
            raise
        
        if(new_file and old_file_id and old_file_id != new_file.id):
            FileStorageService.delete(old_file_id)
            
        saved_term = (
            AdhesionTermModel.get_by_evaluation(evaluation["id"])
        )
        
        result = AdhesionTermService.to_dict(saved_term)
        
        result["avaliacaoEtapaAtual"] = "checklist"
        
        return result
    
    
    #retorna o arquivo anexado ao termo
    @staticmethod
    def get_file(evaluation_id):
        evaluation = (
            AdhesionTermService.get_evaluation(evaluation_id)
        )
        
        term = AdhesionTermModel.get_by_evaluation(evaluation["id"])
        
        if not term:
            raise ValueError("O termo de adesão não foi encontrado.")
        
        if not term.get("arquivo_id"):
            raise ValueError("O termo de adesão não possui documento.")
        
        file_record = FileModel.get_by_id(term["arquivo_id"])
        
        if not file_record:
            raise ValueError("O arquivo do termo não foi encontrado.")
        
        absolute_path = (
            FileStorageService.resolve_path(file_record)
        )
        
        return file_record, absolute_path