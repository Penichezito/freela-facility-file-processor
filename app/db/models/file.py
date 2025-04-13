from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(BigInteger, nullable=False)
    content_type = Column(String, nullable=False)
    metadata = Column(Text)  # JSON string with metadata
    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    uploader = relationship("User", back_populates="files")
    project = relationship("Project", back_populates="files")