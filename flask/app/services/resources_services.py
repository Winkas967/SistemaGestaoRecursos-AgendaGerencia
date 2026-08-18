from models.resource_types_model import ResourceTypeModel
from models.resources_model import Resource, ResourceModel

#contem as regras de negocio dos recursos
class ResourceService:
    ALLOWED_STATUSES = {
        "disponivel",
        "manutencao",
        "indisponivel",
    }
    
    #lista todos os recursos ativos
    @staticmethod
    def get_all():
        resources = ResourceModel.get_all()
        
        return [
            resource.to_dict()
            for resource in resources
        ]
        
    #lista as opcoes usadas nos formularios
    @staticmethod
    def get_form_options():
        resource_types = ResourceTypeModel.get_all()
        
        return {
            "tipos_recursos": [
                resource_type.to_dict()
                for resource_type in resource_types 
            ],
            "status": sorted(ResourceService.ALLOWED_STATUSES),
        }
        
    #valida os dados recebidos
    @staticmethod
    def validade_data(data):
        name = str(data.get("nome") or "").strip()
        description = str(data.get("descricao") or "").strip() or None
        status = str(data.get("status") or "disponivel").strip.lower()
        resource_type_id = data.get("tipo_recurso_id")
        
        if not name:
            raise ValueError("O nome do recurso é obrigatório.")
        
        if len(name) < 2:
            raise ValueError(" O nome do recurso deve ter pelo menos 2 caracteres.")
        
        if len(name) > 120:
            raise ValueError("O nome do recurso deve ter no máximo 120 caracteres.")
        
        if description and len(description) > 255:
            raise ValueError("A descrição deve ter no máximo 255 caracteres.")
        
        if status not in ResourceService.ALLOWED_STATUSES:
            raise ValueError("O status informado é inválido.")
        
        try:
            resource_type_id = int(resource_type_id)
        except (TypeError, ValueError):
            raise ValueError("O tipo de recurso informado é inválido.")
        
        resource_type = ResourceTypeModel.get_by_id(resource_type_id)
        
        if not resource_type or not resource_type.ativo:
            raise ValueError(
                "O tipo de recurso não existe ou está inativo."
            )
            
        return {
            "nome": name,
            "descricao": description,
            "status": status,
            "tipo_recurso_id": resource_type_id,
        }
        
    #cadastro um novo recurso
    @staticmethod
    def create(data):
        validated_data = ResourceService.validade_data(data)
        
        resource = Resource(
            id=None,
            tipo_recurso_id=validated_data["tipo_recurso_id"],
            nome=validated_data["nome"],
            descricao=validated_data["descricao"],
            status=validated_data["status"],
        )
        
        resource_id = ResourceModel.create(resource)
        created_resource = ResourceModel.get_by_id(resource_id)
        
        if not created_resource:
            raise RuntimeError("O recurso foi criado, mas não pôde ser consultado.")
        
        return created_resource.to_dict()
    
    #atualiza um recurso existente
    @staticmethod
    def update(resource_id, data):
        existing_resource = ResourceModel.get_by_id(resource_id)
        
        if not existing_resource or not existing_resource.ativo:
            raise ValueError("O recurso informado não existe.")
        
        validated_data = ResourceService.validade_data(data)
        
        resource =  Resource(
            id=existing_resource.id,
            tipo_recurso_id=validated_data["tipo_recurso_id"],
            nome=validated_data["nome"],
            descricao=validated_data["descricao"],
            status=validated_data["status"],
        )
        
        ResourceModel.update(resource)
        
        update_resource = ResourceModel.get_by_id(resource_id)
        
        return update_resource.to_dict()
    
    #atualiza somente o status doi recurso
    @staticmethod
    def update_status(resource_id, data):
        resource = ResourceModel.get_by_id(resource_id)
        status = str(data.get("status") or "").strip().lower()
        
        if not resource or not resource.ativo:
            raise ValueError("O recurso informado não existe.")
        
        if status not in ResourceService.ALLOWED_STATUSES:
            raise ValueError("O status informado é inválido.")
        
        ResourceModel.update_status(resource_id, status)
        
        updated_resource = ResourceModel.get_by_id(resource_id)
        
        return updated_resource.to_dict()
    
    #desativa um recurso sem apagar o historico
    def deactivate(resource_id):
        resource = ResourceModel.get_by_id(resource_id)
        
        if not resource or not resource.ativo:
            raise ValueError("O recurso informado não existe ou já está inativo.")
        
        ResourceModel.deactivate(resource_id)