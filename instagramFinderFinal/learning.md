# Lições Aprendidas

## Correções e Ajustes

### Nomes de Tabelas e Schema
- Corrigido nome da tabela de `stakeholders` para `stakeholder`
- Adicionado schema `plataforma_stakeholders` nas queries
- Ajustado nome da coluna de `stakeholder_id` para `id`

### Conversão de Resultados SQL para Dicionários
- Ao usar SQLAlchemy com `text()`, os resultados retornados por `fetchone()` e `fetchall()` são objetos Row
- Para converter corretamente para dicionário, usar `dict(result._mapping)` ao invés de `dict(result)`
- Isso é necessário porque o objeto Row não é diretamente convertível para dict
- Exemplo de uso correto:
  ```python
  result = session.execute(query, params).fetchone()
  return dict(result._mapping) if result else None
  ```
- Para listas de resultados:
  ```python
  results = session.execute(query, params).fetchall()
  return [dict(row._mapping) for row in results]
  ```

## Integração com HikerAPI

### Client Python
- Usar AsyncClient para requisições assíncronas
- Exemplo de uso:
  ```python
  from hikerapi import AsyncClient
  
  client = AsyncClient(api_key="sua_chave")
  profile = await client.get_profile(username="exemplo")
  ```

### Endpoints Disponíveis
1. Busca por username
   - Endpoint: `/profile/username/{username}`
   - Método: GET
   - Exemplo de resposta:
   ```json
   {
     "id": "123456789",
     "username": "exemplo",
     "full_name": "Nome Completo",
     "followers_count": 1000,
     "following_count": 500,
     "bio": "Descrição do perfil"
   }
   ```

2. Busca por ID
   - Endpoint: `/profile/id/{id}`
   - Método: GET
   - Mesma estrutura de resposta da busca por username

3. Busca por URL
   - Endpoint: `/profile/url`
   - Método: POST
   - Body: `{"url": "https://instagram.com/exemplo"}`
   - Mesma estrutura de resposta

4. Busca por nome (query)
   - Endpoint: `/profile/query`
   - Método: POST
   - Body: `{"query": "nome para buscar"}`
   - Retorna lista de perfis que correspondem à query

5. Web Profile Info
   - Endpoint: `/profile/web/{username}`
   - Método: GET
   - Retorna informações públicas do perfil

### Boas Práticas
1. Sempre usar try/except para tratar erros da API
2. Implementar rate limiting para evitar bloqueios
3. Cache de resultados para otimizar performance
4. Validação de dados antes de salvar no banco
5. Logs detalhados para debug

## Banco de Dados

### Estrutura
- Schema: `plataforma_stakeholders`
- Tabelas:
  - `empresa`
  - `pessoa`
  - `advogado`

### Queries
- Usar ILIKE para buscas case-insensitive
- Exemplo:
  ```sql
  SELECT * FROM plataforma_stakeholders.empresa
  WHERE nome_fantasia ILIKE :nome_fantasia
  ```

### Índices
- Criar índices para campos frequentemente usados em busca
- Exemplo:
  ```sql
  CREATE INDEX idx_empresa_nome_fantasia ON plataforma_stakeholders.empresa(nome_fantasia);
  ```

## Testes

### Unitários
- Usar pytest-asyncio para testes assíncronos
- Mock de dependências externas
- Exemplo:
  ```python
  @pytest.mark.asyncio
  async def test_buscar_perfil():
      # setup
      # act
      # assert
  ```

### Integração
- Testar conexão real com banco
- Usar banco de teste separado
- Limpar dados após cada teste

## Segurança

### API Keys
- Nunca commitar chaves no código
- Usar variáveis de ambiente
- Exemplo:
  ```python
  import os
  API_KEY = os.getenv("HIKER_API_KEY")
  ```

### Dados Sensíveis
- Não logar dados sensíveis
- Sanitizar inputs
- Validar outputs

## Performance

### Otimizações
1. Cache de resultados
2. Índices no banco
3. Paginação de resultados
4. Batch processing
5. Connection pooling

### Monitoramento
- Logs de performance
- Métricas de uso
- Alertas de erro

## Deploy

### Docker
- Multi-stage builds
- Otimização de layers
- Health checks

### CI/CD
- Testes automáticos
- Linting
- Type checking
- Security scanning

## Documentação

### API
- OpenAPI/Swagger
- Exemplos de uso
- Códigos de erro

### Código
- Docstrings
- Type hints
- README detalhado

## Próximos Passos

