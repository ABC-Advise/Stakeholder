'use client'

import dynamic from 'next/dynamic'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectSeparator,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Separator } from '@/components/ui/separator'
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'
import { getCitiesByUf } from '@/http/get-cities-by-uf'
import { getNetwork } from '@/http/get-network'
import { getUfs } from '@/http/get-ufs'
import { getProjetos } from '@/http/projetos/get-projetos'
import { useQuery } from '@tanstack/react-query'
import {
  ChevronsLeft,
  ChevronsRight,
  FilterX,
  Loader2,
  LoaderCircle,
  Spline,
} from 'lucide-react'
import { usePathname, useRouter, useSearchParams } from 'next/navigation'
import { FormEvent, useEffect, useMemo, useState } from 'react'
import { z } from 'zod'
import { getSegmento, GetSegmentoResponse } from '@/http/segmento/get-segmento'
import { debounce } from 'lodash'

// carregar componente no client side
const NetworkGraph = dynamic(
  () => import('@/components/network-graph').then((mod) => mod.NetworkGraph),
  {
    ssr: false,
    loading: () => (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="size-8 animate-spin" />
      </div>
    ),
  },
)

const filterSchema = z.object({
  nome: z.string().optional(),
  razao_social: z.string().optional(),
  projeto_id: z.string().optional(),
  uf: z.string().optional(),
  cidade: z.string().optional(),
  camada: z.string().optional(),
  em_prospeccao: z.boolean().default(false),
  associado: z.boolean().default(false),
})

type FilterSchemaForm = z.infer<typeof filterSchema>

