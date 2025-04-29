'use client'

import { useQuery } from '@tanstack/react-query'
import { usePathname, useRouter, useSearchParams } from 'next/navigation'
import { z } from 'zod'
import { DataTable } from './data-table'
import { columns } from './columns'
import { Pagination } from '@/components/pagination'
import { DataTableSkeleton } from './data-table-skeleton'
import { ChangeEvent, FormEvent, useState } from 'react'

import { Input } from '@/components/ui/input'
import { ChevronDown, FilterX, Plus, Search } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { CreatePessoaDialog } from './create-pessoa-dialog'
import { getPessoas } from '@/http/pessoa/get-pessoas'
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { getUfs } from '@/http/get-ufs'
import { getCitiesByUf } from '@/http/get-cities-by-uf'

export default function PessoaPage() {
  const [isOpenCreateStakeholder, setIsOpenCreateStakeholder] = useState(false)
  const searchParams = useSearchParams()

  const [searchType, setSearchType] = useState('cpf')

  const pathname = usePathname()
  const router = useRouter()

  const [selectedUF, setSelectedUF] = useState<string | null>(null)
  const [selectedCity, setSelectedCity] = useState<string | null>(null)

  // Busca UFs
  const { data: ufs, isLoading: isLoadingUFs } = useQuery({
    queryKey: ['ufs'],
    queryFn: getUfs,
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
  })

  const cpf = searchParams.get('cpf') ?? null
  const nome = searchParams.get('nome') ?? null
  const sobrenome = searchParams.get('sobrenome') ?? null

  const page = z.coerce
    .number()
    .transform((page) => page)
    .parse(searchParams.get('page') ?? '1')

  const size = z.coerce
    .number()
    .transform((size) => size)
    .parse(searchParams.get('size') ?? '10')

  const { data, isLoading } = useQuery({
    queryKey: [
      'pessoas',
      page,
      size,
      cpf,
      nome,
      sobrenome,
      selectedCity,
      selectedUF,
    ],
    queryFn: () =>
      getPessoas({
        page,
        size,
        cpf,
        nome,
        sobrenome,
        uf: selectedUF,
        cidade: selectedCity,
      }),
  })

  function handlePaginate(page: number) {
    const params = new URLSearchParams(Array.from(searchParams.entries()))

    params.set('page', (page + 1).toString())

    router.replace(`${pathname}?${params.toString()}`)
  }

  function handleSelectChange(e: ChangeEvent<HTMLSelectElement>) {
    setSearchType(e.target.value)
  }

  function handleFilter(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()

    const data = new FormData(e.currentTarget)
    const query = data.get('query')?.toString()

    const params = new URLSearchParams(Array.from(searchParams.entries()))

    if (query) {
      if (searchType === 'cpf') {
        params.set('cpf', query)
      }

      if (searchType === 'nome') {
        params.set('nome', query)
      }

      if (searchType === 'sobrenome') {
        params.set('sobrenome', query)
      }

      router.replace(`${pathname}?${params.toString()}`)
    }

    e.currentTarget.reset()
  }

  function handleClearFilters() {
    const params = new URLSearchParams(Array.from(searchParams.entries()))
    params.delete('page')
    params.delete('size')
    params.delete('cpf')
    params.delete('nome')
    params.delete('sobrenome')

    router.replace(`${pathname}?${params.toString()}`)
  }

  return (
    <main className="relative mx-auto min-h-screen w-full max-w-[1200px] pb-16 pt-28">
      <div className="space-y-4 px-4">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-semibold">Pessoas</h1>

          <div className="flex items-center gap-2">
            <div className="flex w-full rounded-lg shadow-sm shadow-black/[.04]">
              <form
                onSubmit={handleFilter}
                className="relative focus-within:z-10"
              >
                <Input
                  name="query"
                  className="peer -me-px h-9 rounded-e-none pe-9 ps-9 shadow-none focus-visible:z-10"
                  placeholder="Buscar por..."
                  type="text"
                />
                <div className="pointer-events-none absolute inset-y-0 start-0 flex items-center justify-center ps-3 text-muted-foreground/80 peer-disabled:opacity-50">
                  <Search size={16} strokeWidth={2} />
                </div>
              </form>

              <div className="relative">
                <select
                  className="peer inline-flex h-full appearance-none items-center rounded-e-lg border border-input bg-background pe-8 ps-3 text-sm text-muted-foreground ring-offset-background transition-shadow hover:bg-accent hover:text-foreground focus:z-10 focus-visible:border-ring focus-visible:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/30 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50"
                  aria-label="Search type"
                  defaultValue="cpf"
                  value={searchType}
                  onChange={handleSelectChange}
                >
                  <option value="cpf">CPF</option>
                  <option value="nome">Nome</option>
                  <option value="sobrenome">Sobrenome</option>
                </select>
                <span className="pointer-events-none absolute inset-y-0 end-px flex h-full w-9 items-center justify-center text-muted-foreground/80 peer-disabled:opacity-50">
                  <ChevronDown
                    size={16}
                    strokeWidth={2}
                    aria-hidden="true"
                    role="img"
                  />
                </span>
              </div>
            </div>

            <Button
              onClick={() => setIsOpenCreateStakeholder(true)}
              type="button"
              size="sm"
            >
              <Plus className="mr-2 size-4" />
              Adicionar
            </Button>

            <CreatePessoaDialog
              isOpen={isOpenCreateStakeholder}
              setIsOpen={setIsOpenCreateStakeholder}
            />
          </div>
        </div>

        <div className="flex items-end justify-between">
          <div className="flex items-end gap-2">
            {/* Select de UFs */}
            <Select onValueChange={(uf) => setSelectedUF(uf)}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Selecione uma UF" />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  {isLoadingUFs ? (
                    <SelectItem value="carregando" disabled>
                      Carregando...
                    </SelectItem>
                  ) : (
                    ufs?.map((uf: any) => (
                      <SelectItem key={uf.sigla} value={uf.sigla}>
                        {uf.sigla}
                      </SelectItem>
                    ))
                  )}
                </SelectGroup>
              </SelectContent>
            </Select>

            {/* Select de Cidades */}
            <Select onValueChange={(city) => setSelectedCity(city)}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Selecione uma cidade" />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  {isLoadingCities ? (
                    <SelectItem value="carregando" disabled>
                      Carregando...
                    </SelectItem>
                  ) : cities && cities.length > 0 ? (
                    cities.map((city: any) => (
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

          <Button
            title="Limpar filtros"
            variant="outline"
            onClick={handleClearFilters}
          >
            <FilterX className="size-4" />
            <span className="sr-only">Limpar filtros</span>
          </Button>
        </div>

        {data && <DataTable columns={columns} data={data.pessoas} />}

        {data?.pessoas && (
          <Pagination
            onPageChange={handlePaginate}
            pageIndex={page}
            perPage={data.meta.size}
            totalCount={data.meta.total}
          />
        )}

        {isLoading && <DataTableSkeleton />}
      </div>
    </main>
  )
}