1. Implementar cache
2. Adicionar mais testes
3. Melhorar documentação
4. Otimizar queries
5. Implementar rate limiting

## [Lição Aprendida] Ajuste de escopo: atualização de Instagram removida

Durante o desenvolvimento, identificamos que o objetivo do projeto é apenas buscar e validar perfis do Instagram usando a HikerAPI, sem necessidade de persistir o username ou outros dados do Instagram no banco de dados.

Por isso, removemos todos os métodos e testes relacionados à atualização de Instagram nas entidades (empresa, pessoa, advogado). O repositório e os testes agora estão focados apenas em buscas e validação, alinhando o código ao escopo real do sistema.

**Vantagens:**
- Código mais limpo e objetivo
- Testes mais rápidos e relevantes
- Menos dependência de estrutura de banco

**Próximos passos:**
- Foco total na lógica de matching/validação de perfis
- Garantir integração robusta com a HikerAPI 

## [Lição Aprendida] Diferenciação da lógica de busca para empresa, pessoa e advogado

Durante o desenvolvimento, identificamos a necessidade de diferenciar a lógica de matching/validação de perfis conforme o tipo de entidade: empresa, pessoa e advogado. Cada tipo possui critérios e regras específicas para validação do perfil do Instagram.

- A lógica de matching para **empresa** já foi implementada e validada com sucesso.
- As lógicas para **pessoa** e **advogado** ainda precisam ser implementadas e testadas.

Essa diferenciação garante maior precisão e aderência ao contexto de cada entidade, tornando o sistema mais robusto e confiável.

## [Lição Aprendida] Refinamentos na Validação de Perfis de Advogado e Depuração

Durante a implementação e teste da função `validar_perfil_advogado`, passamos por um processo iterativo de depuração e refinamento lógico. As principais lições foram:

1.  **Impacto Crítico das Palavras Negativas (`negative_words.txt`):**
    *   A verificação de palavras negativas, especialmente quando implementada com correspondência de substring (`palavra_negativa_normalizada in bio_normalizada`), é um filtro poderoso, mas extremamente sensível.
    *   **Problema Encontrado:** Uma palavra negativa como `"consultor"` estava sendo encontrada como substring em `"consultoriajuridica"` (na bio normalizada), fazendo com que perfis válidos de advogados com "Consultoria Jurídica" na bio fossem descartados prematuramente.
    *   **Solução:** Remover termos ambíguos ou que podem fazer parte de descrições válidas (como "consultor", "consultora") da lista de palavras negativas. Isso exigiu uma análise cuidadosa do contexto de uso.
    *   **Aprendizado:** A lista de palavras negativas deve ser curada com extrema cautela, e a estratégia de correspondência (substring vs. palavra inteira) deve ser considerada. A ordem da verificação (substring vs. palavra inteira) a torna um ponto de falha determinante.

2.  **Importância da Normalização Consistente (`normalizar`):**
    *   Manter uma função de normalização robusta (converter para minúsculas, remover acentos, tratar pontuações e variações como "Jr." vs "Junior", remover caracteres não alfanuméricos) é fundamental. Isso garante que as comparações entre nomes da query, nomes de perfis e variações geradas sejam justas e eficazes.

3.  **Eficácia da Geração de Variações de Nome (`gerar_variacoes_nome`):**
    *   Uma função `gerar_variacoes_nome` abrangente é crucial para encontrar perfis que não usam o nome completo exato.
    *   **Ajustes Realizados:** A função foi aprimorada para incluir:
        *   Tratamento de sufixos como "Junior" e "jr." para gerar ambas as formas.
        *   Criação de variações com a inicial do primeiro nome seguida do restante (ex: "J. Carlos Ferreira" e "JCarlos Ferreira").
        *   Melhorias na geração de combinações de iniciais e partes do nome.
    *   **Aprendizado:** A complexidade dos nomes reais exige uma geração de variações pensada para cobrir os formatos mais comuns de abreviação e apresentação em redes sociais.

4.  **Estratégia de Pontuação Hierárquica e Contextual:**
    *   Atribuir pesos diferentes para diferentes tipos de correspondência de nome (ex: nome exato da query = 90 pts; variação completa no nome do perfil = 70 pts; variação no username = 50 pts; parte significativa do nome original = 45 pts) cria uma hierarquia de confiança.
    *   Combinar essa pontuação de nome com sinais de contexto (termos jurídicos na bio e/ou username) e um limiar de pontuação (`score >= 70`) permite uma validação mais nuançada.
    *   A condição final de validação foi ajustada para:
        *   Se nome exato (e sem palavras negativas): Válido se `score >= 70` (o que geralmente será o caso devido aos 90 pontos do nome).
        *   Senão (nome não exato): Válido apenas se `score >= 70` E o perfil contiver termos jurídicos.

