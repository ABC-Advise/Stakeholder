# Registro de Aprendizado

## Correções e Otimizações

### 1. Estrutura do Projeto
- Implementada arquitetura em camadas (API, Serviço, Repositório)
- Separação clara de responsabilidades
- Uso de injeção de dependência para melhor testabilidade

### 2. Banco de Dados
- Utilização do SQLAlchemy para ORM
- Implementação de conexão pool para melhor performance
- Uso de transações para garantir consistência dos dados

### 3. API
- Implementação de endpoints RESTful
- Tratamento adequado de erros
- Documentação clara dos endpoints

### 4. Segurança
- Uso de variáveis de ambiente para credenciais
- Implementação de CORS
- Preparação para autenticação e autorização

### 5. Performance
- Implementação de cache (pendente)
- Otimização de queries
- Uso de conexões assíncronas

### 6. Banco de Dados - Correção de Nomes
- Corrigidos os nomes das tabelas principais para refletir o banco real: `empresa`, `pessoa`, `advogado`, `relacionamentos`
- Confirmado o uso do schema `plataforma_stakeholders` em todas as queries e testes

### 7. Integração com HikerAPI (Client Python)
- Corrigido o uso do parâmetro de inicialização do AsyncClient: de `api_key` para `token`.
- Atualizados todos os testes para uso do client assíncrono e mocks adequados.
- Testes assíncronos validados com pytest-asyncio, garantindo integração correta com a HikerAPI.

## Lições Aprendidas

1. **Arquitetura**
   - A separação em camadas facilita a manutenção e testabilidade
   - O uso de interfaces bem definidas permite trocar implementações facilmente

2. **Banco de Dados**
   - O uso de ORM facilita a manutenção do código
   - É importante implementar índices adequados para melhor performance

3. **API**
   - Documentação clara é essencial
   - Tratamento de erros deve ser consistente
   - Validação de dados é crucial

4. **Segurança**
   - Nunca expor credenciais no código
   - Implementar rate limiting para proteger a API
   - Usar HTTPS em produção

5. **Performance**
   - Implementar cache para reduzir chamadas à API externa
   - Otimizar queries do banco de dados
   - Usar conexões assíncronas quando possível

## Próximos Passos

1. Implementar testes automatizados
2. Adicionar monitoramento
3. Implementar sistema de cache
4. Melhorar documentação
5. Adicionar mais funcionalidades

# Documentação de Aprendizado

## Estrutura do Banco de Dados

### Visão Geral
O projeto utiliza um banco de dados PostgreSQL para armazenar e gerenciar informações sobre empresas, pessoas, advogados e seus relacionamentos. O banco está organizado em um schema chamado `plataforma_stakeholders`.

### Principais Tabelas

#### 1. Tabela `empresa`
Armazena informações sobre empresas.

**Principais campos:**
- `empresa_id`: Identificador único da empresa
- `nome`: Nome da empresa
- `instagram`: Nome de usuário do Instagram da empresa
- `segmento_id`: Relacionamento com a tabela de segmentos

#### 2. Tabela `pessoa`
Armazena informações sobre pessoas físicas.

**Principais campos:**
- `pessoa_id`: Identificador único da pessoa
- `firstname`: Primeiro nome
- `lastname`: Sobrenome
- `instagram`: Nome de usuário do Instagram da pessoa

#### 3. Tabela `advogado`
Armazena informações específicas sobre advogados.

**Principais campos:**
- `advogado_id`: Identificador único do advogado
- `firstname`: Primeiro nome
- `lastname`: Sobrenome
- `instagram`: Nome de usuário do Instagram do advogado

#### 4. Tabela `relacionamento_entidades`
Gerencia os relacionamentos entre as diferentes entidades.
- Armazena as conexões entre empresas, pessoas e advogados
- Permite rastrear quem está relacionado a quem

### Relacionamentos
- Empresas podem ter relacionamentos com pessoas e advogados
- Pessoas podem ter relacionamentos com empresas e advogados
- Advogados podem ter relacionamentos com empresas e pessoas

### Queries Comuns
```sql
-- Buscar empresa por ID
SELECT * FROM plataforma_stakeholders.empresa WHERE empresa_id = :id;

-- Buscar pessoa por ID
SELECT * FROM plataforma_stakeholders.pessoa WHERE pessoa_id = :id;

-- Buscar advogado por ID
SELECT * FROM plataforma_stakeholders.advogado WHERE advogado_id = :id;

-- Buscar relacionamentos de uma entidade
SELECT * FROM plataforma_stakeholders.relacionamento_entidades 
WHERE entidade_origem_id = :id AND tipo_entidade_origem = :tipo;
```

### Considerações Importantes
1. Todas as tabelas estão no schema `plataforma_stakeholders`
2. Os campos `instagram` são usados para buscar informações via API Hiker
3. Os relacionamentos são bidirecionais e podem ser consultados em ambas as direções
4. É importante manter a consistência dos dados ao atualizar informações do Instagram 