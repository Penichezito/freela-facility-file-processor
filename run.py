import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Garantir que as importações funcionem corretamente
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar a aplicação Flask
from app.main import app

if __name__ == "__main__":
    # Criar diretório de armazenamento se não existir
    storage_path = os.environ.get("STORAGE_PATH", os.path.join(os.getcwd(), "storage"))
    os.makedirs(storage_path, exist_ok=True)
    
    # Obter porta da variável de ambiente ou usar o padrão 5000
    port = int(os.environ.get("PORT", 5000))
    
    # Iniciar o servidor
    app.run(
        host="0.0.0.0",
        port=port,
        debug=os.environ.get("FLASK_DEBUG", "1") == "1"
    )