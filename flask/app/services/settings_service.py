from models.settings_model import SettingsModel

#contem as regras das configuracoes gerais do sistema
class SettingsService:
    
    EMAIL_NOTIFICATIONS_KEY = (
        "envio_email_documentacao_ativo"
    )
    
    #converte o valor salvo no banco para verdadeiro ou falso
    @staticmethod
    def to_boolean(value):
        return str(value or "").strip().lower() in {
            "1",
            "true",
            "sim",
            "on"
        }
        
    #informa se os avisos de documentacao estao ativos
    @staticmethod
    def email_notifications_enabled():
        value = SettingsModel.get_value(
            SettingsService.EMAIL_NOTIFICATIONS_KEY
        )
        
        return SettingsService.to_boolean(value)
    
    #pausa ou ativa todos os avisos de documentacao
    @staticmethod
    def update_email_notifications(enabled):
        new_value = (
            "true"
            if SettingsService.to_boolean(enabled)
            else "false"
        )
        
        updated = SettingsModel.update_value(
            SettingsService.EMAIL_NOTIFICATIONS_KEY,
            new_value
        )
        
        if not updated:
            raise ValueError("A configuração de envio de e-mails não foi encontrada.")
        
        return {
            "ativo": new_value == "true"
        }