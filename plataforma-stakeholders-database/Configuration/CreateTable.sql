CREATE SCHEMA IF NOT EXISTS plataforma_stakeholders;

CREATE SEQUENCE plataforma_stakeholders.advogado_advogado_id_seq AS integer START WITH 1 INCREMENT BY 1;

CREATE SEQUENCE plataforma_stakeholders.consulta_consulta_id_seq START WITH 1 INCREMENT BY 1;

CREATE SEQUENCE plataforma_stakeholders.empresa_empresa_id_seq AS integer START WITH 1 INCREMENT BY 1;

CREATE SEQUENCE plataforma_stakeholders.escritorio_escritorio_id_seq AS integer START WITH 1 INCREMENT BY 1;

CREATE SEQUENCE plataforma_stakeholders.log_consulta_log_consulta_id_seq START WITH 1 INCREMENT BY 1;

CREATE SEQUENCE plataforma_stakeholders.pessoa_pessoa_id_seq AS integer START WITH 1 INCREMENT BY 1;

CREATE SEQUENCE plataforma_stakeholders.porte_empresa_porte_id_seq AS smallint START WITH 1 INCREMENT BY 1;

CREATE SEQUENCE plataforma_stakeholders.projeto_projeto_id_seq START WITH 1 INCREMENT BY 1;

CREATE SEQUENCE plataforma_stakeholders.segmento_empresa_segmento_id_seq AS smallint START WITH 1 INCREMENT BY 1;

CREATE SEQUENCE plataforma_stakeholders.tipo_entidade_tipo_entidade_id_seq AS smallint START WITH 1 INCREMENT BY 1;

CREATE SEQUENCE plataforma_stakeholders.tipo_log_tipo_log_id_seq AS integer START WITH 1 INCREMENT BY 1;

CREATE SEQUENCE plataforma_stakeholders.tipo_relacao_tipo_relacao_id_seq AS smallint START WITH 1 INCREMENT BY 1;

CREATE  TABLE plataforma_stakeholders.advogado ( 
	firstname            varchar(40)    ,
	lastname             varchar(80)    ,
	oab                  varchar(8)  NOT NULL  ,
	advogado_id          integer DEFAULT nextval('plataforma_stakeholders.advogado_advogado_id_seq'::regclass) NOT NULL  ,
	linkedin             varchar(20)    ,
	instagram            varchar(20)    ,
	cpf                  varchar(11)    ,
	stakeholder          boolean DEFAULT false   ,
	CONSTRAINT pk_advogado PRIMARY KEY ( advogado_id )
 );

CREATE UNIQUE INDEX idx_unique_advogado_cpf ON plataforma_stakeholders.advogado ( cpf );

CREATE INDEX idx_oab_trgm ON plataforma_stakeholders.advogado USING  gin ( oab  gin_trgm_ops );

CREATE INDEX idx_firstname_trgm ON plataforma_stakeholders.advogado USING  gin ( firstname  gin_trgm_ops );

CREATE INDEX idx_lastname_trgm ON plataforma_stakeholders.advogado USING  gin ( lastname  gin_trgm_ops );

CREATE UNIQUE INDEX idx_unique_advogado_oab ON plataforma_stakeholders.advogado ( oab );

CREATE  TABLE plataforma_stakeholders.consulta ( 
	consulta_id          integer DEFAULT nextval('plataforma_stakeholders.consulta_consulta_id_seq'::regclass) NOT NULL  ,
	documento            varchar(14)  NOT NULL  ,
	data_consulta        timestamptz DEFAULT CURRENT_TIMESTAMP   ,
	is_cnpj              boolean DEFAULT false NOT NULL  ,
	status               varchar DEFAULT 'Pendente'::character varying NOT NULL  ,
	CONSTRAINT pk_consulta PRIMARY KEY ( consulta_id )
 );

CREATE  TABLE plataforma_stakeholders.escritorio ( 
	razao_social         varchar(255)  NOT NULL  ,
	nome_fantasia        varchar(255)    ,
	escritorio_id        integer DEFAULT nextval('plataforma_stakeholders.escritorio_escritorio_id_seq'::regclass) NOT NULL  ,
	linkedin             varchar(20)    ,
	instagram            varchar(20)    ,
	cnpj                 varchar(14)  NOT NULL  ,
	CONSTRAINT pk_escritorio PRIMARY KEY ( escritorio_id )
 );

CREATE INDEX idx_escritorio_cnpj_trgm ON plataforma_stakeholders.escritorio USING  gin ( cnpj  gin_trgm_ops );

CREATE UNIQUE INDEX idx_unique_escritorio_cnpj ON plataforma_stakeholders.escritorio ( cnpj );

