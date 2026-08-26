from datetime import date
from email.utils import parseaddr

from models.disaccreditments_model import DisaccreditmentModel
from models.documents_model import DocumentModel
from models.files_model import FileModel
from models.providers_model import Provider, ProviderModel
from services.documents_service import DocumentsService
from services.file_storage_service import FileStorageService


# Contém as regras de negócio dos Prestadores
class ProvidersService:
    # Valida e normaliza um e-mail opcional
    @staticmethod
    def validate_email(value):
        email = str(value or "").strip().lower()
        if not email:
            return None
        parsed = parseaddr(email)[1]
        if parsed != email or "@" not in email or "." not in email.rsplit("@", 1)[-1]:
            raise ValueError("Informe um e-mail de notificação válido.")
        if len(email) > 255:
            raise ValueError("O e-mail deve ter no máximo 255 caracteres.")
        return email

    # Busca e valida um prestador
    @staticmethod
    def get_by_id(provider_id):
        try:
            provider_id = int(provider_id)
        except (TypeError, ValueError):
            raise ValueError("O cadastro informado é inválido.")
        provider = ProviderModel.get_by_id(provider_id)
        if not provider:
            raise ValueError("O cadastro não foi encontrado.")
        return provider

    # Cadastra um prestador
    @staticmethod
    def create(data):
        if not isinstance(data, dict):
            raise ValueError("Os dados do cadastro são inválidos.")
        name = str(data.get("nome") or "").strip()
        category_slug = str(data.get("tipo") or "").strip().lower()
        notification_email = ProvidersService.validate_email(
            data.get("email_notificacao", data.get("emailNotificacao"))
        )
        if not name:
            raise ValueError("O nome do cadastro é obrigatório.")
        if len(name) > 160:
            raise ValueError("O nome deve ter no máximo 160 caracteres.")
        if ProviderModel.name_exists(name):
            raise ValueError("Já existe um cadastro com esse nome.")
        category = ProviderModel.get_category_by_slug(category_slug)
        if not category:
            raise ValueError("A categoria informada é inválida.")
        provider = Provider(
            nome=name,
            categoria_id=category["id"],
            situacao="ativo",
            email_notificacao=notification_email,
            receber_avisos=bool(notification_email),
        )
        provider_id = ProviderModel.create(provider)
        return DocumentsService.provider_to_dict(ProviderModel.get_by_id(provider_id))

    # Altera o destinatário dos avisos de um cadastro existente
    @staticmethod
    def update_notification(provider_id, data):
        provider = ProvidersService.get_by_id(provider_id)
        email = ProvidersService.validate_email(
            data.get("email_notificacao", data.get("emailNotificacao"))
        )
        receive = DocumentsService.to_boolean(
            data.get("receber_avisos", data.get("receberAvisos", bool(email)))
        )
        if receive and not email:
            raise ValueError("Informe um e-mail para ativar os avisos.")
        ProviderModel.update_notification(provider.id, email, receive and bool(email))
        return DocumentsService.provider_to_dict(ProviderModel.get_by_id(provider.id))

    # Descredencia ou recredencia um prestador
    @staticmethod
    def update_situation(provider_id, data, uploaded_file=None, user_id=None):
        provider = ProvidersService.get_by_id(provider_id)
        disaccredited = DocumentsService.to_boolean(data.get("descredenciado"))
        if not disaccredited:
            ProviderModel.update_situation(provider.id, "ativo")
            return DocumentsService.provider_to_dict(ProviderModel.get_by_id(provider.id))

        reason = str(data.get("motivo") or "").strip()
        if not reason:
            raise ValueError("O motivo do descredenciamento é obrigatório.")

        file_record = None
        if uploaded_file:
            file_record = FileStorageService.save(
                uploaded_file=uploaded_file,
                category="descredenciamentos",
                year=date.today().year,
                user_id=user_id,
                allowed_extensions={".pdf", ".doc", ".docx", ".jpg", ".jpeg", ".png"},
            )

        record_id = None
        try:
            record_id = DisaccreditmentModel.create(
                provider.id,
                reason,
                file_record.id if file_record else None,
                user_id,
            )
            ProviderModel.update_situation(provider.id, "descredenciado")
        except Exception:
            if record_id:
                DisaccreditmentModel.delete(record_id)
            if file_record:
                FileStorageService.delete(file_record.id)
            raise

        return DocumentsService.provider_to_dict(ProviderModel.get_by_id(provider.id))

    # Retorna o anexo do último descredenciamento
    @staticmethod
    def get_disaccreditment_file(provider_id):
        provider = ProvidersService.get_by_id(provider_id)
        if not provider.arquivo_descredenciamento_id:
            raise ValueError("Este descredenciamento não possui arquivo.")
        file_record = FileModel.get_by_id(provider.arquivo_descredenciamento_id)
        return file_record, FileStorageService.resolve_path(file_record)

    # Exclui o prestador, documentos e todos os anexos
    @staticmethod
    def delete(provider_id):
        provider = ProvidersService.get_by_id(provider_id)
        documents = DocumentModel.get_by_provider(provider.id)
        disaccreditments = DisaccreditmentModel.get_by_provider(provider.id)
        file_ids = {
            document.arquivo_id for document in documents if document.arquivo_id
        }
        file_ids.update(
            record["arquivo_id"] for record in disaccreditments if record.get("arquivo_id")
        )
        for file_id in file_ids:
            FileStorageService.delete(file_id)
        if not ProviderModel.delete(provider.id):
            raise ValueError("Não foi possível excluir o cadastro.")
        return True
