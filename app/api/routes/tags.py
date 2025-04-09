from flask import Blueprint, request, jsonify
from werkzeug.exceptions import BadRequest, NotFound

from app.db.database import db
from app.db.models.tag import Tag
tags_bp = Blueprint("tags", __name__, url_prefix="/tags")

@tags_bp.route("/", methods=["GET"])
def list_tags():
    """Listar todas as tags com opção de filtro"""
    # Obter parâmetros de consulta 
    auto_generated = request.args.get("auto_generated")
    search = request.args.get("search")

    # Construir consulta
    query = Tag.query
    if auto_generated is not None:
        auto_generated = auto_generated.lower() == "true"
        query = query.filter(Tag.auto_generated == auto_generated)

    if search:
        query = query.filter(Tag.name.ilike(f"%{search}%"))

    # Ordenar por contagem de uso (mais usadas primeiro)
    query = query.order_by(Tag.usage_count.desc())

    # Executar a consulta 
    tags = query.all()

    # Retornar os dados das tags
    return jsonify([tag.to_dict() for tag in tags])

@tags_bp.route("/<int:tag_id>", methods=["GET"])
def get_tag(tag_id):
    """Obter detalhes de uma tag específica"""
    tag = Tag.query.get_or_404(tag_id)
    return jsonify(tag.to_dict())

@tags_bp.route("/", methods=["POST"])
def create_tag(tag_id):
    """Criar uma nova tag"""
    data = request.get_json()

    # Verificar se a tag já existe
    existing_tag = Tag.query.filter_by(name=data["name"]).first()
    if existing_tag:
        return jsonify(existing_tag.to_dict()), 200
    
    # Criar nova tag
    new_tag = Tag(
        name=data["name"],
        description=data.get("description"),
        auto_generated=data.get("auto_generated", False)
    ) 

    db.session.add(new_tag)
    db.session.commit()

    return jsonify(new_tag.to_dict()), 201

@tags_bp.route("/<int:tag_id>", methods=["PUT"])
def update_tag(tag_id):
    """Atualizar uma tag existente"""
    tag = Tag.query.get_or_404(tag_id)
    data = request.get_json()

    if not data:
        raise BadRequest("Nenhum dado fornecido")
    
    # Atualizar os campos da tag
    if "name" in data: 
        # Verificar se o novo nome já está em uso
        if data["name"] != tag.name and Tag.query.filter_by(name=data["name"]).first():
            raise BadRequest("Uma Tag com esse nome já existe")
        tag.name = data["name"]

    if " description" in data:
        tag.description = data["description"]

    if "auto_generated" in data:
        tag.auto_generated = data["auto_generated"]

    db.session.commit()

    return jsonify(tag.to_dict())

@tags_bp.route("/<int:tag_id>", method=["DELETE"])
def delete_tag(tag_id):
    """Excluir uma tag """
    tag = Tag.query.get_or_404(tag_id)

    # Remover a tag de todos os arquivos
    for file in tag.files:
        file.tags.remove(tag)

    # Excluir a tag
    db.session.delete(tag)
    db.session.commit()

    return jsonify({
        "message": "Tag deleted successfully",
        "tag_id": tag_id
    })

@tags_bp.route("/files/<int:tag_id>", method=["GET"])
def get_files_by_tag(tag_id):
    """Obter todos os arquivos associados a uma tag"""
    tag = Tag.query.get_or_404(tag_id)

    # Obter todos os arquivos associados à tag
    files = tag.files.all()

    return jsonify([file.to_dict() for file in files])