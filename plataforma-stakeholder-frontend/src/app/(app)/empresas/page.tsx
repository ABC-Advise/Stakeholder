'use client';

import { useQuery } from '@tanstack/react-query';
import { debounce } from 'lodash';
import { ChevronDown, FilterX, LoaderCircle, Plus, Search } from 'lucide-react';
import { usePathname, useRouter, useSearchParams } from 'next/navigation';
import { ChangeEvent, FormEvent, useEffect, useMemo, useState } from 'react';
import { z } from 'zod';

import { Pagination } from '@/components/pagination';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectSeparator,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { getEmpresas } from '@/http/empresa/get-empresas';
import { getCitiesByUf } from '@/http/get-cities-by-uf';
import { getUfs } from '@/http/get-ufs';
import { getPorteEmpresa } from '@/http/porte/get-porte-empresa';
import { getSegmento, GetSegmentoResponse } from '@/http/segmento/get-segmento';

import { columns } from './columns';
import { CreateEmpresaDialog } from './create-empresa-dialog';
import { DataTable } from './data-table';
import { DataTableSkeleton } from './data-table-skeleton';

const searchFormSchema = z.object({
  cnpj: z.string().min(1, 'Digite um CNPJ válido.'),
});

type SearchFormSchema = z.infer<typeof searchFormSchema>;