5.  **Processo Iterativo de Teste e Depuração:**
    *   A validação de nomes é inerentemente complexa. Chegar a uma solução robusta exigiu:
        *   Criação de diversos casos de teste em `test_profile_validator_advogado.py` cobrindo nomes exatos, abreviações, nomes longos, presença/ausência de termos jurídicos e palavras negativas.
        *   Análise cuidadosa dos resultados dos testes.
        *   Ajustes incrementais na lógica de `validar_perfil_advogado` e `gerar_variacoes_nome`.
        *   Uso temporário de `print` statements para entender o fluxo de pontuação interno (embora a causa raiz do último problema tenha sido identificada por análise lógica da interação com `negative_words.txt`).
    *   **Aprendizado:** Testes unitários bem elaborados são indispensáveis, e a depuração de algoritmos de matching muitas vezes envolve um ciclo de hipótese, teste e refinamento. A alteração dos próprios dados de teste (como no caso `test_advogado_bloqueio_sobrenome_comum`) também pode ser necessária para refletir cenários mais realistas ou para isolar problemas.

## Lições Aprendidas e Evolução do Projeto

### Progresso Recente e Melhorias Chave
Nas últimas interações, focamos em refinar significativamente a lógica de validação de perfis, especialmente para empresas, e em fortalecer a suíte de testes para garantir robustez.

#### Aperfeiçoamento da Validação de Segmento para Empresas (`validar_segmento`)
- **Desafio Inicial:** A validação de segmento para empresas comparava uma porcentagem de "chunks" da descrição do segmento (normalizada de forma agressiva, removendo espaços) com a bio (também normalizada agressivamente). Isso resultava em um único "chunk" longo para a descrição, exigindo uma correspondência quase exata, o que era pouco flexível.
- **Evolução Implementada:** A lógica foi reestruturada para uma abordagem mais granular e eficaz:
    - **Normalização Leve da Descrição do Segmento:** A descrição original do segmento agora passa por uma normalização leve que converte para minúsculas, remove acentos e padroniza pontuações e múltiplos espaços para um único espaço, preservando as palavras individuais.
    - **Tokenização:** A descrição pré-processada é dividida em palavras (tokens).
    - **Remoção de Stopwords:** Uma lista de stopwords em português (`STOPWORDS_PT`) é usada para filtrar tokens irrelevantes da descrição do segmento.
    - **Normalização Final dos Tokens:** Cada token significativo restante é então normalizado individualmente usando a função `normalizar` original (que remove espaços internos e todos os caracteres não alfanuméricos). Tokens que se tornam vazios após esta etapa são descartados.
    - **Normalização da Bio:** A bio do perfil do Instagram continua sendo processada pela função `normalizar` completa.
    - **Critério de Validação:** A validação é considerada bem-sucedida se pelo menos um dos tokens finais normalizados da descrição do segmento for encontrado como uma substring na bio normalizada.
- **Benefício:** Esta nova abordagem permite uma correspondência mais flexível e realista, identificando a presença de termos-chave do segmento na bio, mesmo que não apareçam na mesma ordem ou com as mesmas palavras conectoras da descrição formal.

#### Fortalecimento dos Testes Unitários (`src/tests/test_profile_validator_empresa.py`)
- **Mocking de Dependências:** Os testes para `validar_segmento` foram refatorados para utilizar `unittest.mock.MagicMock` para simular as respostas do banco de dados (`session.execute`). Isso os torna independentes de um banco de dados real, mais rápidos e mais confiáveis.
- **Cobertura Ampliada:** Foram adicionados novos casos de teste para `validar_segmento`, cobrindo cenários como descrições de segmento vazias, bios vazias, descrições que contêm apenas stopwords (testando a lógica de fallback) e descrições com números.
- **Testes de `validar_perfil_empresa`:** Os mocks para `validar_segmento` e `validar_nome_empresa` foram mantidos e refinados nesses testes para isolar a lógica de pontuação e desempate, assegurando a correta avaliação dos bônus (`is_business`), penalidades, limiares e a seleção entre múltiplos perfis candidatos.
- **Clareza:** O arquivo de teste foi revisado para melhorar a legibilidade, embora a remoção completa de comentários via ferramenta tenha apresentado desafios.

