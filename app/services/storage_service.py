import os
import uuid
import shutil
from typing import Tuple, Optional
from werkzeug.utils import secure_filename
from flask import current_app
from datetime import datetime

def get_storage_path() -> str:
    """
    Retorna o caminho base do armazenamento de arquivos.
    """
    return current_app.config['UPLOAD_FOLDER']

def get_date_path() -> str:
    """
    Retorna o caminho de pasta baseado na data atual (ano/mês/dia).
    """
    today = datetime.now()
    return os.path.join(
        str(today.year),
        str(today.month).zfill(2),
        str(today.day).zfill(2)
    )

def generate_unique_filename(original_filename: str) -> str:
    """
    Gera um nome de arquivo único baseado em UUID.
    
    Args:
        original_filename: Nome original do arquivo
        
    Returns:
        Nome de arquivo único com a mesma extensão
    """
    ext = os.path.splitext(original_filename)[1]
    return f"{uuid.uuid4().hex}{ext}"

def ensure_directory_exists(directory: str) -> None:
    """
    Certifica-se de que o diretório existe, criando-o se necessário.
    
    Args:
        directory: Caminho do diretório a verificar/criar
    """
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

def save_file(file_obj, filename: Optional[str] = None) -> Tuple[str, str]:
    """
    Salva um arquivo no sistema de armazenamento.
    
    Args:
        file_obj: Objeto de arquivo a salvar
        filename: Nome de arquivo opcional (se não fornecido, gera um nome único)
        
    Returns:
        Tupla (caminho do arquivo salvo, nome do arquivo armazenado)
    """
    # Obtém o caminho base do armazenamento
    storage_path = get_storage_path()
    
    # Adiciona subdiretório baseado na data
    date_path = get_date_path()
    target_dir = os.path.join(storage_path, date_path)
    
    # Certifica-se de que o diretório existe
    ensure_directory_exists(target_dir)
    
    # Determina o nome do arquivo
    if not filename:
        original_filename = secure_filename(file_obj.filename)
        stored_filename = generate_unique_filename(original_filename)
    else:
        stored_filename = filename
    
    # Caminho completo do arquivo
    file_path = os.path.join(target_dir, stored_filename)
    
    # Salva o arquivo
    file_obj.save(file_path)
    
    return file_path, stored_filename

def delete_file(file_path: str) -> bool:
    """
    Exclui um arquivo do sistema de armazenamento.
    
    Args:
        file_path: Caminho do arquivo a excluir
        
    Returns:
        Boolean indicando sucesso (True) ou falha (False)
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            # Opcionalmente, pode-se tentar remover diretórios vazios
            return True
        return False
    except Exception as e:
        current_app.logger.error(f"Erro ao deletar o arquivo {file_path}: {str(e)}")
        return False

def move_file(source_path: str, target_dir: str, new_filename: Optional[str] = None) -> Tuple[str, str]:
    """
    Move um arquivo de um local para outro.
    
    Args:
        source_path: Caminho atual do arquivo
        target_dir: Diretório de destino
        new_filename: Novo nome para o arquivo (opcional)
        
    Returns:
        Tupla (novo caminho do arquivo, nome do arquivo)
    """
    # Certifica-se de que o diretório de destino existe
    ensure_directory_exists(target_dir)
    
    # Determina o nome do arquivo de destino
    if new_filename:
        target_filename = new_filename
    else:
        target_filename = os.path.basename(source_path)
    
    # Caminho completo de destino
    target_path = os.path.join(target_dir, target_filename)
    
    # Move o arquivo
    shutil.move(source_path, target_path)
    
    return target_path, target_filename

def get_file_url(file_path: str) -> str:
    """
    Gera uma URL para acessar o arquivo.
    
    Args:
        file_path: Caminho do arquivo
        
    Returns:
        URL para acessar o arquivo
    """
    # Remove o caminho base de armazenamento para obter o caminho relativo
    storage_path = get_storage_path()
    if file_path.startswith(storage_path):
        relative_path = file_path[len(storage_path):].lstrip('/')
    else:
        relative_path = file_path
    
    # Constrói a URL (pode ser adaptado conforme necessário)
    base_url = current_app.config.get('FILE_BASE_URL', '/files')
    return f"{base_url}/{relative_path}"