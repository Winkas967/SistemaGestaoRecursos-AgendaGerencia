from models.modules_model import ModuleModel
from models.sector_permissions_model import SectorPermissionModel
from models.sectors_model import SectorModel

#contem as regras das permissoes dos setores
class SectorPermissionService:
    #converte um valor verdadeiro ou falso
    @staticmethod
    def to_boolean(value):
        if isinstance(value, bool):
            return value
        
        if value in (1, "1", "true", "True", "sim", "on"):
            return True
        
        return False
    
    #lista de modulos disponiveis
    @staticmethod
    def get_modules():
        modules = ModuleModel.get_all()
        
        return [
            module.to_dict()
            for module in modules
        ]
        
    #lista as permissoes de um setor
    @staticmethod
    def get_by_sector(sector_id):
        sector = SectorModel.get_by_id(sector_id)
        
        if not sector or not sector.ativo:
            raise ValueError("O setor informado não existe ou está inativo.")
        
        permissions = SectorPermissionModel.get_by_sector(sector_id)
        
        return [
            permission.to_dict()
            for permission in permissions
        ]
        
    #salva a permissao de um modulo para um setor
    @staticmethod
    def save(sector_id, data):
        try:
            sector_id = int(sector_id)
            module_id = int(data.get("modulo_id"))
            
        except (TypeError, ValueError):
            raise ValueError("O setor ou módulo informado é inválido.")
        
        #verifica se o setor existe
        sector = SectorModel.get_by_id(sector_id)
        
        if not sector or not sector.ativo:
            raise ValueError("O setor informado não existe ou está inativo.")
        
        #verifica se o modulo existe
        module = ModuleModel.get_by_id(module_id)
        
        if not module or not module.ativo:
            raise ValueError("O módulo informado não existe ou está inativo.")
        
        #converte as permissoes recebidas
        can_view = SectorPermissionService.to_boolean(
            data.get("pode_visualizar")
        )
        can_create = SectorPermissionService.to_boolean(
            data.get("pode_criar")
        )
        can_edit = SectorPermissionService.to_boolean(
            data.get("pode_editar")
        )
        can_delete = SectorPermissionService.to_boolean(
            data.get("pode_excluir")
        )
        
        #ativa a visualizacao quando existe outra permissao
        if can_create or can_edit or can_delete:
            can_view = True
        
        #salva as permissoes no banco
        SectorPermissionModel.save(
            setor_id = sector_id,
            modulo_id = module_id,
            pode_visualizar=can_view,
            pode_criar=can_create,
            pode_editar=can_edit,
            pode_excluir=can_delete
        )
        
        return SectorPermissionService.get_by_sector(sector_id)