CREATE INDEX idx_razao_social_trgm ON plataforma_stakeholders.escritorio USING  gin ( razao_social  gin_trgm_ops );

CREATE INDEX idx_nome_fantasia_trgm ON plataforma_stakeholders.escritorio USING  gin ( nome_fantasia  gin_trgm_ops );

CREATE  TABLE plataforma_stakeholders.porte_empresa ( 
	porte_id             smallint DEFAULT nextval('plataforma_stakeholders.porte_empresa_porte_id_seq'::regclass) NOT NULL  ,
	descricao            varchar(40)  NOT NULL  ,
	CONSTRAINT pk_porte_empresa PRIMARY KEY ( porte_id )
 );

CREATE  TABLE plataforma_stakeholders.projeto ( 
	projeto_id           integer DEFAULT nextval('plataforma_stakeholders.projeto_projeto_id_seq'::regclass) NOT NULL  ,
	nome                 varchar(160)  NOT NULL  ,
	descricao            text    ,
	data_inicio          date    ,
	data_fim             date    ,
	CONSTRAINT pk_projeto PRIMARY KEY ( projeto_id )
 );

CREATE  TABLE plataforma_stakeholders.segmento_empresa ( 
	descricao            text  NOT NULL  ,
	cnae                 varchar(7)  NOT NULL  ,
	segmento_id          smallint DEFAULT nextval('plataforma_stakeholders.segmento_empresa_segmento_id_seq'::regclass) NOT NULL  ,
	CONSTRAINT pk_segmento_empresa PRIMARY KEY ( segmento_id )
 );

CREATE UNIQUE INDEX unq_segmento_empresa ON plataforma_stakeholders.segmento_empresa ( cnae );

CREATE INDEX idx_descricao_cnae_trgm ON plataforma_stakeholders.segmento_empresa USING  gin ( descricao  gin_trgm_ops );

CREATE  TABLE plataforma_stakeholders.tipo_entidade ( 
	descricao            varchar(40)  NOT NULL  ,
	tipo_entidade_id     smallint DEFAULT nextval('plataforma_stakeholders.tipo_entidade_tipo_entidade_id_seq'::regclass) NOT NULL  ,
	CONSTRAINT pk_tipo_entidade PRIMARY KEY ( tipo_entidade_id )
 );

CREATE  TABLE plataforma_stakeholders.tipo_log ( 
	nome                 varchar(40)  NOT NULL  ,
	tipo_log_id          integer DEFAULT nextval('plataforma_stakeholders.tipo_log_tipo_log_id_seq'::regclass) NOT NULL  ,
	CONSTRAINT pk_tipo_log PRIMARY KEY ( tipo_log_id )
 );

CREATE  TABLE plataforma_stakeholders.tipo_relacao ( 
	tipo_relacao_id      smallint DEFAULT nextval('plataforma_stakeholders.tipo_relacao_tipo_relacao_id_seq'::regclass) NOT NULL  ,
	descricao            varchar(20)  NOT NULL  ,
	descricao_inversa    varchar(20)    ,
	CONSTRAINT pk_tipo_relacao PRIMARY KEY ( tipo_relacao_id ),
	CONSTRAINT unq_tipo_relacao UNIQUE ( descricao, descricao_inversa ) 
 );

CREATE INDEX idx_tipo_relacao ON plataforma_stakeholders.tipo_relacao USING  btree ( descricao );

CREATE INDEX idx_tipo_relacao_0 ON plataforma_stakeholders.tipo_relacao USING  btree ( descricao_inversa );

CREATE  TABLE plataforma_stakeholders.email ( 
	email_id             smallint  NOT NULL  ,
	entidade_id          integer  NOT NULL  ,
	tipo_entidade_id     smallint  NOT NULL  ,
	email                varchar(180)  NOT NULL  ,
	CONSTRAINT pk_email PRIMARY KEY ( email_id, entidade_id, tipo_entidade_id )
 );

CREATE  TABLE plataforma_stakeholders.empresa ( 
	cnpj                 varchar(14)  NOT NULL  ,
	razao_social         varchar(255)  NOT NULL  ,
	nome_fantasia        varchar(255)    ,
	porte_id             integer    ,
	segmento_id          smallint    ,
	empresa_id           integer DEFAULT nextval('plataforma_stakeholders.empresa_empresa_id_seq'::regclass) NOT NULL  ,
	linkedin             varchar(20)    ,
	instagram            varchar(20)    ,
	stakeholder          boolean DEFAULT false NOT NULL  ,
	em_prospecao         boolean DEFAULT false NOT NULL  ,
	data_fundacao        varchar(20)    ,
	situacao_cadastral   text    ,
	quantidade_funcionarios integer    ,
	codigo_natureza_juridica integer    ,
	natureza_juridica_descricao text    ,
	faixa_funcionarios   varchar(125)    ,
	faixa_faturamento    varchar(150)    ,
	matriz               boolean    ,
	orgao_publico        varchar(150)    ,
	ramo                 varchar(150)    ,
	tipo_empresa         varchar(125)    ,
	ultima_atualizacao_pj varchar(20)    ,
	natureza_juridica_tipo varchar(150)    ,
	projeto_id           integer    ,
	CONSTRAINT pk_empresa PRIMARY KEY ( empresa_id ),
	CONSTRAINT unq_empresa UNIQUE ( cnpj ) 
 );

