import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from app import create_app
from app.config import Config
from app.db.database import db
from app.db.models.file import File
from app.db.models.tag import Tag
from app.services.tag_service import find_or_create_tag, generate_tags_for_file


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    UPLOAD_FOLDER = tempfile.mkdtemp()
    AUTO_TAG_ENABLED = True
    MAX_TAGS_PER_FILE = 10


class TagServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_find_or_create_tag(self):
        # Teste de criação de tag
        with self.app.app_context():
            tag = find_or_create_tag("test_tag", "Test Description", False)
            self.assertIsNotNone(tag)
            self.assertEqual(tag.name, "test_tag")
            self.assertEqual(tag.description, "Test Description")
            self.assertFalse(tag.auto_generated)
            
            # Verificar se a tag foi salva no banco
            db_tag = Tag.query.filter_by(name="test_tag").first()
            self.assertIsNotNone(db_tag)
            self.assertEqual(db_tag.id, tag.id)
            
            # Teste de recuperação de tag existente
            same_tag = find_or_create_tag("test_tag", "Ignored Description", True)
            self.assertEqual(same_tag.id, tag.id)
            self.assertEqual(same_tag.description, "Test Description")  # Mantém a descrição original
            self.assertFalse(same_tag.auto_generated)  # Mantém o valor original
            
            # Teste de normalização do nome
            uppercase_tag = find_or_create_tag("TEST_TAG", "Another Description", True)
            self.assertEqual(uppercase_tag.id, tag.id)
            
            # Teste de espaços extras
            space_tag = find_or_create_tag("  test_tag  ", "Another Description", True)
            self.assertEqual(space_tag.id, tag.id)

    @patch('app.services.tag_service.analyze_images')
    def test_generate_tags_for_file(self, mock_analyze_images):
        # Configurar mock para análise de imagens
        mock_analyze_images.return_value = ["object1", "object2"]
        
        with self.app.app_context():
            # Criar um arquivo de teste
            file_obj = File(
                original_filename="test_image.jpg",
                stored_filename="stored_test_image.jpg",
                file_path="/path/to/image.jpg",
                file_type="images",
                file_size=1024,
                content_type="image/jpeg",
                metadata=None
            )
            
            # Salvar no banco para obter ID
            db.session.add(file_obj)
            db.session.commit()
            
            # Testar geração de tags para imagem
            tags = generate_tags_for_file(file_obj)
            
            # Verificar tags específicas para imagens
            self.assertIn("images", tags)  # Tag do tipo de arquivo
            self.assertIn("jpg", tags)     # Tag da extensão
            
            # Verificar tags da análise de imagem
            self.assertIn("object1", tags)
            self.assertIn("object2", tags)
            
            # Verificar chamada do mock
            mock_analyze_images.assert_called_once_with(file_obj.file_path)
            
            # Testar limite de tags
            with patch('app.services.tag_service.current_app') as mock_app:
                mock_app.config.get.return_value = 3  # MAX_TAGS_PER_FILE
                limited_tags = generate_tags_for_file(file_obj)
                self.assertEqual(len(limited_tags), 3)
    
    def test_generate_tags_for_document(self):
        with self.app.app_context():
            # Criar um arquivo de documento
            file_obj = File(
                original_filename="important_report.pdf",
                stored_filename="stored_report.pdf",
                file_path="/path/to/report.pdf",
                file_type="documents",
                file_size=2048,
                content_type="application/pdf",
                metadata=None
            )
            
            # Salvar no banco para obter ID
            db.session.add(file_obj)
            db.session.commit()
            
            # Testar geração de tags para documento
            tags = generate_tags_for_file(file_obj)
            
            # Verificar tags básicas
            self.assertIn("documents", tags)  # Tag do tipo
            self.assertIn("pdf", tags)        # Tag da extensão
            
            # Verificar palavras extraídas do nome
            self.assertIn("important", tags)
            self.assertIn("report", tags)
    
    def test_generate_tags_with_metadata(self):
        with self.app.app_context():
            # Criar um arquivo com metadados que incluem tags
            file_obj = File(
                original_filename="file_with_metadata.txt",
                stored_filename="stored_metadata.txt",
                file_path="/path/to/metadata.txt",
                file_type="documents",
                file_size=512,
                content_type="text/plain",
                metadata={"tags": ["custom_tag1", "custom_tag2"]}
            )
            
            # Salvar no banco para obter ID
            db.session.add(file_obj)
            db.session.commit()
            
            # Testar geração de tags
            tags = generate_tags_for_file(file_obj)
            
            # Verificar tags dos metadados
            self.assertIn("custom_tag1", tags)
            self.assertIn("custom_tag2", tags)


if __name__ == '__main__':
    unittest.main()