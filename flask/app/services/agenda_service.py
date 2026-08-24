from datetime import date, time

from models.agenda_model import AgendaAppointment, AgendaModel


#contem as regras de negocio da agenda
class AgendaService:
    ALLOWED_STATUSES = {
        "agendado",
        "andamento",
        "concluido",
        "cancelado"
    }
    
    #converte e valida um data
    @staticmethod
    def parse_date(value):
        if not value:
            raise ValueError("A data do compromisso é obrigatória.")
        
        try:
            return date.fromisoformat(str(value))
        except (TypeError, ValueError):
            raise ValueError("A data do compromisso é inválida.")
        
    #converte e valida um horario
    @staticmethod
    def parse_time(value, field_name):
        if not value:
            raise ValueError(f"O campo {field_name} é obrigatório.")
        
        try:
            return time.fromisoformat(str(value))
        except (TypeError, ValueError):
            raise ValueError(f"O campo {field_name} possui horário inválido.")
        
        
        
    #valida todos os dados do compromisso
    @staticmethod
    def validate_data(data, ignored_id=None):
        if not isinstance(data, dict):
            raise ValueError("Os dados do compromisso são inválidos.")
        
        title = str(data.get("titulo") or "").strip()
        responsible = (
            str(data.get("responsavel") or "").strip()
            or None
        )
        location = (
            str(data.get("local") or "").strip()
            or None
        )
        description = (
            str(data.get("descricao")or "").strip()
            or None
        )
        status = str(
            data.get("status") or "agendado"
        ).strip().lower()
        
        if not title:
            raise ValueError("O título do compromisso é obrigatório.")
        
        if len(title) > 160:
            raise ValueError(
                "O título deve ter no máximo 160 caracteres."
            )
            
        if responsible and len(responsible) > 120:
            raise ValueError(
                "O responsável deve ter no máximo 120 caracteres."
            )
            
        if location and len(location) > 140:
            raise ValueError(
                "O local deve ter no máximo 140 caracteres."
            )
            
        if status not in AgendaService.ALLOWED_STATUSES:
            raise ValueError("O status informado é inválido.")
        
        appointment_date = AgendaService.parse_date(
            data.get("data")
        )
        
        start_time = AgendaService.parse_time(
            data.get("horaInicio"),
            "horário inicial"
        )
        
        end_time = AgendaService.parse_time(
            data.get("horaFim"),
            "horário final"
        )
        
        if end_time <= start_time:
            raise ValueError(
                "O horário final deve ser posterior ao horário inicial."
            )
            
        if status != "cancelado":
            has_conflict = AgendaModel.has_conflict(
                appointment_date=appointment_date,
                start_time=start_time,
                end_time=end_time,
                ignored_id=ignored_id
            )
            
            if has_conflict:
                raise ValueError("Já existe um compromisso nesse horário.")
            
            
        return {
            "titulo": title,
            "data": appointment_date,
            "hora_inicio": start_time,
            "hora_fim": end_time,
            "responsavel": responsible,
            "local": location,
            "descricao": description,
            "status": status,
        }
        
        
    #lista todos os compromissos
    @staticmethod
    def get_all():
        return [
            appointment.to_dict()
            for appointment in AgendaModel.get_all()
        ]
        
    #busca um compromisso pelo id
    @staticmethod
    def get_by_id(appointment_id):
        try:
            appointment_id = int(appointment_id)
        except (TypeError, ValueError):
            raise ValueError("O compromisso informado é inválido.")
        
        appointment = AgendaModel.get_by_id(appointment_id)
        
        if not appointment:
            raise ValueError("O compromisso não foi encontrado.")
        
        return appointment
    
    #cadastra um compromisso
    @staticmethod
    def create(data, user_id=None):
        validated_data = AgendaService.validate_data(data)
        
        appointment = AgendaAppointment(
            **validated_data,
            criado_por_id=user_id
        )
        
        
        appointment_id = AgendaModel.create(appointment)
        
        created_appointment = AgendaModel.get_by_id(appointment_id)
        
        return created_appointment.to_dict()
    
    #atualzia um compromisso
    @staticmethod
    def update(appointment_id, data):
        existing_appointment = AgendaService.get_by_id(appointment_id)
        
        validated_data = AgendaService.validate_data(data, ignored_id=existing_appointment.id)
        
        appointment = AgendaAppointment(
            id=existing_appointment.id,
            criado_por_id=existing_appointment.criado_por_id,
            **validated_data
        )
        
        AgendaModel.update(appointment)
        
        updated_appointment = AgendaModel.get_by_id(existing_appointment.id)
        
        return updated_appointment.to_dict()
    
    #atualiza somente o status
    @staticmethod
    def update_status(appointment_id, data):
        appointment = AgendaService.get_by_id(appointment_id)
        
        if not isinstance(data, dict):
            raise ValueError("Os dados enviados são inválidos.")
        
        status = str(
            data.get("status") or ""
        ).strip().lower()
        
        if status not in AgendaService.ALLOWED_STATUSES:
            raise ValueError("O status informado é inválido.")
        
        AgendaModel.update_status(
            appointment.id,
            status
        )
        
        updated_appointment = AgendaModel.get_by_id(appointment.id)
        
        return updated_appointment.to_dict()
    
    #exclui um compromisso
    @staticmethod
    def delete(appointment_id):
        appointment = AgendaService.get_by_id(appointment_id)
        
        deleted = AgendaModel.delete(appointment.id)
        
        if not deleted:
            raise ValueError("Não foi possível excluir o compromisso.")
        
        return True