CREATE INDEX idx_cnpj_trgm ON plataforma_stakeholders.empresa USING  gin ( cnpj  gin_trgm_ops );

CREATE INDEX idx_nome_fantasia_empresa_trgm ON plataforma_stakeholders.empresa USING  gin ( nome_fantasia  gin_trgm_ops );

CREATE INDEX idx_razao_social_empresa_trgm ON plataforma_stakeholders.empresa USING  gin ( razao_social  gin_trgm_ops );

CREATE  TABLE plataforma_stakeholders.enderecos ( 
	entidade_id          integer  NOT NULL  ,
	tipo_entidade_id     smallint  NOT NULL  ,
	endereco_id          smallint  NOT NULL  ,
	logradouro           varchar(100)    ,
	numero               varchar(8)    ,
	complemento          varchar(100)    ,
	bairro               varchar(60)    ,
	cidade               varchar(60)  NOT NULL  ,
	uf                   char(2)  NOT NULL  ,
	cep                  varchar(8)  NOT NULL  ,
	CONSTRAINT pk_enderecos PRIMARY KEY ( entidade_id, tipo_entidade_id, endereco_id )
 );

CREATE INDEX idx_cidade_enderecos ON plataforma_stakeholders.enderecos USING  gin ( cidade  gin_trgm_ops );

CREATE  TABLE plataforma_stakeholders.log_consulta ( 
	log_consulta_id      integer DEFAULT nextval('plataforma_stakeholders.log_consulta_log_consulta_id_seq'::regclass) NOT NULL  ,
	mensagem             text  NOT NULL  ,
	consulta_id          integer  NOT NULL  ,
	tipo_log_id          integer  NOT NULL  ,
	data_log             timestamptz DEFAULT CURRENT_TIMESTAMP   ,
	CONSTRAINT pk_log_consulta PRIMARY KEY ( log_consulta_id )
 );

CREATE  TABLE plataforma_stakeholders.pessoa ( 
	firstname            varchar(40)    ,
	lastname             varchar(80)    ,
	cpf                  varchar(11)  NOT NULL  ,
	pessoa_id            integer DEFAULT nextval('plataforma_stakeholders.pessoa_pessoa_id_seq'::regclass) NOT NULL  ,
	linkedin             varchar(20)    ,
	instagram            varchar(20)    ,
	stakeholder          boolean DEFAULT false NOT NULL  ,
	em_prospecao         boolean DEFAULT false NOT NULL  ,
	sexo                 varchar(20)    ,
	data_nascimento      varchar(20)    ,
	nome_mae             varchar(255)    ,
	idade                integer    ,
	signo                varchar(35)    ,
	obito                boolean DEFAULT false   ,
	data_obito           varchar(20)    ,
	renda_estimada       numeric(10,2)    ,
	pep                  boolean DEFAULT false   ,
	projeto_id           integer    ,
	associado            boolean DEFAULT false   ,
	CONSTRAINT pk_pessoa PRIMARY KEY ( pessoa_id )
 );

CREATE INDEX idx_lastname_pessoa_trgm ON plataforma_stakeholders.pessoa USING  gin ( lastname  gin_trgm_ops );

CREATE UNIQUE INDEX idx_unique_pessoa_cpf ON plataforma_stakeholders.pessoa ( cpf );

CREATE INDEX idx_firstname_pessoa_trgm ON plataforma_stakeholders.pessoa USING  gin ( firstname  gin_trgm_ops );

CREATE INDEX idx_cpf_trgm ON plataforma_stakeholders.pessoa USING  gin ( cpf  gin_trgm_ops );

CREATE  TABLE plataforma_stakeholders.relacionamentos ( 
	entidade_origem_id   integer  NOT NULL  ,
	tipo_origem_id       smallint  NOT NULL  ,
	entidade_destino_id  integer  NOT NULL  ,
	tipo_destino_id      smallint  NOT NULL  ,
	tipo_relacao_id      smallint  NOT NULL  ,
	CONSTRAINT pk_relacionamentos PRIMARY KEY ( entidade_origem_id, tipo_origem_id, entidade_destino_id, tipo_destino_id )
 );

