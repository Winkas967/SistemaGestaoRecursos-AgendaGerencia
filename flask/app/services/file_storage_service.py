import hashlib
from pathlib import Path
from uuid import uuid4

from flask import current_app
from werkzeug.utils import secure_filename

from models.files_model import File, FileModel


#gerencia os arquivos armazenados na pasta externa
class FileStorageService:
    
    #retorna a pasta principas dos arquivos
    @staticmethod
    def get_upload_root():
        upload_root = current_app.config.get("UPLOAD_ROOT")
        
        if not upload_root:
            raise ValueError("A pasta de armazenamento não foi configurada.")
        
        return Path(upload_root).resolve()
    
    #valida o arquivo recebido
    @staticmethod
    def validate_file(uploaded_file, allowed_extensions):
        if not uploaded_file:
            raise ValueError("O arquivo é obrigatório.")
        
        original_name = Path(
            uploaded_file.filename or ""
        ).name.strip()
        
        if not original_name:
            raise ValueError("O arquivo enviado é inválido.")
        
        extension = Path(original_name).suffix.lower()
        
        if extension not in allowed_extensions:
            allowed_text = ", ".join(
                sorted(allowed_extensions)
            )
            
            raise ValueError(f"Formato não permitido. Utilize: {allowed_text}.")
        
        return original_name, extension
    
    #salva um arquivo na pasta externa
    @staticmethod
    def save(
        uploaded_file,
        category,
        year,
        user_id=None,
        allowed_extensions=None
    ):
        if allowed_extensions is None:
            allowed_extensions = {".pdf"}
            
        original_name, extension = (
            FileStorageService.validate_file(
                uploaded_file,
                allowed_extensions
            )
        )
        
        upload_root = FileStorageService.get_upload_root()
        relative_directory = Path(category) / str(year)
        destination_directory = (
            upload_root / relative_directory
        )
        
        destination_directory.mkdir(
            parents=True,
            exist_ok=True
        )
        
        safe_base_name = secure_filename(
            Path(original_name).stem
        ) or "arquivo"
        
        stored_name = (
            f"{safe_base_name}_{uuid4().hex}{extension}"
        )
        
        relative_path = (
            relative_directory / stored_name
        )
        absolute_path = upload_root / relative_path
        
        hash_calculator = hashlib.sha256()
        file_size = 0
        
        try:
            uploaded_file.stream.seek(0)
            
            with absolute_path.open("wb") as destination:
                while True:
                    chunk = uploaded_file.stream.read(
                        1024 * 1024
                    )
                    
                    if not chunk:
                        break
                    
                    destination.write(chunk)
                    hash_calculator.update(chunk)
                    file_size += len(chunk)
                    
            if file_size == 0:
                raise ValueError("O arquivo enviado está vazio.")
            
            file_record = File(
                nome_original=original_name,
                nome_armazenado=stored_name,
                caminho_relativo=relative_path.as_posix(),
                mime_type=(
                    uploaded_file.mimetype or "application/octet-stream"
                ),
                tamanho_bytes=file_size,
                hash_sha256=hash_calculator.hexdigest(),
                enviado_por_id=user_id
            )
            
            file_id = FileModel.create(file_record)
            
            return FileModel.get_by_id(file_id)
        
        except Exception:
            if absolute_path.exists():
                absolute_path.unlink()
                
            raise
        
        
    #retorna o caminho absoluto de um arquivo
    @staticmethod
    def resolve_path(file_record):
        if not file_record:
            raise ValueError("O arquivo não foi encontrado.")
        
        upload_root = FileStorageService.get_upload_root()
        absolute_path = (
            upload_root / file_record.caminho_relativo
        ).resolve()
        
        try:
            absolute_path.relative_to(upload_root)
        except ValueError:
            raise ValueError(
                "O caminho do arquivo é inválido."
            )
            
        if not absolute_path.is_file():
            raise ValueError("O arquivo não existe na pasta do servidor.")
        
        return absolute_path
    
    #exclui o arquivo fisico e o registro do banco
    @staticmethod
    def delete(file_id):
        file_record = FileModel.get_by_id(file_id)
        
        if not file_record:
            return False
        
        absolute_path = (
            FileStorageService.get_upload_root() / file_record.caminho_relativo
        ).resolve()
        
        upload_root = (
            FileStorageService.get_upload_root()
        )
        
        try:
            absolute_path.relative_to(upload_root)
        except ValueError:
            raise ValueError("O caminho do arquivo é inválido.")
        
        if absolute_path.is_file():
            absolute_path.unlink()
            
        FileModel.delete(file_record.id)
        
        return True
