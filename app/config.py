import os 
from datetime import timedelta

class Config:
    # Chave secreta para sessões e tokens
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

    # Configurações de banco de dados
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #  Configurações de upload de arquivos
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  
    UPLOAD_FOLDER = os.environ.get("STORAGE_PATH", os.path.join(os.getcwd(), "storage"))

    # Configuração de Google Cloud Vision APi
    GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", None)

    # Tipos de arquivos permitidos
    ALLOWED_EXTENSIONS = {
            "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg", ".webp", ".ico", ".raw", ".psd"],
            "documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".md", ".tex", ".epub", ".mobi", ".azw", ".pages"],
            "spreadsheets": [".xls", ".xlsx", ".csv", ".tsv", ".ods", ".numbers", ".xlsm", ".xlsb", ".xltx", ".xltm"],
            "presentations": [".ppt", ".pptx", ".key", ".odp", ".pps", ".ppsx"],
            "videos": [".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".webm", ".m4v", ".mpg", ".mpeg", ".3gp", ".ogv"],
            "music": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".opus", ".alac", ".aiff", ".mid", ".midi"],
            "archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso"],
            "code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".h", ".php", ".rb", ".go", ".swift", ".json", ".xml"],
            "data": [".db", ".sqlite", ".sql", ".json", ".xml", ".yaml", ".yml", ".parquet", ".feather", ".hdf5", ".h5"]
        }
    
    # Configurações de tag
    AUTO_TAG_ENABLED = True
    MAX_TAGS_PER_FILE = 10
    
    # Limite de requisições por minuto (para evitar abusos)
    RATE_LIMIT = 60