CREATE INDEX idx_relacionamentos ON plataforma_stakeholders.relacionamentos USING  btree ( tipo_relacao_id );

CREATE  TABLE plataforma_stakeholders.telefone ( 
	telefone_id          smallint  NOT NULL  ,
	telefone             varchar(16)  NOT NULL  ,
	operadora            varchar(20)    ,
	tipo_telefone        varchar(150)    ,
	whatsapp             boolean    ,
	entidade_id          integer  NOT NULL  ,
	tipo_entidade_id     smallint  NOT NULL  ,
	CONSTRAINT pk_telefone PRIMARY KEY ( telefone_id, tipo_entidade_id, entidade_id )
 );

CREATE  TABLE plataforma_stakeholders.cnae_secundario ( 
	id_empresa           integer  NOT NULL  ,
	id_segmento_empresa  smallint  NOT NULL  ,
	CONSTRAINT pk_cnae_secundario PRIMARY KEY ( id_empresa, id_segmento_empresa )
 );

ALTER TABLE plataforma_stakeholders.cnae_secundario ADD CONSTRAINT fk_cnae_secundario FOREIGN KEY ( id_segmento_empresa ) REFERENCES plataforma_stakeholders.segmento_empresa( segmento_id );

ALTER TABLE plataforma_stakeholders.cnae_secundario ADD CONSTRAINT fk_cnae_secundario_empresa FOREIGN KEY ( id_empresa ) REFERENCES plataforma_stakeholders.empresa( empresa_id );

ALTER TABLE plataforma_stakeholders.email ADD CONSTRAINT fk_email_tipo_entidade FOREIGN KEY ( tipo_entidade_id ) REFERENCES plataforma_stakeholders.tipo_entidade( tipo_entidade_id );

ALTER TABLE plataforma_stakeholders.empresa ADD CONSTRAINT fk_empresa_porte_empresa FOREIGN KEY ( porte_id ) REFERENCES plataforma_stakeholders.porte_empresa( porte_id );

ALTER TABLE plataforma_stakeholders.empresa ADD CONSTRAINT fk_empresa_projeto FOREIGN KEY ( projeto_id ) REFERENCES plataforma_stakeholders.projeto( projeto_id );

ALTER TABLE plataforma_stakeholders.empresa ADD CONSTRAINT fk_empresa_segmento_empresa FOREIGN KEY ( segmento_id ) REFERENCES plataforma_stakeholders.segmento_empresa( segmento_id );

ALTER TABLE plataforma_stakeholders.enderecos ADD CONSTRAINT fk_enderecos_tipo_entidade FOREIGN KEY ( tipo_entidade_id ) REFERENCES plataforma_stakeholders.tipo_entidade( tipo_entidade_id );

ALTER TABLE plataforma_stakeholders.log_consulta ADD CONSTRAINT fk_log_consulta_tipo_log FOREIGN KEY ( tipo_log_id ) REFERENCES plataforma_stakeholders.tipo_log( tipo_log_id );

ALTER TABLE plataforma_stakeholders.log_consulta ADD CONSTRAINT fk_log_consulta_consulta FOREIGN KEY ( consulta_id ) REFERENCES plataforma_stakeholders.consulta( consulta_id );

ALTER TABLE plataforma_stakeholders.pessoa ADD CONSTRAINT fk_pessoa_projeto FOREIGN KEY ( projeto_id ) REFERENCES plataforma_stakeholders.projeto( projeto_id );

ALTER TABLE plataforma_stakeholders.relacionamentos ADD CONSTRAINT fk_relacionamentos_relacao FOREIGN KEY ( tipo_relacao_id ) REFERENCES plataforma_stakeholders.tipo_relacao( tipo_relacao_id );

ALTER TABLE plataforma_stakeholders.relacionamentos ADD CONSTRAINT fk_relacionamentos_tipo_origem FOREIGN KEY ( tipo_origem_id ) REFERENCES plataforma_stakeholders.tipo_entidade( tipo_entidade_id );

ALTER TABLE plataforma_stakeholders.relacionamentos ADD CONSTRAINT fk_relacionamentos_tipo_destino FOREIGN KEY ( tipo_destino_id ) REFERENCES plataforma_stakeholders.tipo_entidade( tipo_entidade_id );

ALTER TABLE plataforma_stakeholders.telefone ADD CONSTRAINT fk_telefone_tipo_entidade FOREIGN KEY ( tipo_entidade_id ) REFERENCES plataforma_stakeholders.tipo_entidade( tipo_entidade_id );

