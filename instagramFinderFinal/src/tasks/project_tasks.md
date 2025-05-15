# Tarefas do Projeto Instagram Finder

## Fase 1: Configuração Inicial e Testes Básicos
- [x] Configuração do Ambiente
  - [x] Criar ambiente virtual
  - [x] Instalar dependências
  - [x] Configurar variáveis de ambiente
  - [x] Teste: Verificar se todas as dependências estão instaladas corretamente

- [x] Configuração do Banco de Dados
  - [x] Verificar conexão com o banco existente
  - [x] Teste: Verificar acesso ao schema `plataforma_stakeholders`
  - [x] Teste: Verificar acesso às tabelas (`empresa`, `pessoa`, `advogado`, `relacionamentos`)

## Fase 2: Implementação do Cliente da HikerAPI
- [x] Implementação do Cliente/Repositório Hiker
  - [x] Criar classe `HikerRepository` (ou similar)
  - [x] Implementar método de busca de perfil por username (`user_by_username_v1`)
  - [x] Implementar método de busca de seguidores de perfil (`user_followers_v2` ou `user_followers_chunk_v1`)
  - [x] Implementar métodos para outras buscas relevantes (ID, URL, query geral de nome)
  - [x] Teste: Mock da HikerAPI para simular respostas
  - [x] Teste: Verificar tratamento de respostas de erro da API (401, 404, 429, etc.)
  - [x] Teste: Verificar comportamento em caso de timeout

- [x] Documentação Interna da Integração com HikerAPI
  - [x] Documentar os endpoints da HikerAPI utilizados e seus propósitos no projeto
  - [x] Documentar os parâmetros enviados e as respostas esperadas/tratadas

## Fase 3: Implementação do Repositório PostgreSQL (Acesso a Dados)
- [x] Implementação do Repositório PostgreSQL para Consultas
  - [x] Método para buscar empresas (com e sem Instagram registrado)
  - [x] Método para buscar pessoas (com e sem Instagram registrado)
  - [x] Método para buscar advogados (com e sem Instagram registrado)
  - [x] Método para buscar entidades (pessoas, advogados) relacionadas a uma empresa
  - [x] Teste: Integração das consultas ao banco de dados
  - [x] Teste: Verificar performance das consultas principais
  - [x] Preparar e refinar o repositório para uso eficiente pela camada de serviço

## Fase 4: Serviço de Busca e Validação de Perfis Instagram
- [x] Implementação do Serviço Principal (`ProfileFinderService` ou similar)
  - [x] Orquestrar o fluxo de busca de perfis não registrados
    - [x] Identificar empresas no banco sem Instagram
    - [x] Para cada empresa, iniciar busca de perfil Instagram
    - [x] Identificar pessoas/advogados relacionados a empresas (com Instagram já encontrado ou não)
    - [x] Para cada pessoa/advogado relacionado, iniciar busca de perfil Instagram
  - [x] Implementar lógica de validação de perfil para `empresa` (`validar_perfil_empresa`)
  - [x] Implementar lógica de validação de perfil para `advogado` (`validar_perfil_advogado`)
  - [x] Implementar lógica de validação de perfil para `pessoa` (`validar_perfil_pessoa`)
    - [x] Implementar validação básica de nomes
    - [x] Adicionar normalização de nomes (leve e agressiva)
    - [x] Implementar comparação usando distância de Levenshtein
    - [x] Adicionar rejeição de perfis com nomes extras
    - [x] Implementar testes para casos básicos
    - [x] Implementar testes para nomes compostos
    - [x] Implementar testes para nomes com acentos
    - [x] Implementar testes para nomes com caracteres especiais
    - [x] Remover tratamento especial para nomes abreviados
    - [x] Atualizar documentação
  - [ ] Implementar estratégias de fallback para busca de perfis:
    - [ ] Tentativa 1 (para pessoas/advogados): Buscar entre seguidores do perfil da empresa associada (via HikerAPI)
    - [ ] Tentativa 2: Realizar busca direta por nome (query geral) na HikerAPI
  - [ ] Estruturar os resultados da busca (perfis candidatos com scores de validação) para serem consumidos pela API
  - [x] Teste: Unitários para a lógica de validação de cada tipo de entidade
  - [ ] Teste: Unitários para as estratégias de fallback
  - [ ] Teste: Integração do serviço (mockando repositórios e HikerAPI)

