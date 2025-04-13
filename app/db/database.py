from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)

def init_db(app):
    """Inicializa o banco de dados com a aplicação Flask"""
    db.init_app(app)

    with app.app_context():
        # Importe todos os modelos aqui para garantir que eles sejam registrados com o SQLAlchemy
        from app.db.models.file import File
        from app.db.models.tag import Tag

        # Crie todas as tabelas no banco de dados
        db.create_all()