import os 
import json
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename

from flask import Blueprint, request, jsonify, current_app, send_file
from werkzeug.exceptions import BadRequest, NotFound

from app.db.database import db
from app.db.models.file import File
from app.db.models.tag import Tag
from app.services.file_service import save_file, delete_file, get_file_type
from app.services.tag_service import generate_tags_for_file, find_or_create_tag

files_bp = Blueprint("files", __name__, url_prefix="/files")

@files_bp.route("/upload", methods=["POST"])
def upload_file():
    """ Endpoint para upload de arquivo."""
    # Verificar se o arquivo foi enviado
    if "file" not in request.files:
        raise BadRequest("Nenhum arquivo enviado.")
    
    file = request.files["file"]

    if file.filename == "":
        raise BadRequest("Nenhum arquivo selecionado.")
    
    # Verificar se os metadados foram enviados
    metadata_str = request.form.get("metadata", "{}")
    try:
        metadata = json.loads(metadata_str)
    except json.JSONDecodeError:
        metadata = {}

    # Obter informações básicas do arquivo
    original_filename = secure_filename(file.filename)
    content_type = file.content_type or "application/octet-stream"

    # Gerar um nome único para o arquivo no aramazenamento
    ext = os.path.splitext(original_filename)[1]
    stored_filename = f"{uuid.uiid4().hex}{ext}"

    # Determinar o tipo de arquivo 
    file_type = get_file_type(original_filename, content_type)

    # Salva arquivo no sistema de arquivos
    file_path = save_file(file, stored_filename)
    file_size = os.path.getsize(file_path)

    # Criar o objeto File (registro do arquivo) no banco de dados
    new_file = File(
        original_filename=original_filename,
        stored_filename=stored_filename,
        file_path=file_path,
        file_type=file_type,
        file_size=file_size,
        content_type=content_type,
        metadata=metadata,
        external_id=metadata.get("external_id"),
        project_id=metadata.get("projects_id"),
        uploader_id=metadata.get("uploader_id"),
    )

    db.session.add(new_file)
    db.session.commit()

    # Gerar tagas automaticamente se habilitado
    if current_app.config["AUTO_TAG_ENABLED"]:
        tags = generate_tags_for_file(new_file)

        # Associar tags ao arquivo
        for tag_name in tags:
            tag = find_or_create_tag(tag_name, auto_generated=True)
            if tag not in new_file.tags:
                new_file.tags.append(tag)
                tag.usage_count += 1
        
        db.session.commit()

    # Retornar os dados do arquivo 
    return jsonify({
        "id": new_file.id,
        "original_filename": new_file.original_filename,
        "stored_filename": new_file.stored_filename,
        "file_path": new_file.file_path,
        "file_type": new_file.file_type,
        "file_size": new_file.file_size,
        "content_type": new_file.content_type,
        "metadata": new_file.metadata,
        "tags": [tag.name for tag in new_file.tags],
        "created_at": new_file.created_at.isoformat(),
    })

@files_bp.route("/", methods=["GET"])
def list_files():
    """ Listar arquivos com opção de filtrar por tags"""
    # Obter parâmetros de consulta
    project_id = request.args.get("project_id", type=int)
    uploader_id = request.args.get("uploader_id", type=int)
    file_type = request.args.get("file_type")
    tags = request.args.getlist("tags")

    # Construir a consulta
    query = File.query

    if project_id:
        query = query.filter(File.project_id == project_id)
    
    if uploader_id:
        query = query.filter(File.uploader_id == uploader_id)

    if file_type:
        query = query.filter(File.file_type == file_type)

    if tags:
        for tag_name in tags:
            tag = Tag.query.filter_by(name=tag_name).first()
            if tag:
                query = query.filter(File.tags.contains(tag))

    # Executar a consulta e obter os resultados
    files = query.all()

    return jsonify([file.todict() for file in files])

@files_bp.route("/<int:file_id/tags>", methods=["POST"])
def add_tags_to_files(file_id):
    """Adicionar tags a um arquivo"""
    file = File.query.get_or_404(file_id)

    # Obter a lista de tags do corpo da requisição
    data = request.get_json()
    if not data or "tags" not in data:
        raise BadRequest("Nenhuma tag fornecida.")

    tags_to_add = data["tags"]
    if not isinstance(tags_to_add, list):
        raise BadRequest("As tags devem ser uma lista.")
    
    # Adicionar cada tag ao arquivo
    added_tags = []
    for tag_name in tags_to_add:
        tag = find_or_create_tag(tag_name)
        if tag not in file.tags:
            file.tags.append(tag)
            tag.usage_count += 1
            added_tags.append(tag.name)

    db.session.commit()

    return jsonify({
        "message": "Tags adicionadas com sucesso.",
        "file_id": file.id,
        "added_tags": added_tags,
        "all_tags": [tag.name for tag in file.tags]
    })

@files_bp.route("/<int:file_id>/tags/tag_name>", methods=["DELETE"])
def remove_tag_from_file(file_id, tag_name):
    """Remover uma tag de um arquivo"""
    file = File.query.get_or_404(file_id)

    # Procurar a tag 
    tag = Tag.query.filter_by(name=tag_name).first()
    if not tag:
        raise NotFound("Tag não encontrada")
    
    # Remover a tag do arquivo
    if tag in file.tags:
        file.tags.remove(tag)
        tag.usage_count -= 1
        db.session.commit()

    return jsonify({
        "message": "Tag removida com sucesso.",
        "file_id": file.id,
        "removed_tag": tag_name,
        "remaining_tags": [tag.name for tag in file.tags]
    })

@files_bp.route("/<int:file_id>", methods=["DELETE"])
def delete_file_endpoint(file_id):
    """ Excluir um arquivo """
    file = File.query.get_or_404(file_id)

    # Excluir o arquivo do sistema de arquivos
    success = delete_file(file.file_path)

    if success:
        # Adicionar os contadores de uso das tags
        for tag in file.tags:
            tag.usage_count -= 1

        # Excluir o registro do banco de dados
        db.session.delete(file)
        db.session.commit()

        return jsonify({
            "message": "Arquivo deletado com sucesso.",
            "file_id": file.id
        })
    else:
        return jsonify({
            "message": "Erro ao deletar o arquivo do sistema de arquivos.",
            "file_id": file.id
        }), 207 # Multi-Status
    




