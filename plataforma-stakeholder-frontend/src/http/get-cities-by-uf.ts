import axios from 'axios'

export const getCitiesByUf = async (uf: string) => {
  const response = await axios.get(
    `https://servicodados.ibge.gov.br/api/v1/localidades/estados/${uf}/municipios`,
  )
  return response.data.map((city: { nome: string }) => city.nome)
}
