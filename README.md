# Freela Facility - API de Processamento de Arquivos

API especializada no processamento, categorização e armazenamento de arquivos para o sistema Freela Facility.

## Tecnologias Utilizadas

- **Flask**: Framework web para Python
- **SQLAlchemy**: ORM para interação com banco de dados
- **PostgreSQL**: Banco de dados relacional
- **Google Cloud Vision API**: Para análise e classificação automática de imagens
- **Docker**: Containerização da aplicação

## Estrutura do Projeto

```
freela-facility-file-processor/
├── app/
│   ├── __init__.py
│   ├── main.py              # Ponto de entrada da aplicação
│   ├── config.py            # Configurações da aplicação
│   ├── core/                # Núcleo da aplicação
│   ├── db/                  # Modelos e conexão com banco de dados
│   │   ├── database.py
│   │   └── models/          # Modelos SQLAlchemy
│   ├── api/                 # Rotas da API
│   │   ├── routes/          # Rotas por recurso
│   │   └── schemas/         # Esquemas de dados
│   ├── services/            # Lógica de negócios
│   └── utils/               # Utilitários
├── tests/                   # Testes
├── Dockerfile               # Configuração do Docker
└── requirements.txt         # Dependências do projeto
```

## Funcionalidades Principais

- **Processamento de Arquivos**: Recebe arquivos, processa e armazena
- **Categorização Automática**: Identifica o tipo de arquivo e gera categorias
- **Geração de Tags**: Utiliza IA para analisar o conteúdo e gerar tags relevantes
- **Armazenamento Eficiente**: Sistema organizado de armazenamento de arquivos
- **API RESTful**: Interface para interação com outros serviços

## Endpoints da API

### Arquivos

- `POST /api/files/upload` - Upload de arquivo com processamento e categorização
- `GET /api/files/` - Listar arquivos (com filtros por tags, tipos, etc.)
- `GET /api/files/{file_id}` - Obter detalhes de um arquivo específico
- `GET /api/files/{file_id}/download` - Download de um arquivo
- `DELETE /api/files/{file_id}` - Excluir um arquivo
- `POST /api/files/{file_id}/tags` - Adicionar tags a um arquivo
- `DELETE /api/files/{file_id}/tags/{tag_name}` - Remover tag de um arquivo

### Tags

- `GET /api/tags/` - Listar todas as tags
- `POST /api/tags/` - Criar nova tag
- `GET /api/tags/{tag_id}` - Obter detalhes de uma tag
- `PUT /api/tags/{tag_id}` - Atualizar uma tag
- `DELETE /api/tags/{tag_id}` - Excluir uma tag
- `GET /api/tags/files/{tag_id}` - Listar arquivos com uma tag específica

## Integração com Google Cloud Vision API

Esta API utiliza o Google Cloud Vision API para análise de imagens e geração automática de tags. Recursos utilizados:

- Detecção de objetos e cenas
- Reconhecimento de textos em imagens
- Classificação de conteúdo
- Detecção de cores predominantes

## Instalação e Execução

### Com Docker

```bash
# Construir a imagem
docker build -t freela-facility-file-processor .

# Executar o container
docker run -p 5000:5000 --env-file .env freela-facility-file-processor
```

### Desenvolvimento Local

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/freela-facility-file-processor.git
   cd freela-facility-file-processor
   ```

2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure as variáveis de ambiente:
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas configurações
   ```

5. Execute a aplicação:
   ```bash
   python app/main.py
   ```

## Configuração do Google Cloud Vision API

Para utilizar a funcionalidade de análise de imagens, você precisa configurar as credenciais do Google Cloud Vision API:

1. Crie uma conta de serviço no [Google Cloud Console](https://console.cloud.google.com/)
2. Ative a Vision API para seu projeto
3. Faça download das credenciais JSON
4. Configure o caminho para o arquivo de credenciais na variável de ambiente `GOOGLE_APPLICATION_CREDENTIALS`

## Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `DATABASE_URL` | URL de conexão com o banco de dados | `sqlite:///app.db` |
| `STORAGE_PATH` | Caminho para armazenamento de arquivos | `./storage` |
| `GOOGLE_APPLICATION_CREDENTIALS` | Caminho para o arquivo de credenciais do Google Cloud | - |
| `MAX_CONTENT_LENGTH` | Tamanho máximo de upload (bytes) | `104857600` (100MB) |
| `AUTO_TAG_ENABLED` | Ativar/desativar geração automática de tags | `True` |

## Formatos de Arquivo Suportados

- **Imagens**: png, jpg, jpeg, gif, bmp, webp, svg, tiff
- **Documentos**: pdf, doc, docx, xls, xlsx, ppt, pptx, txt, rtf, csv, md
- **Código**: py, js, html, css, java, cpp, c, cs, go, rb, php, swift, ts, json, xml
- **Áudio**: mp3, wav, ogg, flac, m4a
- **Vídeo**: mp4, avi, mov, wmv, mkv, webm
- **Arquivos**: zip, rar, tar, gz, 7z