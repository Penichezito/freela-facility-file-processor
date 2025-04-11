import os
import logging
from typing import List, Dict, Any, Optional
from flask import current_app

from google.cloud import vision
import io

logger = logging.getLogger(__name__)

def analyze_images(image_path: str) -> List[str]:
    """
    Analisa uma imagem usando o Google Cloud Vision API para identificar 
    objetos, cenas, texto e gerar tags relevantes.
    
    Args:
        image_path: Caminho para o arquivo de imagem
    
    Returns:
        Lista de tags (strings) identificadas na imagem
    """
    # Verificar se o arquivo existe
    if not os.path.exists(image_path):
        logger.error(f"Image file not found: {image_path}")
        return ["images"]
    
    # Verificar se as credenciais do Google Cloud estão configuradas
    if not current_app.config.get("GOOGLE_APPLICATION_CREDENTIALS"):
        logger.warning("Credenciais do Google Cloud não estão configuradas. Usando uma tag de imagem básica.")
        return ["images"]
    
    try:
            # Inicializar o cliente Vision
            client = vision.ImageAnnotatorClient()
            
            # Carregar a imagem
            with io.open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            
            # Detectar características na imagem
            features = [
                {'type_': vision.Feature.Type.LABEL_DETECTION, 'max_results': 5},
                {'type_': vision.Feature.Type.OBJECT_LOCALIZATION, 'max_results': 5},
            ]
            
            request = vision.AnnotateImageRequest(
                image=image,
                features=features,
            )
            
            response = client.annotate_image(request=request)
            
            # Extrair as tags dos rótulos
            tags = []
            
            # Adicionar rótulos de objetos
            for label in response.label_annotations:
                tags.append(label.description.lower())
            
            # Adicionar objetos localizados
            for obj in response.localized_object_annotations:
                tags.append(obj.name.lower())
            
            # Retornar tags únicas
            return list(set(tags))
        
    except Exception as e:
        current_app.logger.error(f"Error analyzing image: {str(e)}")
        # Em caso de erro, retornar uma tag básica
        return ['images']