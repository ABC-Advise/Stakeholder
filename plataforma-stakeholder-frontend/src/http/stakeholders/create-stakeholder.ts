import { api } from '../api-client';

interface CreateStakeholderRequest {
  documento: string;
  prospeccao: boolean;
  camada_advogados?: boolean;
  stakeholder_advogado?: boolean;
  associado?: boolean;
}

interface CreateStakeholderResponse {
  message: string;
}

export async function createStakeholder({
  documento,
  prospeccao,
  camada_advogados,
  stakeholder_advogado,
  associado,
}: CreateStakeholderRequest): Promise<CreateStakeholderResponse> {
  const response = await api.post(`/stakeholders`, {
    documento,
    prospeccao,
    camada_advogados,
    stakeholder_advogado,
    associado,
  });

  return response.data;
}
