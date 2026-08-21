from models.reports_model import ReportModel
from datetime import date
#prepara os dados exibidos nos relatorios
class ReportService:
    
    #prepara os filtros recebidos da pag
    @staticmethod
    def prepare_filters(filters=None):
        filters = filters or {}

        start_date = (
            str(filters.get("dataInicio") or "").strip()
            or None
        )

        end_date = (
            str(filters.get("dataFim") or "").strip()
            or None
        )

        sector = (
            str(filters.get("setor") or "").strip()
            or None
        )

        try:
            parsed_start = (
                date.fromisoformat(start_date)
                if start_date
                else None
            )

            parsed_end = (
                date.fromisoformat(end_date)
                if end_date
                else None
            )
        except ValueError:
            raise ValueError(
                "Uma das datas informadas é inválida."
            )

        if (
            parsed_start
            and parsed_end
            and parsed_start > parsed_end
        ):
            raise ValueError(
                "A data inicial não pode ser posterior à data final."
            )
        
        return {
            "start_date": start_date,
            "end_date": end_date,
            "sector": sector,
        }
    
    #transforma o resultado do banco em formato dos graficos
    @staticmethod
    def format_chart_data(records):
        return {
            "labels": [
                str(record["label"])
                for record in records
            ],
            "valores": [
                int(record["valor"])
                for record in records
            ],
        }
        
    #prepara o grafico de reservas por recurso
    @staticmethod
    def get_reservations_by_resource():
        records = (
            ReportModel.get_reservations_by_resource()
        )
        
        return ReportService.format_chart_data(
            records
        )
        
    #prepara o grafico de reservas por setor
    @staticmethod
    def get_reservations_by_sector():
        records = (
            ReportModel.get_reservations_by_sector()
        )
        
        return ReportService.format_chart_data(
            records
        )
        
    #prepara o grafico de reservas por status
    @staticmethod
    def get_reservations_by_status():
        records = (
            ReportModel.get_reservations_by_status()
        )
        
        status_labels = {
            "reservado": "Reservado",
            "em_uso": "Em uso",
            "devolvido": "Devolvido",
            "cancelado": "Cancelado"
        }
        
        for record in records:
            status = str(record["label"] or "").lower()
            
            record["label"] = status_labels.get(
                status,
                status.replace("_"," ").title(),
            )
            
        return ReportService.format_chart_data(
            records
        )
        
    #prepara o grafico de reservas por responsavel
    @staticmethod
    def get_reservations_by_responsable():
        records = (
            ReportModel.get_reservations_by_responsible()
        )
        
        return ReportService.format_chart_data(
            records
        )
        
    #prepara o grafico de reservas por horario
    @staticmethod
    def get_reservations_by_hour():
        records = (
            ReportModel.get_reservation_by_hour()
        )
        
        return ReportService.format_chart_data(
            records
        )
        
    #prepara o grafico de reservas por periodo
    @staticmethod
    def get_reservations_by_period():
        records = (
            ReportModel.get_reservations_by_period()
        )
        
        return ReportService.format_chart_data(
            records
        )
        
        
    #prepara os numeros gerais dos relatorios
    @staticmethod
    def get_summary(filters=None):
        prepared_filters = (
            ReportService.prepare_filters(filters)
        )
        
        record = ReportModel.get_summary(
            **prepared_filters
        ) or {}
        
        total = int(record.get("total") or 0)
        reservados = int(
            record.get("reservados") or 0
        )
        em_uso = int(
            record.get("em_uso") or 0
        )
        devolvidos = int(
            record.get("devolvidos") or 0
        )
        viagens = int(record.get("viagens") or 0
        )
        atrasados = int(
            record.get("atrasados") or 0
        )
        dias_com_uso = int(
            record.get("dias_com_uso") or 0
        )
        
        #considera como pendentes os reservados e os que estao em uso
        pendentes = reservados + em_uso
        
        #calcula a porcentagem de reservas devolvidas
        taxa_devolucao = (
            round((devolvidos / total) * 100, 2)
            if total > 0 
            else 0
        )
        
        #calcula a media de reservas por dia com uso
        media_diaria = (
            round(total / dias_com_uso, 2)
            if dias_com_uso > 0
            else 0
        )
        
        resources = (
            ReportModel.get_reservations_by_resource(
                **prepared_filters
            )
        )
        
        sectors = (
            ReportModel.get_reservations_by_sector(
                **prepared_filters
            )
        )
        
        resource_top = (
            resources[0]["label"]
            if resources
            else "-"
        )
        
        sector_top = (
            sectors[0]["label"]
            if sectors
            else "-"
        )
        
        return {
            "total": total,
            "pendentes": pendentes,
            "atrasados": atrasados,
            "taxaDevolucao": taxa_devolucao,
            "recursoTop": resource_top,
            "setorTop": sector_top,
            "mediaDiaria": media_diaria,
            "diasComUso": dias_com_uso,
            "emUso": em_uso,
            "reservados": reservados,
            "viagens": viagens,
            "devolvidos": devolvidos,
        }
        
    #trasnforma registros do banco em uma lista para o ranking
    @staticmethod
    def format_ranking(records, limit=5):
        return [
            (
                str(record["label"]),
                str(record["valor"])
            )
            for record in records[:limit]
        ]
        
    #prepara os rankings exibidos nos relatorios
    @staticmethod
    def get_rankings(filters=None):
        prepared_filters = (
            ReportService.prepare_filters(filters)
        )
        
        resources = (
            ReportModel.get_reservations_by_resource(
                **prepared_filters
            )
        )
        
        sectors = (
            ReportModel.get_reservations_by_sector(
                **prepared_filters
            )
        )
        
        responsible = (
            ReportModel.get_reservations_by_responsible(
                **prepared_filters
            )
        )
        
        return {
            "recursos": ReportService.format_ranking(
                resources
            ),
            "setores": ReportService.format_ranking(
                sectors
            ),
            "responsaveis": ReportService.format_ranking(
                responsible
            )
        }
        
    #prepara todos os graficos usando os mesmos filtros
    @staticmethod
    def get_all_charts(filters=None):
        prepared_filters = (
            ReportService.prepare_filters(filters)
        )
        
        resource_records = (
            ReportModel.get_reservations_by_resource(
                **prepared_filters
            )
        )
        
        sector_records = (
            ReportModel.get_reservations_by_sector(
                **prepared_filters
            )
        )
        
        status_records = (
            ReportModel.get_reservations_by_status(
                **prepared_filters
            )
        )
        
        responsible_records = (
            ReportModel.get_reservations_by_responsible(
                **prepared_filters
            )
        )
        
        hour_records = (
            ReportModel.get_reservation_by_hour(
                **prepared_filters
            )
        )
        
        period_records = (
            ReportModel.get_reservations_by_period(
                **prepared_filters
            )
        )
        
        status_labels = {
            "reservado": "Reservado",
            "em_uso": "Em uso",
            "devolvido": "Devolvido",
            "cancelado": "Cancelado"
        }
        
        #traduz os nomes dos status para exibicao
        for record in status_records:
            status = str(
                record["label"] or ""
            ).lower()
            
            record["label"] = status_labels.get(
                status,
                status.replace("_"," ").title()
            )
            
        return {
        "recurso": (
            ReportService.format_chart_data(
                resource_records
            )
        ),
        "setor": (
            ReportService.format_chart_data(
                sector_records
            )
        ),
        "status": (
            ReportService.format_chart_data(
                status_records
            )
        ),
        "responsavel": (
            ReportService.format_chart_data(
                responsible_records
            )
        ),
        "hora": (
            ReportService.format_chart_data(
                hour_records
            )
        ),
        "periodo": (
            ReportService.format_chart_data(
                period_records
            )
        ),
    }
        
        
    #prepara as reservas detalhadas para a exportacao
    @staticmethod
    def get_reservation_details(filters=None):
        prepared_filters = (
            ReportService.prepare_filters(filters)
        )
        
        #busca as reservas do banco
        records = (
            ReportModel.get_reservation_details(
                **prepared_filters
            )
        )
        
        #define os nomes apresentados no excel
        status_labels = {
            "reservado": "Reservado",
            "em_uso": "Em uso",
            "devolvido": "Devolvido",
            "cancelado": "Cancelado"
        }
        
        #prepara os valores de cada reserva
        for record in records:
            status = str(
                record.get("status") or ""
            ).lower()
            
            record["status"] = status_labels.get(
                status,
                status.replace("_"," ").title(),
            )
            
            #substitui valores vazios
            for field in [
                "data_volta",
                "hora_fim",
                "motivo",
                "observacao"
            ]:
                if record.get(field) is None:
                    record[field] = ""
                    
        return records
