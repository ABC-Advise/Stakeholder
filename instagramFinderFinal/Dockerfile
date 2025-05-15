# Imagem base
FROM python:3.11-slim-bookworm

# Define o diretório de trabalho
WORKDIR /app

# Instala as dependências do sistema e atualiza os pacotes
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Cria um usuário não-root
RUN useradd -m -u 1000 appuser

# Copia os arquivos de requisitos
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir safety

# Verifica vulnerabilidades nas dependências
RUN safety check

# Copia o código da aplicação
COPY --chown=appuser:appuser . .

# Cria os diretórios necessários
RUN mkdir -p logs cache_busca && \
    chown -R appuser:appuser logs cache_busca && \
    chmod -R 755 logs cache_busca

# Define variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    PYTHONPATH=/app \
    PATH="/home/appuser/.local/bin:${PATH}"

# Muda para o usuário não-root
USER appuser

# Expõe a porta da aplicação
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"] 