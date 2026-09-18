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

        #update_value faz upsert: cria a configuracao se ainda nao existir
        SettingsModel.update_value(
            SettingsService.EMAIL_NOTIFICATIONS_KEY,
            new_value
        )

        return {
            "ativo": new_value == "true"
        }