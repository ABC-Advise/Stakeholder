-- Cria o usuário com a senha especificada
CREATE USER api_service_user WITH PASSWORD 'admin123';

-- Concede permissão para o usuário conectar ao banco de dados
GRANT CONNECT ON DATABASE "example" TO api_service_user;

-- Concede permissão para usar o esquema 'plataforma_stakeholders'
GRANT USAGE ON SCHEMA plataforma_stakeholders TO api_service_user;

-- Concede permissão para usar e selecionar todas as sequências existentes no esquema
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA plataforma_stakeholders TO api_service_user;

-- Concede permissões para selecionar, inserir, atualizar e deletar todas as tabelas existentes no esquema
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA plataforma_stakeholders TO api_service_user;

-- Concede permissão para executar todas as funções existentes no esquema
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA plataforma_stakeholders TO api_service_user;

-- Define o search_path padrão para o esquema 'plataforma_stakeholders' ao se conectar como o usuário
ALTER USER api_service_user SET search_path TO plataforma_stakeholders;
