from datetime import date, timedelta

from models.documents_model import Document, DocumentModel
from models.providers_model import ProviderModel
from services.file_storage_service import FileStorageService
from utils.pagination import build_pagination_meta, resolve_pagination


# Contém as regras de negócio da Documentação
class DocumentsService:
    ALLOWED_STATUSES = {"CONFORME", "PENDENTE", "NOTIFICADO"}

    # Converte um valor para verdadeiro ou falso
    @staticmethod
    def to_boolean(value):
        if isinstance(value, bool):
            return value
        return str(value or "").strip().lower() in {"1", "true", "sim", "on"}

    # Converte uma data opcional
    @staticmethod
    def parse_optional_date(value, field_name):
        if value in {None, ""}:
            return None
        try:
            return date.fromisoformat(str(value))
        except (TypeError, ValueError):
            raise ValueError(f"O campo {field_name} possui uma data inválida.")

    # Calcula o status automático
    @staticmethod
    def calculate_status(expiration_date, notification_date, no_expiration):
        if no_expiration or not expiration_date:
            return "CONFORME"
        today = date.today()
        if today <= expiration_date:
            return "CONFORME"
        if notification_date and today > notification_date:
            return "NOTIFICADO"
        return "PENDENTE"

    # Busca e valida um documento
    @staticmethod
    def get_by_id(document_id):
        try:
            document_id = int(document_id)
        except (TypeError, ValueError):
            raise ValueError("O documento informado é inválido.")
        document = DocumentModel.get_by_id(document_id)
        if not document:
            raise ValueError("O documento não foi encontrado.")
        return document

    # Converte um documento para o formato da interface
    @staticmethod
    def document_to_dict(document):
        expiration = document.data_vencimento.isoformat() if document.data_vencimento else ""
        notification = document.data_notificacao.isoformat() if document.data_notificacao else ""
        file_data = None
        if document.arquivo_id:
            file_data = {
                "id": document.arquivo_id,
                "nome": document.nome_original,
                "url": f"/api/agenda/documentacao/{document.id}/arquivo",
            }
        return {
            "id": document.id,
            "medico": document.prestador_nome,
            "nome": document.prestador_nome,
            "documento": document.nome,
            "status": document.status,
            "semValidade": bool(document.sem_validade),
            "naoIndicado": bool(document.nao_indicado),
            "arquivo": file_data,
            "valores": [
                document.prestador_nome,
                document.nome,
                expiration,
                notification,
                document.status,
                bool(document.sem_validade),
                bool(document.nao_indicado),
                document.observacao or "",
            ],
        }

    # Converte um prestador para o formato da interface
    @staticmethod
    def provider_to_dict(provider):
        file_data = None
        if provider.arquivo_descredenciamento_id:
            file_data = {
                "id": provider.arquivo_descredenciamento_id,
                "nome": provider.arquivo_descredenciamento_nome,
                "url": f"/api/agenda/medicos/{provider.id}/descredenciamento/arquivo",
            }
        return {
            "id": provider.id,
            "nome": provider.nome,
            "tipo": provider.categoria_slug,
            "descredenciado": provider.situacao == "descredenciado",
            "motivoDescredenciamento": provider.motivo_descredenciamento or "",
            "arquivoDescredenciamento": file_data,
            "emailNotificacao": provider.email_notificacao,
            "receberAvisos": bool(provider.receber_avisos),
        }

    # Atualiza os status automáticos conforme a data atual
    @staticmethod
    def refresh_automatic_statuses(documents):
        for document in documents:
            if document.status_manual:
                continue
            calculated_status = DocumentsService.calculate_status(
                document.data_vencimento,
                document.data_notificacao,
                document.sem_validade,
            )
            if calculated_status == document.status:
                continue
            document.status = calculated_status
            DocumentModel.update(document)
        return documents

    # Verifica se um documento atende ao status/busca informados (mesma regra
    # usada pelo filtro da tela, para decidir quais documentos/prestadores aparecem)
    @staticmethod
    def _document_matches(document, status=None, search=None):
        if status and (document.status or "").strip().upper() != status:
            return False

        if not search:
            return True

        campos = " ".join([
            document.prestador_nome or "",
            document.nome or "",
            document.observacao or "",
            document.status or "",
        ]).lower()

        return search in campos

    # Lista prestadores, documentos e indicadores, com busca/status/categoria e
    # paginacao no servidor (por prestador); o resumo e o percentual continuam
    # calculados sobre a base completa, para não variarem conforme a página/filtro
    @staticmethod
    def get_all(pagina=None, por_pagina=None, busca=None, status=None, categoria=None):
        pagina, por_pagina = resolve_pagination(pagina, por_pagina)

        busca = (busca or "").strip().lower() or None
        status = (status or "").strip().upper() or None
        categoria = (categoria or "").strip() or None
        mostrar_descredenciados = categoria == "descredenciados"

        providers = ProviderModel.get_all()
        documents = DocumentsService.refresh_automatic_statuses(
            DocumentModel.get_all()
        )
        provider_by_id = {provider.id: provider for provider in providers}

        # resumo/percentual/alerta de vencimento excluem descredenciados sempre e
        # respeitam a categoria selecionada, mas nao a busca/status/pagina — por
        # isso nao mudam so porque o usuario troca de pagina ou digita uma busca
        def no_escopo_do_resumo(document):
            provider = provider_by_id.get(document.prestador_id)
            if provider and provider.situacao == "descredenciado":
                return False
            if categoria and categoria != "todos":
                tipo_cadastro = provider.categoria_slug if provider else "credenciado"
                if tipo_cadastro != categoria:
                    return False
            return True

        active_documents = [document for document in documents if no_escopo_do_resumo(document)]
        evaluated = [document for document in active_documents if not document.nao_indicado]
        conforming = sum(document.status == "CONFORME" for document in evaluated)
        pending = sum(document.status == "PENDENTE" for document in evaluated)
        notified = sum(document.status == "NOTIFICADO" for document in evaluated)
        total_evaluated = len(evaluated)
        percentage = conforming / total_evaluated * 100 if total_evaluated else 0

        # candidatos ao alerta de vencimento (sem paginacao): mesmo escopo do
        # resumo, excluindo nao indicados e documentos sem validade
        aviso_vencimento = [
            document for document in active_documents
            if not document.nao_indicado and not document.sem_validade
        ]

        documentos_filtrados = [
            document for document in documents
            if DocumentsService._document_matches(document, status, busca)
        ]
        documentos_por_prestador = {}
        for document in documentos_filtrados:
            documentos_por_prestador.setdefault(document.prestador_id, []).append(document)

        prestadores_visiveis = []
        for provider in providers:
            if (provider.situacao == "descredenciado") != mostrar_descredenciados:
                continue
            if not mostrar_descredenciados and categoria and categoria != "todos" and provider.categoria_slug != categoria:
                continue

            tem_documento_correspondente = provider.id in documentos_por_prestador

            if status:
                if not tem_documento_correspondente:
                    continue
            elif busca:
                nome_bate = busca in (provider.nome or "").lower()
                if not nome_bate and not tem_documento_correspondente:
                    continue

            prestadores_visiveis.append(provider)

        prestadores_visiveis.sort(key=lambda provider: (provider.nome or "").lower())

        total_prestadores = len(prestadores_visiveis)
        offset = (pagina - 1) * por_pagina
        prestadores_pagina = prestadores_visiveis[offset:offset + por_pagina]
        ids_pagina = {provider.id for provider in prestadores_pagina}

        registros_pagina = [
            document for document in documentos_filtrados
            if document.prestador_id in ids_pagina
        ]

        return {
            "medicos": [DocumentsService.provider_to_dict(provider) for provider in prestadores_pagina],
            "registros": [DocumentsService.document_to_dict(document) for document in registros_pagina],
            "resumo": {
                "total": total_evaluated,
                "conformes": conforming,
                "pendentes": pending,
                "notificados": notified,
                "naoIndicados": len(active_documents) - total_evaluated,
            },
            "percentualTexto": f"{percentage:.2f}%".replace(".", ","),
            "avisoVencimento": [DocumentsService.document_to_dict(document) for document in aviso_vencimento],
            "totalPrestadores": total_prestadores,
            **build_pagination_meta(pagina, por_pagina, total_prestadores),
        }

    # Cadastra um documento
    @staticmethod
    def create(data):
        if not isinstance(data, dict):
            raise ValueError("Os dados do documento são inválidos.")
        provider_name = str(data.get("nome_medico") or "").strip()
        document_name = str(data.get("documento") or "").strip()
        if not provider_name:
            raise ValueError("O prestador é obrigatório.")
        provider = ProviderModel.get_by_name(provider_name)
        if not provider:
            raise ValueError("O prestador não foi encontrado.")
        if not document_name:
            raise ValueError("O nome do documento é obrigatório.")
        if len(document_name) > 255:
            raise ValueError("O nome deve ter no máximo 255 caracteres.")
        document = Document(
            prestador_id=provider.id,
            nome=document_name,
            sem_validade=True,
            status="CONFORME",
            status_manual=False,
        )
        document_id = DocumentModel.create(document)
        return DocumentsService.document_to_dict(DocumentModel.get_by_id(document_id))

    # Atualiza parcialmente um documento
    @staticmethod
    def update(document_id, data):
        document = DocumentsService.get_by_id(document_id)
        if not isinstance(data, dict):
            raise ValueError("Os dados enviados são inválidos.")
        date_changed = False
        if "documento" in data:
            name = str(data.get("documento") or "").strip()
            if not name:
                raise ValueError("O nome do documento é obrigatório.")
            if len(name) > 255:
                raise ValueError("O nome deve ter no máximo 255 caracteres.")
            document.nome = name
        if "data_vencimento" in data:
            document.data_vencimento = DocumentsService.parse_optional_date(
                data.get("data_vencimento"), "data de vencimento"
            )
            date_changed = True
            if document.data_vencimento:
                document.sem_validade = False
                if "data_maxima_notificacao" not in data:
                    document.data_notificacao = document.data_vencimento + timedelta(days=60)
            else:
                document.sem_validade = True
                document.data_notificacao = None
        if "data_maxima_notificacao" in data:
            document.data_notificacao = DocumentsService.parse_optional_date(
                data.get("data_maxima_notificacao"), "data de notificação"
            )
            date_changed = True
        if "semValidade" in data:
            document.sem_validade = DocumentsService.to_boolean(data.get("semValidade"))
            date_changed = True
            if document.sem_validade:
                document.data_vencimento = None
                document.data_notificacao = None
        if "naoIndicado" in data:
            document.nao_indicado = DocumentsService.to_boolean(data.get("naoIndicado"))
        if "documentacao" in data:
            document.observacao = str(data.get("documentacao") or "").strip() or None
        if "status" in data:
            status = str(data.get("status") or "").strip().upper()
            if status not in DocumentsService.ALLOWED_STATUSES:
                raise ValueError("O status informado é inválido.")
            document.status = status
            document.status_manual = True
        elif date_changed:
            document.status_manual = False
        if not document.status_manual:
            document.status = DocumentsService.calculate_status(
                document.data_vencimento,
                document.data_notificacao,
                document.sem_validade,
            )
        DocumentModel.update(document)
        return DocumentsService.document_to_dict(DocumentModel.get_by_id(document.id))

    # Salva ou substitui o anexo
    @staticmethod
    def save_file(document_id, uploaded_file, user_id=None):
        document = DocumentsService.get_by_id(document_id)
        old_file_id = document.arquivo_id
        year = document.data_vencimento.year if document.data_vencimento else date.today().year
        new_file = FileStorageService.save(
            uploaded_file=uploaded_file,
            category="documentacao",
            year=year,
            user_id=user_id,
            allowed_extensions={".pdf", ".doc", ".docx", ".jpg", ".jpeg", ".png"},
        )
        try:
            DocumentModel.update_file(document.id, new_file.id)
        except Exception:
            FileStorageService.delete(new_file.id)
            raise
        if old_file_id:
            FileStorageService.delete(old_file_id)
        return DocumentsService.document_to_dict(DocumentModel.get_by_id(document.id))

    # Retorna o caminho do anexo
    @staticmethod
    def get_file(document_id):
        document = DocumentsService.get_by_id(document_id)
        if not document.arquivo_id:
            raise ValueError("Este documento não possui arquivo.")
        return document, FileStorageService.resolve_path(document)

    # Exclui um documento e o anexo
    @staticmethod
    def delete(document_id):
        document = DocumentsService.get_by_id(document_id)
        file_id = document.arquivo_id
        if file_id:
            FileStorageService.delete(file_id)
        if not DocumentModel.delete(document.id):
            raise ValueError("Não foi possível excluir o documento.")
        return True
