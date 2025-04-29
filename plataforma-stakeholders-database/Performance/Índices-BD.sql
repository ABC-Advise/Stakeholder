CREATE UNIQUE INDEX idx_unique_advogado_cpf ON plataforma_stakeholders.advogado ( cpf );

CREATE INDEX idx_oab_trgm ON plataforma_stakeholders.advogado  ( oab );

CREATE INDEX idx_firstname_trgm ON plataforma_stakeholders.advogado  ( firstname );

CREATE INDEX idx_lastname_trgm ON plataforma_stakeholders.advogado  ( lastname );

CREATE UNIQUE INDEX idx_unique_advogado_oab ON plataforma_stakeholders.advogado ( oab );

CREATE INDEX idx_escritorio_cnpj_trgm ON plataforma_stakeholders.escritorio  ( cnpj );

CREATE UNIQUE INDEX idx_unique_escritorio_cnpj ON plataforma_stakeholders.escritorio ( cnpj );

CREATE INDEX idx_razao_social_trgm ON plataforma_stakeholders.escritorio  ( razao_social );

CREATE INDEX idx_nome_fantasia_trgm ON plataforma_stakeholders.escritorio  ( nome_fantasia );

CREATE UNIQUE INDEX unq_segmento_empresa ON plataforma_stakeholders.segmento_empresa ( cnae );

CREATE INDEX idx_descricao_cnae_trgm ON plataforma_stakeholders.segmento_empresa  ( descricao );

CREATE INDEX idx_tipo_relacao ON plataforma_stakeholders.tipo_relacao  ( descricao );

CREATE INDEX idx_tipo_relacao_0 ON plataforma_stakeholders.tipo_relacao  ( descricao_inversa );

CREATE INDEX idx_cnpj_trgm ON plataforma_stakeholders.empresa  ( cnpj );

CREATE INDEX idx_nome_fantasia_empresa_trgm ON plataforma_stakeholders.empresa  ( nome_fantasia );

CREATE INDEX idx_razao_social_empresa_trgm ON plataforma_stakeholders.empresa  ( razao_social );

CREATE INDEX idx_cidade_enderecos ON plataforma_stakeholders.enderecos  ( cidade );

CREATE INDEX idx_lastname_pessoa_trgm ON plataforma_stakeholders.pessoa  ( lastname );

CREATE UNIQUE INDEX idx_unique_pessoa_cpf ON plataforma_stakeholders.pessoa ( cpf );

CREATE INDEX idx_firstname_pessoa_trgm ON plataforma_stakeholders.pessoa  ( firstname );

CREATE INDEX idx_cpf_trgm ON plataforma_stakeholders.pessoa  ( cpf );

CREATE INDEX idx_relacionamentos ON plataforma_stakeholders.relacionamentos  ( tipo_relacao_id );