export default function EmpresaPage() {
  const [isOpenCreateStakeholder, setIsOpenCreateStakeholder] = useState(false);
  const searchParams = useSearchParams();

  const [searchType, setSearchType] = useState('cnpj');

  const pathname = usePathname();
  const router = useRouter();

  const [selectedUF, setSelectedUF] = useState<string | null>(null);
  const [selectedCity, setSelectedCity] = useState<string | null>(null);

  const [search, setSearch] = useState('');
  const [pageSegmento, setPageSegmento] = useState(1);

  // Busca UFs
  const { data: ufs, isLoading: isLoadingUFs } = useQuery({
    queryKey: ['ufs'],
    queryFn: getUfs,
  });

  // Busca cidades com base na UF selecionada
  const {
    data: cities,
    isLoading: isLoadingCities,
    refetch: refetchCities,
  } = useQuery({
    queryKey: ['cities', selectedUF],
    queryFn: () => getCitiesByUf(selectedUF!),
    enabled: !!selectedUF, // Só executa quando uma UF for selecionada
  });

  const page = z.coerce
    .number()
    .transform(page => page)
    .parse(searchParams.get('page') ?? '1');

  const size = z.coerce
    .number()
    .transform(size => size)
    .parse(searchParams.get('size') ?? '10');

  const cnpj = searchParams.get('cnpj') ?? null;
  const razao_social = searchParams.get('razao_social') ?? null;
  const segmento_id = searchParams.get('segmento_id') ?? null;
  const porte_id = searchParams.get('porte_id') ?? null;

  const [loadedSegments, setLoadedSegments] = useState<
    GetSegmentoResponse['segmento_empresas']
  >([]);

  const { data, isLoading } = useQuery({
    queryKey: [
      'empresas',
      page,
      size,
      cnpj,
      razao_social,
      segmento_id,
      porte_id,
      selectedCity,
      selectedUF,
    ],
    queryFn: () =>
      getEmpresas({
        page,
        size,
        cnpj,
        razao_social,
        segmento_id,
        porte_id,
        uf: selectedUF,
        cidade: selectedCity,
      }),
  });

  const { data: segmento, isLoading: isLoadingSegmento } = useQuery({
    queryKey: ['segmento_empresa', pageSegmento, size, search],
    queryFn: () => getSegmento({ page: pageSegmento, size, descricao: search }),
  });

  const { data: porte, isLoading: isLoadingPorte } = useQuery({
    queryKey: ['porte_empresa', page, size],
    queryFn: () => getPorteEmpresa({ page: 1, size: 10 }),
  });

  function handlePaginate(page: number) {
    const params = new URLSearchParams(Array.from(searchParams.entries()));

    params.set('page', (page + 1).toString());

    router.replace(`${pathname}?${params.toString()}`);
  }

  function handleSelectChange(e: ChangeEvent<HTMLSelectElement>) {
    setSearchType(e.target.value);
  }

  function handleFilter(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();

    const data = new FormData(e.currentTarget);
    const query = data.get('query')?.toString();

    const params = new URLSearchParams(Array.from(searchParams.entries()));

    if (query) {
      if (searchType === 'cnpj') {
        params.set('cnpj', query);
      }

      if (searchType === 'razao_social') {
        params.set('razao_social', query);
      }

      router.replace(`${pathname}?${params.toString()}`);
    }

    e.currentTarget.reset();
  }

  function handleFilterSegmento(id: string) {
    const params = new URLSearchParams(Array.from(searchParams.entries()));

    console.log(id);

    params.set('segmento_id', id);

    router.replace(`${pathname}?${params.toString()}`);
  }

  function handleFilterPorte(id: string) {
    const params = new URLSearchParams(Array.from(searchParams.entries()));

    console.log(id);

    params.set('porte_id', id);

    router.replace(`${pathname}?${params.toString()}`);
  }

  function handleClearFilters() {
    const params = new URLSearchParams(Array.from(searchParams.entries()));
    params.delete('page');
    params.delete('size');
    params.delete('cnpj');
    params.delete('razao_social');
    params.delete('segmento_id');
    params.delete('porte_id');

    router.replace(`${pathname}?${params.toString()}`);
  }

  useEffect(() => {
    if (segmento && segmento.segmento_empresas) {
      if (pageSegmento === 1) {
        setLoadedSegments(segmento.segmento_empresas);
      } else {
        setLoadedSegments(prev => [...prev, ...segmento.segmento_empresas]);
      }
    }
  }, [segmento, pageSegmento]);

  // Função debounced para evitar muitas requisições enquanto o usuário digita
  const debouncedSearch = useMemo(
    () =>
      debounce((value: string) => {
        // Reinicia para a página 1 e atualiza a busca
        setPageSegmento(1);
        setSearch(value);
      }, 300),
    []
  );

  // Manipula as mudanças no input de busca
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const valor = e.target.value;
    if (valor === '') {
      // Se o campo estiver vazio, reinicia a página e a busca imediatamente,
      // fazendo com que a lista exiba os segmentos da primeira página padrão
      setPageSegmento(1);
      setSearch('');
    } else {
      debouncedSearch(valor);
    }
  };

  const isDisable = segmento ? pageSegmento === segmento?.meta.pages : false;

  return (
    <main className="relative mx-auto min-h-screen w-full max-w-[1200px] pb-16 pt-28">
      <div className="space-y-6 px-4">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-semibold">Empresas</h1>

          <div className="flex items-end gap-2">
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
                  defaultValue="cnpj"
                  value={searchType}
                  onChange={handleSelectChange}
                >
                  <option value="cnpj">CNPJ</option>
                  <option value="razao_social">Razão social</option>
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

            <CreateEmpresaDialog
              isOpen={isOpenCreateStakeholder}
              setIsOpen={setIsOpenCreateStakeholder}
            />
          </div>
        </div>

        <div className="flex items-end justify-between">
          <div className="flex items-end gap-2">
            {/* Select de UFs */}
            <Select onValueChange={uf => setSelectedUF(uf)}>
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
            <Select onValueChange={city => setSelectedCity(city)}>
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

            <Select onValueChange={handleFilterSegmento}>
              <SelectTrigger className="w-[240px]">
                <SelectValue placeholder="Selecione um segmento" />
              </SelectTrigger>
              <SelectContent className="relative">
                {/* Campo de busca fixo dentro do Select */}
                <div className="fixed left-0 top-0 z-20 flex w-full flex-col gap-2 bg-white p-2">
                  <Input
                    placeholder="Buscar segmentos..."
                    onChange={handleInputChange}
                    onKeyDown={e => e.stopPropagation()}
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
                  {loadedSegments.map(item => (
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
                  onClick={() => setPageSegmento(prev => prev + 1)}
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

            <Select onValueChange={value => handleFilterPorte(value)}>
              <SelectTrigger className="w-[240px]">
                <SelectValue placeholder="Selecione um porte" />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  <SelectLabel>Porte da empresa</SelectLabel>
                  {porte?.porte_empresas.map(porte => (
                    <SelectItem
                      key={porte.porte_id}
                      value={porte.porte_id.toString()}
                    >
                      {porte.descricao}
                    </SelectItem>
                  ))}
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

        {data && <DataTable columns={columns} data={data.empresas} />}

        {!isLoading && !data && (
          <p className="py-4 text-muted-foreground">
            Não foi possível encontrar sua busca...
          </p>
        )}

        {data?.empresas && (
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
  );
}
