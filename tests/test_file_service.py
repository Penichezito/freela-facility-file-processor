import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from app import create_app
from app.config import Config
from app.db.database import db
from app.db.models.file import File
from app.services.file_service import get_file_type, save_file, delete_file, detect_mime_type


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    UPLOAD_FOLDER = tempfile.mkdtemp()
    AUTO_TAG_ENABLED = False


class FileServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        
        # Criar diretório temporário para testes
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
        # Limpar os arquivos de teste
        for root, dirs, files in os.walk(self.test_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.test_dir)

    def test_get_file_type(self):
        # Testar tipos de arquivo baseados na extensão
        self.assertEqual(get_file_type('image.jpg'), 'images')
        self.assertEqual(get_file_type('document.pdf'), 'documents')
        self.assertEqual(get_file_type('spreadsheet.xlsx'), 'spreadsheets')
        self.assertEqual(get_file_type('code.py'), 'code')
        self.assertEqual(get_file_type('archive.zip'), 'archives')
        
        # Testar tipos de arquivo baseados no content-type
        self.assertEqual(get_file_type('file', 'image/jpeg'), 'images')
        self.assertEqual(get_file_type('file', 'application/pdf'), 'documents')
        self.assertEqual(get_file_type('file', 'text/plain'), 'documents')
        
        # Testar arquivo desconhecido
        self.assertEqual(get_file_type('unknown.xyz'), 'outros')

    @patch('app.services.file_service.magic.Magic')
    def test_detect_mime_type(self, mock_magic):
        # Configurar o mock
        magic_instance = MagicMock()
        magic_instance.from_file.return_value = 'image/jpeg'
        mock_magic.return_value = magic_instance
        
        # Testar a detecção do tipo MIME
        mime_type = detect_mime_type('test_file.jpg')
        self.assertEqual(mime_type, 'image/jpeg')
        
        # Verificar se o mock foi chamado corretamente
        mock_magic.assert_called_once_with(mime=True)
        magic_instance.from_file.assert_called_once_with('test_file.jpg')
        
        # Testar exceção
        magic_instance.from_file.side_effect = Exception("Error")
        mime_type = detect_mime_type('test_file.jpg')
        self.assertEqual(mime_type, 'application/octet-stream')

    def test_save_and_delete_file(self):
        # Criar um arquivo temporário para teste
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(b'Test content')
        temp_file.close()
        
        with self.app.test_request_context():
            # Simular um objeto de arquivo do Flask
            class MockFileStorage:
                def __init__(self, path):
                    self.path = path
                    
                def save(self, dst):
                    with open(self.path, 'rb') as src:
                        with open(dst, 'wb') as dst_file:
                            dst_file.write(src.read())
            
            mock_file = MockFileStorage(temp_file.name)
            
            # Testar salvar arquivo
            with patch('app.services.file_service.os.path.join', return_value=os.path.join(self.test_dir, 'saved_file.txt')):
                file_path = save_file(mock_file, 'saved_file.txt')
                self.assertTrue(os.path.exists(file_path))
                
                # Testar conteúdo do arquivo
                with open(file_path, 'rb') as f:
                    content = f.read()
                    self.assertEqual(content, b'Test content')
                
                # Testar deletar arquivo
                result = delete_file(file_path)
                self.assertTrue(result)
                self.assertFalse(os.path.exists(file_path))
                
                # Testar deletar arquivo inexistente
                result = delete_file('nonexistent_file.txt')
                self.assertFalse(result)
        
        # Limpar o arquivo temporário
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)


if __name__ == '__main__':
    unittest.main()