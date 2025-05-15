# Instagram Profile Finder API

API para busca e validação de perfis do Instagram.

## 🚀 Tecnologias

- Python 3.9+
- FastAPI
- PostgreSQL
- Redis
- Docker
- Railway (Deploy)

## 📋 Pré-requisitos

- Python 3.9 ou superior
- PostgreSQL
- Redis
- Docker (opcional)

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/instagram-finder.git
cd instagram-finder
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows
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

## 🏃‍♂️ Executando localmente

1. Inicie o servidor de desenvolvimento:
```bash
uvicorn src.main:app --reload
```

2. Acesse a documentação da API:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🐳 Executando com Docker

1. Construa a imagem:
```bash
docker build -t instagram-finder .
```

2. Execute o container:
```bash
docker run -p 8000:8000 instagram-finder
```

## 🚀 Deploy no Railway

1. Crie uma conta no [Railway](https://railway.app/)

2. Crie um novo projeto e conecte com seu repositório GitHub

3. Configure as variáveis de ambiente no Railway:
   - DATABASE_URL
   - REDIS_URL
   - SECRET_KEY
   - JWT_SECRET_KEY
   - BACKEND_CORS_ORIGINS
   - ENVIRONMENT=production
   - Outras variáveis necessárias

4. Adicione um banco de dados PostgreSQL no Railway

5. Faça o deploy

## 📝 Variáveis de Ambiente

Veja o arquivo `.env.example` para todas as variáveis necessárias.

## 🧪 Testes

Execute os testes:
```bash
pytest
```

## 📚 Documentação

A documentação completa da API está disponível em:
- Swagger UI: `/docs`
- ReDoc: `/redoc`

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## Estrutura do Projeto

```
src/
├── controllers/     # Controladores da API
├── services/        # Lógica de negócio
├── repositories/    # Comunicação com APIs e banco de dados
├── config/         # Configurações
├── utils/          # Funções utilitárias
├── tasks/          # Tarefas do projeto
└── docs/           # Documentação
```

## Documentação da API

A documentação completa da API está disponível em `src/docs/api_documentation.md`.

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request 