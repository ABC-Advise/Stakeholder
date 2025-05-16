import { api } from '../api-client';

interface GetSegmentoResponseQuery {
  segmento_id?: number | null;
  page?: number | null;
  size?: number | null;
  descricao?: string | null;
}

export interface GetSegmentoResponse {
  segmento_empresas: {
    segmento_id: number;
    cnae: string;
    descricao: string;
  }[];
  meta: {
    total: number;
    page: number;
    size: number;
    pages: number;
  };
}

export async function getSegmento({
  segmento_id,
  page,
  size,
  descricao,
}: GetSegmentoResponseQuery): Promise<GetSegmentoResponse> {
  const response = await api.get(`/segmento_empresa`, {
    params: {
      segmento_id,
      page,
      size,
      descricao,
    },
  });

  console.log(descricao);
  console.log(response.data);

  return response.data;
}
