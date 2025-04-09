from flask import Blueprint

def register_routes(app):
    """ Rgistra todas as rotas da API"""
    from app.api.routes.files import files_bp
    from app.api.routes.tags import tags_bp

    api_bp = Blueprint("api", __name__, url_prefix="/api")

    # Registra os blueprints das rotas 
    api_bp.register_blueprint(files_bp)
    api_bp.register_blueprint(tags_bp)

    # Registra o blueprint principal
    app.register_blueprint(api_bp)