### Como Funciona o Código de Validação de Empresas (`ProfileValidator`)
A validação de um perfil de Instagram para uma empresa (`validar_perfil_empresa`) segue a seguinte lógica de pontuação e decisão:
- **Iteração e Inicialização:** A função itera sobre cada perfil de Instagram fornecido para a empresa. Cada perfil inicia com um `score` de 0.
- **Pontuação do Nome (`full_name` - até 80 pontos):**
    - O `nome_fantasia` da empresa e o `full_name` do perfil são comparados usando `validar_nome_empresa`.
    - Esta função normaliza ambos os nomes, divide-os em partes e calcula um `score` de similaridade (0 a 1) baseado em correspondência exata de partes, verificação de substring e distância de Levenshtein. Penaliza grande diferença no número de palavras.
    - Se o `nome_score` resultante for 0 (nenhuma correspondência significativa), o perfil é desconsiderado para esta empresa.
    - Caso contrário, `nome_score * 80` é adicionado ao `score` total.
- **Pontuação da Bio (Segmento - 10 pontos):**
    - A bio do perfil é normalizada.
    - A função `validar_segmento` (com a lógica de tokenização e stopwords descrita acima) é chamada com o `segmento_id` da empresa e a bio normalizada.
    - Se `validar_segmento` retornar `True` (pelo menos um termo significativo da descrição do segmento encontrado na bio), 10 pontos são adicionados ao `score` total.
- **Pontuação do Username (até 10 pontos ou -5 pontos):**
    - O `nome_fantasia` da empresa e o `username` do perfil são comparados usando `validar_nome_empresa`.
    - Se o `username_score` for 0, uma penalidade de 5 pontos é aplicada (-5).
    - Caso contrário, `username_score * 10` é adicionado ao `score` total.
- **Bônus `is_business` (5 pontos):**
    - Se o campo `is_business` do perfil for `True`, um bônus fixo de 5 pontos é adicionado.
- **Cálculo do Score Total:** Os pontos de nome, bio, username e o bônus `is_business` são somados.
- **Validação e Seleção:**
    - Apenas perfis com `score_total >= 70` são considerados válidos.
    - Se houver perfis válidos, eles são armazenados com seus `scores` e um indicador `is_business_profile`.
    - O perfil retornado é aquele com o maior `score_total`.
    - **Desempate:** Se múltiplos perfis tiverem o mesmo `score_total` máximo, o perfil com `is_business_profile = True` terá preferência.

### Como Funciona o Código de Validação de Advogados (`ProfileValidator`)
*(Esta seção é baseada nas informações do seu `learning.md` e na sumarização anterior, pois não revisitamos este código em detalhes recentemente)*

A validação de um perfil de Instagram para um advogado (`validar_perfil_advogado`) utiliza uma estratégia de pontuação e filtros específicos:
- **Geração de Variações de Nome:**
    - A função `gerar_variacoes_nome` cria uma lista abrangente de variações do nome do advogado (primeiro nome, último nome), considerando:
        - Nome completo original.
        - Combinações de primeiro/último nome, nomes compostos.
        - Abreviações (ex: "J. Carlos", "JCarlos").
        - Sufixos (ex: "Junior", "Jr.", gerando ambas as formas).
        - Inversões ( Último + Primeiro), filtrando por sobrenomes comuns (`sobrenomes_comuns.txt`).
        - Iniciais (ex: "JCFJ").
- **Normalização:**
    - O nome completo original do advogado, as variações geradas, o `full_name` do perfil, o `username` e a bio passam pela função `normalizar` (minúsculas, tratamento de "jr."/"junior", remoção de acentos e não alfanuméricos).
- **Filtro por Palavras Negativas:**
    - Uma lista de palavras (`NEGATIVE_WORDS` de `negative_words.txt`) é verificada na `bio_norm` do perfil.
    - Se qualquer palavra negativa (normalizada) for encontrada como substring na `bio_norm`, o perfil é imediatamente descartado e não entra na pontuação.
- **Estrutura de Pontuação:**
    - **Nome (até 90 pontos):**
        - 90 pontos: Se o nome completo original do advogado (normalizado) corresponde exatamente ao `full_name` do perfil (normalizado).
        - 70 pontos: (Se não houver match exato) Se uma variação completa do nome (normalizada) é encontrada no `full_name` do perfil.
        - 50 pontos: (Se as anteriores falharem) Se uma variação completa (normalizada) é encontrada no `username` do perfil.
        - 45 pontos: (Se as anteriores falharem) Se partes significativas do nome original do advogado (normalizadas, incluindo iniciais e partes do nome) são encontradas no `full_name` do perfil.
    - **Bio (até +20 pontos):**
        - Uma lista `TERMS_JURIDICOS` (incluindo emojis relevantes) é usada.
        - +20 pontos: Se 2 ou mais termos jurídicos (palavras ou emojis) forem encontrados na bio (palavras são normalizadas para busca, emojis são buscados diretamente).
        - +10 pontos: Se 1 termo jurídico for encontrado.
    - **Username (até +10 pontos):**
        - +10 pontos: Se uma variação de nome (normalizada) E um termo jurídico (normalizado) estiverem presentes no `username` normalizado.
        - +5 pontos: Se uma variação de nome OU um termo jurídico estiver presente no `username`.
