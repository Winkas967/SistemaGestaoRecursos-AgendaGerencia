from datetime import date

from models.minutes_model import Minute, MinuteModel
from services.file_storage_service import FileStorageService



#contem as regras de negocio das atas
class MinutesService:
    TYPE_NAMES = {
        "conselho-administrativo": (
            "Ata do Conselho Administrativo"
        ),
        "conselho-fiscal": (
            "Ata do Conselho Fiscal"
        ),
        "conselho-etica": (
            "Ata do Conselho Ético"
        ),
        "relacionamento-cooperado": (
            "Ata do Relacionamento ao Cooperado"
        ),
        "cgi": (
            "Ata do CGI"
        ),
        "comite-governanca": (
            "Ata do Comitê de Governança"
        ),
        "age-ago-unimed-sete-meia": (
            "Ata das AGE/AGO/Unimed Sete e Meia"
        ),
    }

    #converte uma data recebida pelo formulario
    @staticmethod
    def parse_date(value):
        if not value:
            raise ValueError("A data da reunião é obrigatória.")
        
        try:
            return date.fromisoformat(str(value))
        except (TypeError, ValueError):
            raise ValueError("A data da reunião é inválida.")
        
        
    #valida os campos do formulário
    @staticmethod
    def validate_data(data):
        number = str(data.get("numero") or "").strip()
        type_slug = str(data.get("tipo") or "").strip()
        agenda = str(data.get("pauta") or "").strip()
        participants = str(data.get("participantes") or "").strip()
        
        if not number:
            raise ValueError("O número da ata é obrigatório.")
        
        if len(number) > 50:
            raise ValueError("O número da ata deve ter no máximo 50 caracteres")
        
        meeting_date = MinutesService.parse_date(data.get("data"))
        type_name = MinutesService.TYPE_NAMES.get(type_slug)
        
        if not type_name:
            raise ValueError("O tipo da ata informada é inválido.")
        
        minute_type = MinuteModel.get_type_by_name(type_name)
        
        if not minute_type:
            raise ValueError("O tipo da ata não está cadastrado ou está inativo.")
        
        if not agenda:
            raise ValueError("A pauta da reunião é obrigatória.")
        
        if not participants:
            raise ValueError("Os participantes são obrigatórios.")
        
        return {
            "numero_ata": number,
            "data_reuniao": meeting_date,
            "tipo_ata_id": minute_type["id"],
            "pauta": agenda,
            "participantes": participants
        }
        
    #descobre o codigo utilizado pelo filtro do javascript
    @staticmethod
    def get_type_slug(type_name):
        for slug, registered_name in (
            MinutesService.TYPE_NAMES.items()
        ):
            if registered_name == type_name:
                return slug
            
        return ""
    
    #converte uma ata para o formato da interface
    @staticmethod
    def to_dict(minute):
        meeting_date = minute.data_reuniao
        
        file_data = None
        
        if minute.arquivo_id:
            file_data = {
                "id": minute.arquivo_id,
                "nome": minute.nome_original,
                "url": (
                    f"/api/agenda/atas/"
                    f"{minute.id}/arquivo"
                ),
            }
            
        return {
            "id": minute.id,
            "numero": minute.numero_ata,
            "data": (
                meeting_date.isoformat()
                if meeting_date
                else None
            ),
            "dataTexto": (
                meeting_date.strftime("%d/%m/%Y")
                if meeting_date
                else ""
            ),
            "ano": (
                meeting_date.year
                if meeting_date
                else None
            ),
            "tipo": MinutesService.get_type_slug(minute.tipo_ata_nome),
            "tipoTexto": minute.tipo_ata_nome,
            "pauta": minute.pauta,
            "participantes": minute.participantes,
            "arquivo": file_data,
        }
        
    #lista todos as atas
    @staticmethod
    def get_all():
        minutes = MinuteModel.get_all()
        
        records = [
            MinutesService.to_dict(minute)
            for minute in minutes
        ]
        
        years = sorted({
            minute.data_reuniao.year
            for minute in minutes
            if minute.data_reuniao
        })
        
        update_dates = [
            minute.atualizado_em or minute.criado_em
            for minute in minutes
            if minute.atualizado_em or minute.criado_em
        ]
        
        last_update = "Nenhuma"
        
        if update_dates:
            last_update = max(update_dates).strftime(
                "%d/%m/%Y %H:%M"
            )
            
        return {
            "registros": records,
            "anos": years,
            "total": len(records),
            "ultimaAtualizacao": last_update
        }
        
    #busca uma ata e valida o id
    @staticmethod
    def get_by_id(minute_id):
        try:
            minute_id = int(minute_id)
        except (TypeError, ValueError):
            raise ValueError("A ata informada é inválida.")
        
        minute = MinuteModel.get_by_id(minute_id)
        
        if not minute:
            raise ValueError("A ata não foi encontrada.")
        
        return minute
    
    #cadastra uma ata e salva o anexo
    @staticmethod
    def create(data, uploaded_file, user_id=None):
        validated_data = MinutesService.validate_data(data)
        
        file_record = FileStorageService.save(
            uploaded_file=uploaded_file,
            category="atas",
            year=validated_data["data_reuniao"].year,
            user_id=user_id,
            allowed_extensions={
                ".pdf",
                ".doc",
                ".docx"
            },
        )
        
        try:
            minute = Minute(
                **validated_data,
                arquivo_id=file_record.id,
                criado_por_id=user_id
            )
            
            minute_id = MinuteModel.create(minute)
            
        except Exception:
            FileStorageService.delete(file_record.id)
            raise
        
        created_minute = MinuteModel.get_by_id(minute_id)
        
        return MinutesService.to_dict(created_minute)
    
    #retorna a ata e o caminho do anexo
    @staticmethod
    def get_file(minute_id):
        minute = MinutesService.get_by_id(minute_id)
        
        if not minute.arquivo_id:
            raise ValueError("Esta ata não possui arquivo.")
        
        absolute_path = (
            FileStorageService.resolve_path(minute)
        )
        
        return minute, absolute_path
    
    #exclui uma ata e seu anexo
    @staticmethod
    def delete(minute_id):
        minute = MinutesService.get_by_id(minute_id)
        
        file_id = minute.arquivo_id

        if file_id:
            FileStorageService.delete(file_id)

        deleted = MinuteModel.delete(minute.id)
        
        if not deleted:
            raise ValueError("Não foi possível excluir a ata.")
        
        return True
