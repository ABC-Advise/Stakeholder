from app import db
from app.models.base_model import BaseModel
from app.models.porte_empresa import PorteEmpresa
from app.models.segmento_empresa import SegmentoEmpresa
from app.models.projeto import Projeto


class Empresa(BaseModel):
    __tablename__ = 'empresa'
    __table_args__ = {'schema': 'plataforma_stakeholders'}

    empresa_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cnpj = db.Column(db.String(14), nullable=False)
    razao_social = db.Column(db.String(255), nullable=False)
    nome_fantasia = db.Column(db.String(255), nullable=True)
    data_fundacao = db.Column(db.String(20), nullable=True)
    quantidade_funcionarios = db.Column(db.Integer, nullable=True)
    situacao_cadastral = db.Column(db.String, nullable=True)
    codigo_natureza_juridica = db.Column(db.Integer, nullable=True)
    natureza_juridica_descricao = db.Column(db.String, nullable=True)
    natureza_juridica_tipo = db.Column(db.String(150), nullable=True)
    faixa_funcionarios = db.Column(db.String(125), nullable=True)
    faixa_faturamento = db.Column(db.String(150), nullable=True)
    matriz = db.Column(db.Boolean, nullable=True)
    orgao_publico = db.Column(db.String(150), nullable=True)
    ramo = db.Column(db.String(150), nullable=True)
    tipo_empresa = db.Column(db.String(125), nullable=True)
    ultima_atualizacao_pj = db.Column(db.Date, nullable=True)
    porte_id = db.Column(db.SmallInteger, db.ForeignKey(PorteEmpresa.porte_id), nullable=False)
    segmento_id = db.Column(db.SmallInteger, db.ForeignKey(SegmentoEmpresa.segmento_id), nullable=False)
    linkedin = db.Column(db.String(20), nullable=True)
    instagram = db.Column(db.String(20), nullable=True)
    stakeholder = db.Column(db.Boolean, nullable=False, default=False)
    em_prospecao = db.Column(db.Boolean, nullable=False, default=False)
    projeto_id = db.Column(db.Integer, db.ForeignKey(Projeto.projeto_id), nullable=False)

    porte_empresa = db.relationship("PorteEmpresa", back_populates='empresa')
    segmento_empresa = db.relationship("SegmentoEmpresa", back_populates='empresa')
    projeto = db.relationship("Projeto", back_populates='empresa')
    cnae_secundarios = db.relationship("CnaeSecundario", back_populates="empresa")

    def to_dict(self, extend=True):
        base_dict = super().to_dict()

        custom_fields = {}
        if extend:
            custom_fields = {
                "projeto": self.projeto.nome if self.projeto else None,
                "cnae": self.segmento_empresa.cnae if self.segmento_empresa else None,
                "descricao_cnae": self.segmento_empresa.descricao if self.segmento_empresa else None,
                "porte": self.porte_empresa.descricao if self.porte_empresa else None
            }

        return {**base_dict, **custom_fields}
