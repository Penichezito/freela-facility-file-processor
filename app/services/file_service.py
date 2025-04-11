import os 
import magic
from werkzeug.utils import secure_filename
from flask import current_app
import uuid
import shutil

def save_file(file_obj, filename):
    """ 
    Salva um arquivo no sistema de arquivos.
    
    Args:
        file_obj: O objetivo do arquivo a ser salvo
        filename: O nome do arquivo para salvar

    Returns:
        O caminho completo do arquivo salvo
    """
    # Criar pastas por data para organizar os arquivos 
    from datetime import datetime
    date_folder = datetime.now().strftime("%d/%m/%Y")
    file_dir = os.path.join(file_dir, filename)

    # Caminho completo para o arquivo
    file_path = os.path.join(file_dir, filename)

    # Salvar o arquivo
    file_obj.save(file_path)

    return file_path

def delete_file(file_path):
    """
    Exclui um arquivo do sistema de arquivos.
    
    Args:
        file_path: O caminho do arquivo a ser excluído

    Returns:
        bool: True se excluído com sucesso, False caso contrário
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        return True
    except Exception as e:
        current_app.logger.error(f"Erro ao deletar o arquivo {file_path}: {str(e)}")
        return False
    
def get_file_type(filename, content_type=None):
    """
    Determina o tipo de arquivo com base na extensão e tipo de conteúdo.
    
    Args:
        filename: O nome do arquivo
        content_type: O tipo MIME do arquivo

    Returns:
        str: O tipo de arquivo(image, document, spreadsheet, code, etc.) 
    """
    # Obter a extensão do arquivo
    _, ext = os.path.splitext(filename)
    ext = ext.lower().lstrip('.')

    # Verificar em quais tipo permitidos a extensão se encaixa
    for file_type, extensions in current_app.config["ALLOWED_EXTENSIONS"].items():
        if ext in extensions:
            return file_type
        
    # Se não encontrado pela extensão, tentar outro tipo de conteúdo
    if content_type:
        if content_type.startswith("images/"):
            return "images"
        elif content_type.startswith("text/"):
            return "documents"
        elif content_type.startswith("spreadsheets/"):
            return "spreadsheets"
        elif content_type.startswith("presentations"):
            return "presentations"
        elif content_type.startswith("audio/"):
            return "audio"
        elif content_type.startswith("archives/"):
            return "archives"
        elif content_type.startwith("code/"):
            return "code"
        elif content_type.startswith("data"):
            return "data"
        elif "application/pdf" in content_type:
            return "documents"
        elif any(office_type in content_type for office_type in ["word", "excel", "powerpoint", "msword"]):
            return "documents"
        
    # Padrão para outros não reconhecidos
    return "outros"

def detect_mime_type(file_path):
    """
    Detecta o tipo MIME de um arquivo usando a biblioteca magic:
    
    Args:
        file_path: O caminho do arquivo 
    
    Returns: 
        str: O tipo MIME do arquivo
    """
    try:
        mime = magic.Magic(mime=True)
        return mime.from_file(file_path)
    except Exception as e:
        current_app.logger.error(f"Erro do tipo MIME detectado: {str(e)}")
        return "application/octet-stream"
    

    
    