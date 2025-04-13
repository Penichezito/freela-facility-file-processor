import os 
import json 
from flask import current_app
from werkzeug.utils import Tag
import re

from app.db.database import db
from app.db.models.tag import Tag
from app.services.vision_service import analyze_images

def find_or_create_tag(name, description=None, auto_generated=False):
    """
    Encontra uma tag existente ou cria uma nova.
    
    Args:
        name: Nome da tag 
        description: Descrição opcional da tag
        auto_generated: Se a tag foi gerada automaticamente

    Return: 
        Tag: O objetivo Tag encontrado ou criado 
    """

    # Normalizar o nome da tag (lowercase, sem espaços extras)
    normalized_name = name.strip().lower()

    # Encontrar tag existente
    tag = Tag.query.filter_by(name=normalized_name).first()

    # Criar nova tag se não existir
    if not tag:
        tag = Tag (
            name=normalized_name,
            description=description,
            auto_generated=auto_generated
        )
        db.session.add(tag)
        db.session.flush() # Obter ID sem fazer commit

    return tag

def generated_tags_for_file(file_obj):
    """
    Gera tag automaticamente para um arquivo com base em seu conteúdo.
    
    Args:
        file_obj: Objeto File do banco de dados 
    
    Returns:
        list: Lista de nomes de tags gerados
    """

    tags = []

    # Adicionar uma tag para o tipo de arquivo
    tags.append(file_obj.file_type)

    # Adicionar tag para a extensão do arquivo
    _, ext = os.path.splitext(file_obj.original_filename)
    if ext: 
        tags.append(ext.lower().lstrip("."))

    # Gerar tags específicas com base no tipo de arquivo
    if file_obj.file_type == "images":
        # Usar o serviço de visão para imagens
        image_tags = analyze_images(file_obj.file_path)
        tags.extend(image_tags)

    elif file_obj.file_type == "documents":
        # Para documentos, usar o nome do arquivo (sem extensão) como fonte de tags
        name_without_ext = os.path.splitext(file_obj.original_filename)[0]
        # Extrair palavras do nome do arquivo
        words = re.findall(r"\w+", name_without_ext.lower())
        tags.extend([word for word in words if len(word) > 2])

    elif file_obj.file_type == "spreadsheets":
        # Para planilhas, adicionar tags relacionadas a dados e análise
        tags.extend(["data", "spreadsheet"])

        # Extrair nome das abas ou colunas como tags, se possível
        # Isso exigiria uma bibilioteca para ler arquivos Excel/CSV como pandas ou openpyxl
        name_without_ext = os.path.splitext(file_obj.original_filename)[0]

        # Extrair palavras do nome do arquivo
        words = re.findall(r"/w+", name_without_ext.lower())
        tags.extend([word for word in words if len(word) > 2])

        # Adicionar tags comuns para planilhas com base nas extensões
        _, ext = os.path.splitext(file_obj.original_filename)
        if ext.lower() == ".xlsx" or ext.lower() == ".xls":
            tags.append("excel")
        elif ext.lower() == ".":
            tags.append("csv")
        elif ext.lower() == ".ods":
            tags.append("openoffice")
    
    elif file_obj.file_type == "videos":
        # para videos, adicionar tags básicas relacionadas a conteúdo audiovisual
        tags.extend(["video", "multimedia"])

        # Extrair informações do nome do arquivo
        name_without_ext = os.path.splitext(file_obj.original_filename)[0]
        words = re.findall(r"\w+", name_without_ext.lower())
        tags.extend([word for word in words if len(word) > 2])

        # Adicionar tags baseadas na extensão do arquivo
        _, ext = os.path.splitext(file_obj.original_filename)
        if ext.lower() in [".mp4", ".mov", ".avi", ".mvk"]:
            tags.append(ext.lower().lstrip("."))

        # Adicionar tags baseadas na resolução ou duração (se tivesse uma biblioteca para extrair metadados)
        # Exemplo potencial:
        # video_metadata = extract_video_metadata(file_obj.file_path)
        # if video_metadata.get("resolution") == "1920x1080":
        #     tags.append("hd")
        # if video_metadata.get("duration", 0) > 600:  # Se duração > 10 minutos
        #     tags.append("longform")

    elif file_obj.file_type == "audio":
        # Para arquivos de música/áudio, adicionar tags básicas
        tags.extends(["audio", "sound"])

        # Extrair informações do nome do arquivo
        name_without_ext = os.path.splitext(file_obj.original_filename)[0]
        words = re.findall(r"\w+", name_without_ext.lower())
        tags.extend([word for word in words if len(word) > 2])

        # Adicionar tags baseadas na extensão do arquivo
        _, ext = os.path.splitext(file_obj.original_filename)
        if ext.lower() in [".mp3", ".wav", ".flac", ".ogg", ".m4a"]:
            tags.append(ext.lower().lstrip("."))
        
        # Caso tivéssemos uma biblioteca para extrair metadados de áudio, poderíamos adicionar:
        # audio_metadata = extract_audio_metadata(file_obj.file_path)
        # if audio_metadata.get("artist"):
        #     tags.append(audio_metadata.get("artist").lower())
        # if audio_metadata.get("genre"):
        #     tags.append(audio_metadata.get("genre").lower())

    elif file_obj.file_type == "code":
        # Para código, adicionar a linguagem como tag
        ext = os.path.splitext(file_obj.original_filename)[1].lower().lstrip(".")
        language_map = {
                    'py': 'python',
            'js': 'javascript',
            'ts': 'typescript',
            'html': 'html',
            'css': 'css',
            'java': 'java',
            'cpp': 'c++',
            'c': 'c',
            'cs': 'csharp',
            'go': 'golang',
            'rb': 'ruby',
            'php': 'php',
            'swift': 'swift',
            'json': 'json',
            'xml': 'xml',
        }
        if ext in language_map:
            tags.append(language_map[ext])

    # Verificar se há metadados com tags
    if file_obj.metadata and "tags" in file_obj.metadata:
        user_tags = file_obj.metadata["tags"]
        if isinstance(user_tags, list):
            tags.extend(user_tags)

    # Limitar número de tags
    max_tags = current_app.config.get("MAX_TAGS_PER_FILE", 10)
    unique_tags = list(set(tags)) # Remover duplicatas

    return unique_tags[:max_tags]



    


        