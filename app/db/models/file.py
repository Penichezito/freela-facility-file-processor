from datetime import datetime
from app.db.database import db

# Tabela de associação entre arquivos e tags
file_tags = db.Table("file_tags",
    db.Column("file_id", db.Integer, db.ForeignKey("file.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeinKey("tag.id"), primary_key=True)
)

class File(db.Model):
    __tablename__ = "files"

    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False, unique=True)
    file_path = db.Column(db.String(512), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    file_size = db.Column(db.BigInteger, nullable=False)
    content_type = db.Column(db.String(100), nullable=False)
    
    # Metadados adicionais
    metadata = db.column(db.JSON, nullable=True)

    # Campos para rastreamento de alterações
    external_id = db.Column(db.Integer, nullable=True)
    project_id = db.Column(db.Integer, nullable=True)
    uploader_id = db.Column(db.Integer, nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.now(datetime.timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(datetime.timezone.utc), onupdate=datetime.now(datetime.timezone.utc))

    # Relações
    tags = db.relationships("Tag", secondary=file_tags, backref=db.backref("files", lazy="dynamic"))

    def __repr__(self):
        return f"<File {self.original_filename}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "original_filename": self.original_filename,
            "stored_filename": self.stored_filename,
            "file_path": self.file_path,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "content_type": self.content_type,
            "metadata": self.metadata,
            "external_id": self.external_id,
            "project_id": self.project_id,
            "uploader_id": self.uploader_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "tags": [tag.to_dict() for tag in self.tags]
        }
    

