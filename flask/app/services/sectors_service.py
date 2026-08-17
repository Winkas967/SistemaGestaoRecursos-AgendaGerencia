from models.sectors_model import SectorModel

#contem as regras de negocio dos setores
class SectorService:
    #lista de setores ativos
    @staticmethod
    def get_all():
        sectors = SectorModel.get_all()
        
        return [
            sector.to_dict()
                for sector in sectors
        ]
    
    #cadastra um novo setor
    @staticmethod
    def create(data):
        name = str(data.get("nome") or "").strip()
        
        #verifica se o nome foi preenchido
        if not name:
            raise ValueError("O nome do setor é obrigatório.")
        
        #verifica o tamanho minimo do nome
        if len(name) < 2:
            raise ValueError(
                "O nome do setor deve ter pelo menos 2 caracteres."
            )
            
        #verifica o tamanho maximo permitido no banco
        if len(name) > 100:
            raise ValueError("O nome do setor deve ter no máximo 100 caracteres.")
        
        #impede o cadastro de setores duplicados
        existing_sector = SectorModel.get_by_name(name)
        
        if existing_sector:
            raise ValueError("Já existe um setor cadastrado com esse nome.")
        
        #cadastra um setor no banco
        sector_id = SectorModel.create(name)
        
        #busca o setor que acabou de ser criado
        created_sector = SectorModel.get_by_id(sector_id)
        
        if not created_sector:
            raise RuntimeError("O setor foi criado, mas não pode ser consultado.")
        
        return created_sector.to_dict()
        