# Instagram Finder

Este projeto é uma aplicação Python para busca de perfis no Instagram utilizando a Hiker API.

## Requisitos

- Python 3.8+
- PostgreSQL
- Chave de API da Hiker

## Instalação

1. Clone o repositório:
```bash
git clone [url-do-repositorio]
cd instagram-finder
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure o arquivo .env:
- Copie o arquivo `.env.example` para `.env`
- Preencha as variáveis de ambiente com suas credenciais

5. Configure o banco de dados:
```bash
python src/config/database.py
```

## Executando a aplicação

Para iniciar o servidor de desenvolvimento:
```bash
uvicorn src.main:app --reload
```

## Testes

Para executar os testes:
```bash
pytest
```

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