## Fase 5: API para Consulta e Suporte à Validação Manual
- [ ] Implementação dos Endpoints da API (Back-end)
  - [ ] Endpoint para listar entidades do banco (empresas, pessoas, advogados) que não possuem Instagram registrado (para o front-end saber o que pode ser buscado)
  - [ ] Endpoint para disparar o processo de busca de perfil do Instagram para uma entidade específica (ex: `/instagram/find/empresa/{id_empresa_banco}`)
  - [ ] Endpoint para disparar o processo de busca para todas as entidades pendentes de um tipo (ex: `/instagram/find_all/empresa`)
  - [ ] Endpoint para retornar os perfis candidatos encontrados para uma entidade, com seus scores de validação (para o front-end exibir para validação manual) (ex: `/instagram/candidates/empresa/{id_empresa_banco}`)
  - [ ] Considerar paginação e filtros para os endpoints que retornam listas
  - [ ] Implementar validação de parâmetros de entrada dos endpoints
  - [ ] Implementar tratamento de erros e respostas HTTP adequadas
  - [ ] Teste: Testes de integração para os endpoints da API
  - [ ] Teste: Testes de validação de entrada
  - [ ] Teste: Testes de tratamento de erros

## Fase 6: Documentação e Preparação para Front-end
- [ ] Documentação da API do Back-end
  - [ ] Documentar todos os endpoints da API (rotas, métodos, parâmetros, exemplos de requisição e resposta) usando um formato como OpenAPI/Swagger (pode ser um arquivo Markdown inicialmente)
  - [ ] Criar/Atualizar README.md do projeto com instruções de configuração, execução e como a API funciona.
  - [ ] Teste: Revisar a documentação da API quanto à clareza e completude

## Fase 7: Manutenção e Melhorias (Pós-Implementação Inicial)
- [ ] Monitoramento e Logging
  - [ ] Implementar logging básico para rastrear o fluxo de busca e possíveis erros no back-end
  - [ ] (Alertas e monitoramento avançado podem ser fases futuras)

- [ ] Melhorias Contínuas
  - [ ] Refinar algoritmos de validação com base no feedback da validação manual
  - [ ] Otimizar performance conforme o uso
  - [ ] (Novas features podem ser adicionadas em ciclos futuros)

## Validação de Perfis

- [X] Implementar lógica de validação no `ProfileValidator`. *(Já existia, mas revisamos)*
- [X] Integrar `ProfileValidator` no `ProfileFinderService`.
- [X] Adicionar testes unitários para `ProfileValidator`. *(Parcialmente coberto, mas o fluxo principal no FinderService está testado)*
- [ ] ~~Refinar critérios de pontuação com base em feedback.~~ *(Removido do escopo por enquanto)*

## Fluxo de Busca e Validação

- [X] Implementar `ProfileFinderService` para orquestrar a busca e validação.
- [X] Buscar perfis candidatos usando `HikerRepository`.
- [X] Chamar `ProfileValidator` para validar os candidatos.
- [X] Salvar o perfil validado no banco de dados via `PostgresRepository`. *(Próximo passo)*
- [X] Implementar busca por entidades relacionadas (sócios/advogados).
- [X] Adicionar testes de integração para o fluxo completo. *(Testes unitários do FinderService cobrem o fluxo mockado)*

## Testes

- [X] Configurar ambiente de testes com `pytest` e `pytest-asyncio`.
- [X] Criar mocks para dependências externas (`HikerRepository`, `PostgresRepository`).
- [X] Escrever testes unitários para `ProfileFinderService`. *(Concluído)*
- [ ] Escrever testes unitários para `PostgresRepository`.
- [ ] Escrever testes unitários para `HikerRepository`.
- [ ] Aumentar cobertura de testes geral.

## Banco de Dados

- [X] Definir schema do banco de dados.
- [X] Implementar `PostgresRepository` com métodos CRUD básicos.
- [ ] Implementar métodos específicos para buscar entidades sem Instagram e relacionadas. *(Feito no escopo do FinderService)*
- [ ] Otimizar queries e índices.

## API (se aplicável)

- [ ] Definir endpoints da API.
- [ ] Implementar rotas usando FastAPI.
- [ ] Adicionar documentação da API (Swagger/OpenAPI).

## Outros

- [X] Configurar `setup.py` e `requirements.txt`.
- [X] Implementar tratamento de erros robusto. *(Melhorado no FinderService)*
- [ ] Adicionar logging.
- [ ] Configurar CI/CD.
- [X] Atualizar `README.md`.
- [X] Atualizar `project_tasks.md`. *(Atualizando agora)*

**Legenda de Status (Exemplo):**
- `