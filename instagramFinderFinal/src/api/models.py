from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# --- Modelos Base --- 

class BaseEntity(BaseModel):
    id: int
    name: Optional[str] = None # nome_fantasia ou nome completo
    instagram_db: Optional[str] = Field(None, alias="instagram") # Mapeia 'instagram' do DB

class CompanyEntity(BaseEntity):
    cnpj: Optional[str] = None
    razao_social: Optional[str] = None
    # Adicionar outros campos relevantes da tabela empresa, se necessário no response
    # nome_fantasia será mapeado para 'name' em BaseEntity
    segmento_id: Optional[int] = None 

    class Config:
        orm_mode = True
        allow_population_by_field_name = True # Permite usar 'instagram'

class PersonEntity(BaseEntity):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    cpf: Optional[str] = None # Assumindo que existe ou será adicionado
    # Adicionar outros campos relevantes da tabela pessoa

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

class LawyerEntity(PersonEntity): # Herda de Person
    oab: Optional[str] = None
    # Adicionar outros campos relevantes da tabela advogado

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

class InstagramProfileCandidate(BaseModel):
    # Campos principais retornados pela HikerAPI
    pk: Optional[int] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    profile_pic_url: Optional[str] = None
    is_private: Optional[bool] = False
    is_verified: Optional[bool] = False
    # Corrigir nome do campo e usar alias para manter "bio" na API
    biography: Optional[str] = Field(None, alias="bio") 
    is_business: Optional[bool] = None
    # Poderia adicionar mais campos se o frontend precisar

class ValidatedProfileDetail(BaseModel):
    score: Optional[float] = None
    is_business_profile: Optional[bool] = None
    # Adicionar detalhes da validação se necessário

class ValidatedProfileResponse(BaseModel):
    perfil: InstagramProfileCandidate
    score: float
    is_business_profile: bool
    # Pode incluir "detalhes_validacao" se for útil para o frontend

# --- Modelos de Resposta dos Endpoints ---

class EntityProfileResponse(BaseModel):
    # Usaremos Any por enquanto para flexibilidade, idealmente seria uma Union dos tipos de entidade
    entity: Dict[str, Any] # Ou Union[CompanyEntity, PersonEntity, LawyerEntity]
    candidates: List[InstagramProfileCandidate]
    validated_profile: Optional[ValidatedProfileResponse]
    possible_profiles: Optional[List[str]] = None # Adicionado campo para sugestões

class AllEntitiesResponseItem(BaseModel):
    # Usaremos Any por enquanto
    entity: Dict[str, Any]
    candidates: Optional[List[InstagramProfileCandidate]] = None
    validated_profile: Optional[ValidatedProfileResponse] = None
    possible_profiles: Optional[List[str]] = None
    error: Optional[str] = None

class CompanyRelatedResponse(BaseModel):
    company: EntityProfileResponse # Resposta para a empresa principal
    related_entities: List[EntityProfileResponse] # Lista de respostas para entidades relacionadas

class ErrorResponse(BaseModel):
    detail: str 

class ConfirmInstagramRequest(BaseModel):
    instagram: str = Field(..., description="Username do Instagram a ser confirmado") 