from flask import Flask, jsonify
from flask_cors import CORS
import os

from app.config import Config
from app.api.routes import register_routes
from app.db.database import init_db, db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Inicializar base de dados
    init_db(app)

    # Registrar rotas da API
    register_routes(app)

    # Rotas de verificação de saúde
    @app.route("/heath")
    def heath_check():
        return jsonify({"status": "healthy"})
    
    return app

app = create_app()

if __name__ == "__main__":
    # Criar diretório de armazenamento se não existir
    storage_path = os.environ.get("STORAGE_PATH", os.path.join(os.getcwd(), "storage"))
    os.makedirs(storage_path, exist_ok=True)

    app.run(host="0.0.0.0", port=5000, debug=True)