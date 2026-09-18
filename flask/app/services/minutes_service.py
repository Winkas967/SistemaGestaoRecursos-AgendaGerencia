from datetime import date

from models.minutes_model import Minute, MinuteModel
from services.file_storage_service import FileStorageService
from utils.pagination import build_pagination_meta, resolve_pagination



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
        
    #resolve o id do tipo de ata a partir do slug usado pelo filtro do front
    @staticmethod
    def _resolve_type_id(type_slug):
        type_name = MinutesService.TYPE_NAMES.get((type_slug or "").strip())

        if not type_name:
            return None

        minute_type = MinuteModel.get_type_by_name(type_name)

        return minute_type["id"] if minute_type else None


    #lista as atas com busca/ano/tipo/ordenacao e paginacao no servidor; os
    #agregados (anos existentes, total e ultima atualizacao) sao globais, ou
    #seja, nao mudam conforme a pagina/filtro, pois alimentam o cabecalho da tela
    @staticmethod
    def get_all(pagina=None, por_pagina=None, busca=None, ano=None, tipo=None, ordem="recentes"):
        pagina, por_pagina = resolve_pagination(pagina, por_pagina)

        busca = (busca or "").strip() or None

        try:
            ano = int(ano) if ano not in (None, "") else None
        except (TypeError, ValueError):
            raise ValueError("O ano informado é inválido.")

        type_id = MinutesService._resolve_type_id(tipo) if tipo else None

        total = MinuteModel.count_all(year=ano, type_id=type_id, search=busca)

        offset = (pagina - 1) * por_pagina

        minutes = MinuteModel.get_all(
            year=ano,
            type_id=type_id,
            search=busca,
            order=ordem,
            limit=por_pagina,
            offset=offset,
        )

        records = [
            MinutesService.to_dict(minute)
            for minute in minutes
        ]

        global_stats = MinuteModel.get_global_stats()

        last_update = "Nenhuma"

        if global_stats["ultima_atualizacao"]:
            last_update = global_stats["ultima_atualizacao"].strftime("%d/%m/%Y %H:%M")

        return {
            "registros": records,
            "anos": global_stats["anos"],
            "total": total,
            "totalGeral": global_stats["total"],
            "ultimaAtualizacao": last_update,
            **build_pagination_meta(pagina, por_pagina, total),
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
