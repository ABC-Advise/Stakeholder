import axios from 'axios';

export async function getUfs() {
  const response = await axios.get(
    `https://servicodados.ibge.gov.br/api/v1/localidades/estados`
  );

  return response.data;
}