export default function Home() {
  const searchParams = useSearchParams()

  const pathname = usePathname()
  const router = useRouter()

  const [searchTerm, setSearchTerm] = useState('')

  const [currentLayer, setCurrentLayer] = useState('0')
  const [openFilter, setOpenFilter] = useState(true)

  const [selectedValues, setSelectedValues] = useState<string[]>([])

  const [selectedUF, setSelectedUF] = useState<string | undefined>(undefined)

  const [selectedCity, setSelectedCity] = useState<string | undefined>(
    undefined,
  )

  const [selectedProjeto, setSelectedProjeto] = useState<string | undefined>(
    undefined,
  )

  const [selectedSegmento, setSelectedSegmento] = useState<string | undefined>(
    undefined,
  )

  const [search, setSearch] = useState('')
  const [pageSegmento, setPageSegmento] = useState(1)

  const [loadedSegments, setLoadedSegments] = useState<
    GetSegmentoResponse['segmento_empresas']
  >([])

  const nome = searchParams.get('nome') ?? null
  const razao_social = searchParams.get('razao_social') ?? null

  const documento = searchParams.get('documento') ?? null
  const layer = searchParams.get('layer') ?? null

  const associado = searchParams.get('associado') ?? null
  const em_prospeccao = searchParams.get('em_prospeccao') ?? null

  const cidade = searchParams.get('cidade') ?? null
  const uf = searchParams.get('uf') ?? null
  const projeto_id = searchParams.get('projeto_id') ?? null
  const segmento_id = searchParams.get('segmento_id') ?? null

  const { data: segmento, isLoading: isLoadingSegmento } = useQuery({
    queryKey: ['segmento_empresa', pageSegmento, search],
    queryFn: () =>
      getSegmento({ page: pageSegmento, size: 10, descricao: search }),
    staleTime: 1000 * 60 * 5, // Cache por 5 minutos
    retry: 1,
  })

  // Busca UFs
  const { data: ufs, isLoading: isLoadingUFs } = useQuery({
    queryKey: ['ufs'],
    queryFn: getUfs,
    staleTime: 1000 * 60 * 60, // Cache por 1 hora
    retry: 1,
  })

  // Busca cidades com base na UF selecionada
  const {
    data: cities,
    isLoading: isLoadingCities,
    refetch: refetchCities,
  } = useQuery({
    queryKey: ['cities', selectedUF],
    queryFn: () => getCitiesByUf(selectedUF!),
    enabled: !!selectedUF, // Só executa quando uma UF for selecionada
    staleTime: 1000 * 60 * 60, // Cache por 1 hora
    retry: 1,
  })

  const { data: projetos, isLoading: isLoadingProjetos } = useQuery({
    queryKey: ['projetos'],
    queryFn: () => getProjetos({}),
    staleTime: 1000 * 60 * 5, // Cache por 5 minutos
    retry: 1,
  })

  const { data, isLoading, error: networkError } = useQuery({
    queryKey: [
      'network',
      documento,
      nome,
      razao_social,
      layer,
      associado,
      em_prospeccao,
      uf,
      cidade,
      projeto_id,
      segmento_id,
    ],
    queryFn: async () =>
      getNetwork({
        documento,
        nome,
        razao_social,
        camadas: Number(layer) > 0 ? Number(layer) : null,
        associado,
        em_prospecao: em_prospeccao,
        uf,
        cidade,
        projeto_id,
        segmento_id,
      }),
    staleTime: 1000 * 60 * 5, // Cache por 5 minutos
    retry: 1, // Tenta apenas uma vez em caso de erro
  })

  const memoizedClusters = useMemo(() => {
    console.log("Parent (page.tsx): Recalculating memoizedClusters for NetworkGraph...");
    return data || []; // Return data from query or empty array if undefined/null
  }, [data]); // Dependency is the data from useQuery

  function handleFilterNome(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const params = new URLSearchParams(Array.from(searchParams.entries()))

    const data = new FormData(e.currentTarget)
    const nome = data.get('nome')?.toString()

    if (nome) {
      params.set('nome', nome)
    }

    router.replace(`${pathname}?${params.toString()}`)

    e.currentTarget.reset()
  }

  function handleFilterRazaoSocial(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const params = new URLSearchParams(Array.from(searchParams.entries()))

    const data = new FormData(e.currentTarget)
    const razao_social = data.get('razao_social')?.toString()

    if (razao_social) {
      params.set('razao_social', razao_social)
    }

    router.replace(`${pathname}?${params.toString()}`)

    e.currentTarget.reset()
  }

  function handleFilterLayer(layer: string) {
    const params = new URLSearchParams(Array.from(searchParams.entries()))

    setCurrentLayer(layer)

    if (layer === '0') {
      params.delete('layer')
    } else {
      params.set('layer', layer)
    }

    router.replace(`${pathname}?${params.toString()}`)
  }

  useEffect(() => {
    const initialValues: string[] = []
    if (associado) {
      initialValues.push('1') // Valor do toggle associado
    }
    if (em_prospeccao) {
      initialValues.push('2') // Valor do toggle em prospecção
    }
    setSelectedValues(initialValues)
  }, [associado, em_prospeccao])

  useEffect(() => {
    if (layer) setCurrentLayer(layer)

    if (uf) setSelectedUF(uf)
    if (cidade) setSelectedCity(cidade)
    if (projeto_id) setSelectedProjeto(projeto_id)
  }, [layer, uf, cidade, projeto_id])

  const updateUrlParams = (key: string, value: boolean) => {
    const params = new URLSearchParams(searchParams.toString())

    if (value) {
      // Adicionar o parâmetro
      params.set(key, 'true')
    } else {
      // Remover o parâmetro
      params.delete(key)
    }

    // Atualizar a URL sem recarregar
    router.push(`?${params.toString()}`)
  }

  const handleToggleChange = (value: string) => {
    setSelectedValues((prev) => {
      const isCurrentlySelected = prev.includes(value)

      // Atualizar os parâmetros da URL
      if (value === '1') updateUrlParams('associado', !isCurrentlySelected)
      if (value === '2') updateUrlParams('em_prospeccao', !isCurrentlySelected)

      return isCurrentlySelected
        ? prev.filter((v) => v !== value) // Remover se estava marcado
        : [...prev, value] // Adicionar se estava desmarcado
    })
  }

  const updateSelectUrlParams = (key: string, value: string | null) => {
    const params = new URLSearchParams(Array.from(searchParams.entries()))

    if (value) {
      params.set(key, value)
    } else {
      params.delete(key)
    }

    router.replace(`?${params.toString()}`)
  }

  const handleUFChange = (uf: string) => {
    setSelectedUF(uf)
    updateSelectUrlParams('uf', uf)
  }

  const handleCityChange = (city: string) => {
    setSelectedCity(city)
    updateSelectUrlParams('cidade', city)
  }

  const handleProjetoChange = (projeto: string) => {
    setSelectedProjeto(projeto)
    updateSelectUrlParams('projeto_id', projeto)
  }

  function handleClearFilters() {
    setSelectedUF(undefined)
    setSelectedCity(undefined)
    setSelectedProjeto(undefined)

    const params = new URLSearchParams(Array.from(searchParams.entries()))

    params.delete('nome')
    params.delete('razao_social')

    params.delete('documento')
    params.delete('associado')
    params.delete('em_prospeccao')

    params.delete('projeto_id')
    params.delete('segmento_id')
    params.delete('uf')
    params.delete('cidade')

    params.delete('layer')

    router.replace(`${pathname}?${params.toString()}`)
  }

  const filteredUFs = ufs?.filter((uf: any) =>
    uf.sigla.toLowerCase().includes(searchTerm.toLowerCase()),
  )

  const filteredCities = cities?.filter((city: string) =>
    city.toLowerCase().includes(searchTerm.toLowerCase()),
  )

  function handleFilterSegmento(id: string) {
    const params = new URLSearchParams(Array.from(searchParams.entries()))
    setSelectedSegmento(id)

    params.set('segmento_id', id)

    router.replace(`${pathname}?${params.toString()}`)
  }

  useEffect(() => {
    if (segmento && segmento.segmento_empresas) {
      if (pageSegmento === 1) {
        setLoadedSegments(segmento.segmento_empresas)
      } else {
        setLoadedSegments((prev) => [...prev, ...segmento.segmento_empresas])
      }
    }
  }, [segmento, pageSegmento])

  // Função debounced para evitar muitas requisições enquanto o usuário digita
  const debouncedSearch = useMemo(
    () =>
      debounce((value: string) => {
        // Reinicia para a página 1 e atualiza a busca
        setPageSegmento(1)
        setSearch(value)
      }, 300),
    [],
  )

  // Manipula as mudanças no input de busca
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const valor = e.target.value
    if (valor === '') {
      // Se o campo estiver vazio, reinicia a página e a busca imediatamente,
      // fazendo com que a lista exiba os segmentos da primeira página padrão
      setPageSegmento(1)
      setSearch('')
    } else {
      debouncedSearch(valor)
    }
  }

  const isDisable = segmento ? pageSegmento === segmento?.meta.pages : false

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <Loader2 className="size-8 animate-spin" />
      </div>
    )
  }

  return (
    <>
      {/* filters */}
      <div
        className={`absolute ${openFilter ? 'left-4' : '-left-[288px]'} top-24 z-20 space-y-4 transition-all ease-in-out`}
      >
        <div className="relative w-72 space-y-2 rounded-lg border bg-background p-3">
          <button
            type="button"
            title="Filtros"
            className="absolute -right-10 top-2 flex h-10 w-10 items-center justify-center rounded-e-lg border bg-background"
            onClick={() => setOpenFilter(!openFilter)}
          >
            {openFilter ? (
              <ChevronsLeft className="size-4" />
            ) : (
              <ChevronsRight className="size-4" />
            )}
          </button>

          <div className="flex items-center justify-between">
            <h2 className="font-semibold">Filtros</h2>

            <Button
              title="Limpar filtros"
              variant="ghost"
              onClick={handleClearFilters}
              size="icon"
            >
              <FilterX className="size-4" />
              <span className="sr-only">Limpar filtros</span>
            </Button>
          </div>

          <form onSubmit={handleFilterNome}>
            <Input
              defaultValue={nome ?? ''}
              name="nome"
              placeholder="Buscar por nome"
              type="text"
            />
          </form>

          <form onSubmit={handleFilterRazaoSocial}>
            <Input
              defaultValue={razao_social ?? ''}
              name="razao_social"
              placeholder="Buscar por razão social"
              type="text"
            />
          </form>

          <Select value={selectedSegmento} onValueChange={handleFilterSegmento}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Selecione um segmento" />
            </SelectTrigger>
            <SelectContent className="relative">
              {/* Campo de busca fixo dentro do Select */}
              <div className="fixed left-0 top-0 z-20 flex w-full flex-col gap-2 bg-white p-2">
                <Input
                  placeholder="Buscar segmentos..."
                  onChange={handleInputChange}
                  onKeyDown={(e) => e.stopPropagation()}
                />
                <SelectSeparator />
              </div>
              <SelectGroup>
                <SelectLabel className="flex items-center justify-between gap-16 pt-16">
                  Segmento da empresa
                  <span className="text-sm font-normal text-muted-foreground">
                    Resultados ({loadedSegments.length})
                  </span>
                </SelectLabel>
                {/* Exibe os segmentos armazenados */}
                {loadedSegments.map((item) => (
                  <SelectItem
                    key={item.segmento_id}
                    value={item.segmento_id.toString()}
                  >
                    {item.descricao}
                  </SelectItem>
                ))}
              </SelectGroup>
              <Button
                variant="ghost"
                size="sm"
                className="w-full py-5"
                onClick={() => setPageSegmento((prev) => prev + 1)}
                disabled={isDisable}
              >
                {isLoadingSegmento ? (
                  <LoaderCircle className="size-4 animate-spin" />
                ) : (
                  'Carregar mais'
                )}
              </Button>
            </SelectContent>
          </Select>

          <Select onValueChange={handleProjetoChange} value={selectedProjeto}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Selecione um projeto" />
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                {projetos?.projetos.map((projeto) => (
                  <SelectItem
                    key={projeto.projeto_id}
                    value={projeto.projeto_id.toString()}
                  >
                    {projeto.nome}
                  </SelectItem>
                ))}
              </SelectGroup>
            </SelectContent>
          </Select>

          <div className="flex flex-col gap-2">
            <Select onValueChange={handleUFChange} value={selectedUF}>
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Selecione uma UF" />
              </SelectTrigger>
              <SelectContent>
                {/* Campo de busca */}
                <div className="p-2">
                  <input
                    type="text"
                    placeholder="Pesquisar..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    onKeyDown={(e) => e.stopPropagation()}
                    className="w-full rounded border px-2 py-1"
                  />
                </div>

                {/* Lista de itens filtrados */}
                <SelectGroup>
                  {isLoadingUFs ? (
                    <SelectItem value="carregando" disabled>
                      Carregando...
                    </SelectItem>
                  ) : filteredUFs && filteredUFs.length > 0 ? (
                    filteredUFs.map((uf: any) => (
                      <SelectItem key={uf.sigla} value={uf.sigla}>
                        {uf.sigla}
                      </SelectItem>
                    ))
                  ) : (
                    <SelectItem value="nenhuma-uf" disabled>
                      Nenhuma UF encontrada
                    </SelectItem>
                  )}
                </SelectGroup>
              </SelectContent>
            </Select>

            <Select onValueChange={handleCityChange} value={selectedCity}>
              <SelectTrigger className="w-">
                <SelectValue placeholder="Selecione uma cidade" />
              </SelectTrigger>
              <SelectContent>
                {/* Campo de busca */}
                <div className="p-2">
                  <input
                    type="text"
                    placeholder="Pesquisar..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    onKeyDown={(e) => e.stopPropagation()}
                    className="w-full rounded border px-2 py-1"
                  />
                </div>

                {/* Lista de itens filtrados */}
                <SelectGroup>
                  {isLoadingCities ? (
                    <SelectItem value="carregando" disabled>
                      Carregando...
                    </SelectItem>
                  ) : filteredCities && filteredCities.length > 0 ? (
                    filteredCities.map((city: string) => (
                      <SelectItem key={city} value={city}>
                        {city}
                      </SelectItem>
                    ))
                  ) : (
                    <SelectItem value="sem-cidades" disabled>
                      Nenhuma cidade encontrada
                    </SelectItem>
                  )}
                </SelectGroup>
              </SelectContent>
            </Select>
          </div>

          <ToggleGroup
            value={selectedValues}
            type="multiple"
            className="flex flex-col items-start"
          >
            <div className="flex items-center gap-2">
              <ToggleGroupItem
                className="size-5 p-0"
                variant="outline"
                value="1"
                onClick={() => handleToggleChange('1')}
                aria-label="Associado"
              />
              <span className="text-sm text-zinc-600">Associado</span>
            </div>

            <div className="flex items-center gap-2">
              <ToggleGroupItem
                className="size-5 p-0"
                variant="outline"
                value="2"
                onClick={() => handleToggleChange('2')}
                aria-label="Em prospecção"
              />
              <span className="text-sm text-zinc-600">Em prospecção</span>
            </div>
          </ToggleGroup>

          <Separator />

          <ToggleGroup
            defaultValue={currentLayer}
            type="single"
            className="flex flex-col items-start"
          >
            <div className="flex items-center gap-2">
              <ToggleGroupItem
                className="size-5 p-0"
                variant="outline"
                value="1"
                aria-label="Camadas 1"
                onClick={() => handleFilterLayer('1')}
              />
              <span className="text-sm text-zinc-600">Camada 1</span>
            </div>
            <div className="flex items-center gap-2">
              <ToggleGroupItem
                className="size-5 p-0"
                variant="outline"
                value="2"
                aria-label="Camadas 2"
                onClick={() => handleFilterLayer('2')}
              />
              <span className="text-sm text-zinc-600">Camada 2</span>
            </div>
            <div className="flex items-center gap-2">
              <ToggleGroupItem
                className="size-5 p-0"
                variant="outline"
                value="3"
                aria-label="Camadas 3"
                onClick={() => handleFilterLayer('3')}
              />
              <span className="text-sm text-zinc-600">Camada 3</span>
            </div>

            <div className="flex items-center gap-2">
              <ToggleGroupItem
                className="size-5 p-0"
                variant="outline"
                value="0"
                aria-label="Todas camadas"
                onClick={() => handleFilterLayer('0')}
              />
              <span className="text-sm text-zinc-600">Todas camadas</span>
            </div>
          </ToggleGroup>

          {/* <Button className="w-full">Filtrar</Button> */}
        </div>
      </div>

      {memoizedClusters && memoizedClusters.length > 0 ? (
        <NetworkGraph clusters={memoizedClusters} />
      ) : (
        !isLoading && !networkError && (
          <div className="flex min-h-screen items-center justify-center">
            <span className="rounded-lg border bg-background p-2 text-sm text-muted-foreground">
              Não há dados de rede para exibir com os filtros atuais.
            </span>
          </div>
        )
      )}

      {/* help */}
      <div className="absolute bottom-4 left-4 space-y-4">
        <div className="w-52 space-y-2 rounded-lg border bg-background p-3">
          <h2 className="font-semibold">Legendas</h2>

          <span className="text-xs font-medium text-muted-foreground">
            Nodes
          </span>
          <div className="flex items-center gap-2">
            <div className="size-4 rounded bg-orange-600" />
            <span className="text-sm text-zinc-600">Stakeholder</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="size-4 rounded bg-emerald-500" />
            <span className="text-sm text-zinc-600">Em prospecção</span>
          </div>

          <span className="text-xs font-medium text-muted-foreground">
            Links
          </span>
          <div className="flex items-center gap-2">
            <Spline className="size-4 text-orange-400" />
            <span className="text-sm text-zinc-600">Clusters</span>
          </div>
        </div>
      </div>

      <div className="absolute bottom-4 right-4 space-x-4">
        {networkError && (
          <span className="rounded-lg border bg-background p-2 text-sm text-rose-500">
            Erro ao carregar os dados. Por favor, tente novamente.
          </span>
        )}
        {!isLoading && !data && !networkError && (
          <span className="rounded-lg border bg-background p-2 text-sm text-rose-500">
            Não foi possível encontrar os dados solicitados!
          </span>
        )}
        <Button
          variant="outline"
          className="rounded-full text-lg font-semibold text-zinc-700"
        >
          ?
        </Button>
      </div>
    </>
  )
}
