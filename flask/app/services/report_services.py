from models.reports_model import ReportModel

#prepara os dados exibidos nos relatorios
class ReportService:
    
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