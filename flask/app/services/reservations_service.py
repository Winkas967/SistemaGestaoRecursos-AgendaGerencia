from datetime import date, datetime, time, timedelta

from models.reservations_model import Reservation, ReservationModel
from models.resources_model import ResourceModel
from models.sectors_model import SectorModel

#contem as regras de negocio das reservas
class ReservationService:
    #converte um valor em verdadeiro ou falso
    @staticmethod
    def to_boolean(value):
        return value in (
            True,
            1,
            "1",
            "true",
            "True",
            "on",
            "sim",
        )
        
    #converte uma data recebida em texto
    @staticmethod
    def parse_date(value, field_name, required=False):
        value = str(value or "").strip()
        
        if not value:
            if required:
                raise ValueError(
                    f"O campo {field_name} é obrigatório."
                )    
                
            return None
        
        try:
            return date.fromisoformat(value)
        
        except ValueError:
            
            raise ValueError(
            f"O campo {field_name} possui uma data inválida."
        )
        
    #converte um horario recebido em texto
    @staticmethod
    def parse_time(value, field_name, required=False):
        value = str(value or "").strip()
        
        if not value:
            if required:
                raise ValueError(
                    f"O campo {field_name} é obrigatório."
                )
                
            return None
        
        try:
            return time.fromisoformat(value)
        except ValueError:
            raise ValueError(
                f"O campo {field_name} possui um horário inválido."
            )
            
    #valida os dados da reserva
    @staticmethod
    def validate_data(data, user_sector_id, is_admin=False):
        resource_id = data.get("recurso_id")
        sector_id = data.get("setor_id")
        reason = str(data.get("motivo") or "").strip()
        observation = (
            str(data.get("observacao") or "").strip()
            or None
        )
        is_trip = ReservationService.to_boolean(
            data.get("viagem")
        )
        
        try:
            resource_id = int(resource_id)
        except (TypeError, ValueError):
            raise ValueError("O recurso informado é inválido.")
        
        resource = ResourceModel.get_by_id(resource_id)
        
        if not resource or not resource.ativo:
            raise ValueError("O recurso informado não existe.")
        
        if resource.status != "disponivel":
            raise ValueError(
                "Este recurso não está disponível para reserva."
            )
            
        if not is_admin:
            sector_id = user_sector_id
            
        try:
            sector_id = int(sector_id)
        except (TypeError, ValueError):
            raise ValueError("O setor informado é inválido.")
        
        sector = SectorModel.get_by_id(sector_id)
        
        if not sector or not sector.ativo:
            raise ValueError(
                "O setor informado não existe ou está inativo."
            )
            
        if not reason:
            raise ValueError("O motivo da reserva é obrigatório.")
        
        if len(reason) > 150:
            raise ValueError("O motivo deve ter no máximo 150 caracteres.")
        
        start_date = ReservationService.parse_date(
            data.get("data_reserva"),
            "data da reserva",
            required = True,
        )
        
        end_date = ReservationService.parse_date(
            data.get("data_volta"),
            "data de volta",
        )
        
        start_time = ReservationService.parse_time(
            data.get("hora_inicio"),
            "hora de inicio",
            required=True
        )
        
        end_time = ReservationService.parse_time(
            data.get("hora_fim"),
            "hora de término",
        )
        
        if end_date is None:
            end_date = start_date
            
        #define uma hora de duração quando o fim não foi preenchido
        if end_time is None and end_date == start_date:
            calculated_end = (
                datetime.combine(start_date, start_time)
                + timedelta(hours=1)
            )
            
            end_date = calculated_end.date()
            end_time = calculated_end.time()
            
        #usa o final do dia quando existe data de volta
        elif end_time is None:
            end_time = time(23, 59, 59)
            
        start_datetime = datetime.combine(
            start_date,
            start_time,
        )
        
        end_datetime = datetime.combine(
            end_date,
            end_time
        )
        
        if end_datetime <= start_datetime:
            raise ValueError(
                "O término deve ser posterior ao início."
            )
            
        has_conflict = ReservationModel.has_conflict(
            resource_id=resource_id,
            start_date=start_date,
            end_date=end_date,
            start_time=start_time,
            end_time=end_time,
        )
        
        if has_conflict:
            raise ValueError(
                "Este recurso já possui uma reserva nesse periodo."
            )
            
        return {
            "recurso_id": resource_id,
            "setor_id": sector_id,
            "motivo": reason,
            "observacao": observation,
            "viagem": is_trip,
            "data_reserva": start_date,
            "data_volta": end_date,
            "hora_inicio": start_time,
            "hora_fim": end_time,
        }
        
    #cadastra uma nova reserva
    @staticmethod
    def create(
        data,
        user_id,
        username,
        user_sector_id,
        is_admin=False,
    ):
        validated_data = ReservationService.validate_data(
            data,
            user_sector_id,
            is_admin,
        )
        
        reservation = Reservation(
            recurso_id=validated_data["recurso_id"],
            usuario_id=user_id,
            setor_id=validated_data["setor_id"],
            responsavel=username,
            motivo=validated_data["motivo"],
            data_reserva=validated_data["data_reserva"],
            data_volta=validated_data["data_volta"],
            hora_inicio=validated_data["hora_inicio"],
            hora_fim=validated_data["hora_fim"],
            observacao=validated_data["observacao"],
            viagem=validated_data["viagem"],
            status="reservado",
        )
        
        reservation_id = ReservationModel.create(
            reservation
        )
        
        created_reservation = ReservationModel.get_by_id(
            reservation_id
        )
        
        if not created_reservation:
            raise RuntimeError(
                "A reserva for criada, mas não pôde ser consultada."
            )
            
        return created_reservation.to_dict()
    
    #lista as reservas de um recurso
    @staticmethod
    def get_by_resource(resource_id):
        try:
            resource_id = int(resource_id)
        except (TypeError, ValueError):
            raise ValueError("O recurso informado é inválido.")
        
        resource = ResourceModel.get_by_id(resource_id)
        
        if not resource or not resource.ativo:
            raise ValueError("O recurso informado não existe.")
        
        reservations = ReservationModel.get_by_resource(
            resource_id
        )
        
        return [
            reservation.to_dict()
            for reservation in reservations
        ]
        
    #organiza as reservas para exibicao na pagina
    @staticmethod
    def get_schedule_by_resource(resource_id):
        reservations = ReservationService.get_by_resource(
            resource_id
        )
        
        schedule = {}
        
        for reservation in reservations:
            reservation_date = reservation["data_reserva"]
            
            if reservation_date not in schedule:
                formatted_date = date.fromisoformat(
                    reservation_date
                ).strftime("%d/%m/%Y")
                
                schedule[reservation_date] = {
                    "data_formatada": formatted_date,
                    "horarios": [],
                }
                
            end_date = reservation["data_volta"]
            
            if end_date:
                end_date = date.fromisoformat(
                    end_date
                ).strftime("%d/%m/%Y")
                
            schedule[reservation_date]["horarios"].append({
                "inicio": reservation["hora_inicio"][:5],
                "fim": reservation["hora_fim"][:5],
                "data_fim": end_date,
                "responsavel": reservation["responsavel"],
                "status": reservation["status"]
            })
            
        return [
            schedule[reservation_date]
            for reservation_date in sorted(schedule)
        ]
            
            
    #prepara as reservas exibidas na pagina inicial
    @staticmethod
    def get_for_home(user_id, is_admin=False):
        filter_user_id = None if is_admin else user_id
        
        reservations = ReservationModel.get_for_home(
            filter_user_id
        )
        
        status_labels = {
            "reservado": "Reservado",
            "em_uso": "Em uso",
            "devolvido": "Devolvido",
            "cancelado": "Cancelado"
        }
        
        items = []
        
        for reservation in reservations:
            data = reservation.to_dict()
            status = str(data["status"] or "").lower()
            
            data["data_reserva_formatada"] = (
                reservation.data_reserva.strftime("%d/%m/%Y")
                if reservation.data_reserva
                else "-"
            )
            
            data["data_volta_formatada"] = (
                reservation.data_volta.strftime("%d/%m/%Y")
                if reservation.data_volta
                else "-"
            )
            
            data["hora_inicio_formatada"] = (
                str(reservation.hora_inicio)[:5]
                if reservation.hora_inicio
                else "-"
            )

            data["hora_fim_formatada"] = (
                str(reservation.hora_fim)[:5]
                if reservation.hora_fim
                else None
            )

            data["status_calculado"] = status
            data["status_label"] = status_labels.get(
                status,
                status.replace("_", " ").title(),
            )

            data["devolucao_iso"] = (
                data["data_volta"]
                or data["data_reserva"]
                or ""
            )

            items.append(data)

        return {
            "items": items,
            "total": len(items),
            "page": 1,
            "has_prev": False,
            "has_next": False,
            "prev_num": None,
            "next_num": None,
        }
        
    #finaliza uma reserva e marca o equipamento como devolvido
    @staticmethod
    def return_reservation(reservation_id, user_id, is_admin=False):
        
        try:
            reservation_id = int(reservation_id)
        except (TypeError, ValueError):
            raise ValueError("O agendamento informado é inválido.")
        
        reservation = ReservationModel.get_by_id(reservation_id)
        
        if not reservation:
            raise ValueError("O agendamento não foi encontrado.")
        
        #impede que um employee feche a reserva de outro usuario
        if (
            not is_admin
            and reservation.usuario_id != user_id
        ):
            raise ValueError(
                "Você não pode fechar o agendamento de outro usuário."
            )
            
        if reservation.status == "devolvido":
            raise ValueError(
                "Este agendamento já foi finalizado."
            )
            
        if reservation.status == "cancelado":
            raise ValueError(
                "Um agendamento cancelado não pode ser finalizado."
            )
            
        updated = ReservationModel.mark_as_returned(reservation_id)
        
        if not updated:
            raise ValueError("Não foi possível finalizar o agendamento.")
        
        returned_reservation = ReservationModel.get_by_id(reservation_id)
        
        return returned_reservation.to_dict()