- **Condição Final de Validação:**
    - Um perfil é considerado válido se:
        - **Caso 1 (Match Exato do Nome):** O nome completo original do advogado corresponde exatamente ao `full_name` do perfil (e não há palavras negativas) E o `score_total >= 70`.
        - **Caso 2 (Outros Matches de Nome):** O nome não é um match exato, MAS o `score_total >= 70` E o perfil contém algum termo jurídico (na bio ou no `username`).
- **Seleção:** Retorna o perfil válido com o maior `score`. Se nenhum perfil for válido, retorna `None`. 

## Validação de Perfis de Pessoas

### Lógica de Validação
- O nome original vem do RG e é considerado a fonte de verdade
- Qualquer nome adicional no perfil do Instagram é rejeitado
- Não há tratamento especial para nomes abreviados
- A comparação é feita usando:
  - Normalização leve (com espaços) para tokenização
  - Normalização agressiva (sem espaços) para comparação
  - Distância de Levenshtein para similaridade

### Pontuação
- Score 100: Nome exatamente igual ao do RG
- Score >= 65: Nome similar (usando distância de Levenshtein)
- Score 0: Rejeitado quando:
  - Tem palavras extras que não estão no RG
  - Similaridade muito baixa

### Exemplos
- "João Silva" (RG) vs "João Silva" (Instagram) -> Score 100
- "João Silva" (RG) vs "João S. Silva" (Instagram) -> Rejeitado (palavra extra)
- "Juliano Silva de Castro" (RG) vs "Juliano de Castro" (Instagram) -> Score >= 65
- "Juliano Silva de Castro" (RG) vs "Juliano S. de Castro" (Instagram) -> Score >= 65

### Variações de Nome
- Nomes compostos são tratados como uma única unidade
- Acentos são removidos na comparação
- Caracteres especiais são removidos
- Espaços extras são normalizados

### Rejeição de Perfis
- Nomes vazios
- Nomes completamente diferentes
- Nomes com palavras extras
- Similaridade muito baixa (< 65) 

# Aprendizados e Ajustes - Busca de Seguidores Instagram (Hiker API)

## 1. Formato de Resposta da API
- A resposta do método `user_followers_chunk_v1` pode variar:
  - Pode retornar um dicionário com as chaves `users` (lista de seguidores) e `next_max_id` (para paginação).
  - Pode retornar uma lista aninhada: `[seguidores, next_max_id]`, onde o primeiro elemento é a lista de seguidores (cada um como dicionário) e o segundo é o cursor para a próxima página.

## 2. Tratamento Correto da Resposta
- O código deve identificar o tipo da resposta:
  - Se for lista aninhada, desempacotar corretamente os seguidores e o `next_max_id`.
  - Se for dicionário, acessar normalmente as chaves `users` e `next_max_id`.
- Isso garante que todos os seguidores de cada página sejam processados corretamente, evitando processar apenas 1 ou 2 por vez.

## 3. Paginação
- O parâmetro `max_id` deve ser omitido na primeira chamada (ou seja, só enviado se não for `None`).
- O loop de paginação deve ser controlado pelo valor de `next_max_id` retornado pela API.

## 4. Debug e Logs
- Adicionar prints temporários para inspecionar o tipo e o conteúdo da resposta ajuda a identificar rapidamente problemas de parsing.
- Mensagens de log claras facilitam o entendimento do fluxo e dos possíveis erros.

## 5. Robustez
- O código agora está preparado para lidar com diferentes formatos de resposta, tornando a integração mais robusta e menos sujeita a quebras caso a API varie o formato.

---

**Resumo:**
A principal lição foi garantir que o código trate corretamente diferentes formatos de resposta da API de seguidores, especialmente listas aninhadas, para garantir a correta paginação e processamento de todos os seguidores. Isso evita bugs de "busca de 2 em 2" e garante performance e precisão na busca de nomes entre seguidores. 