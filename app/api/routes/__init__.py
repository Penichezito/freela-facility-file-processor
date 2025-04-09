from flask import Blueprint

def register_routes(app):
    """ Rgistra todas as rotas da API"""
    from app.api.routes.files import files_bp
    from app.api.routes.tags import tags_bp

    api_bp = Blueprint("api", __name__, url_prefix="/api")