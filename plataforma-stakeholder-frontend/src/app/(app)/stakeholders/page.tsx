'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { DropdownMenuCheckboxItemProps } from '@radix-ui/react-dropdown-menu';
import { useQuery } from '@tanstack/react-query';
import { FilterX, ListFilter, Loader2, Plus, Search } from 'lucide-react';
import { usePathname, useRouter, useSearchParams } from 'next/navigation';
import { FormEvent, useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';

import { Pagination } from '@/components/pagination';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { getCitiesByUf } from '@/http/get-cities-by-uf';
import { getUfs } from '@/http/get-ufs';
import { getStakeholders } from '@/http/stakeholders/get-stakeholders';

import { columns } from './columns';
import { CreateStakeholderDialog } from './create-stakeholder-dialog';
import { DataTable } from './data-table';
import { DataTableSkeleton } from './data-table-skeleton';

type Checked = DropdownMenuCheckboxItemProps['checked'];

const searchFormSchema = z.object({
  documento: z.string().min(1, 'Digite um documento válido.'),
});

type SearchFormSchema = z.infer<typeof searchFormSchema>;

export default function StakeholdersPage() {
  const [isOpenCreateStakeholder, setIsOpenCreateStakeholder] = useState(false);

  const [showProspect, setShowProspect] = useState<Checked>(false);
  const [showAssociado, setShowAssociado] = useState<Checked>(false);

  const searchParams = useSearchParams();
  const pathname = usePathname();
  const router = useRouter();

  const [selectedUF, setSelectedUF] = useState<string | null>(null);
  const [selectedCity, setSelectedCity] = useState<string | null>(null);

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

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<SearchFormSchema>({
    resolver: zodResolver(searchFormSchema),
  });

  const documento = searchParams.get('documento') ?? null;

  const page = z.coerce
    .number()
    .transform(page => page)
    .parse(searchParams.get('page') ?? '1');

  const size = z.coerce
    .number()
    .transform(size => size)
    .parse(searchParams.get('size') ?? '10');

  const { data, isLoading } = useQuery({
    queryKey: [
      'stakeholders',
      page,
      size,
      documento,
      showProspect,
      showAssociado,
      selectedCity,
      selectedUF,
    ],
    queryFn: () =>
      getStakeholders({
        page,
        size,
        documento,
        em_prospecao: showProspect || undefined,
        associado: showAssociado || undefined,
        uf: selectedUF,
        cidade: selectedCity,
      }),
  });

  function handlePaginate(page: number) {
    const params = new URLSearchParams(Array.from(searchParams.entries()));

    params.set('page', (page + 1).toString());

    router.replace(`${pathname}?${params.toString()}`);
  }

  function handleClearFilters() {
    const params = new URLSearchParams(Array.from(searchParams.entries()));
    params.delete('page');
    params.delete('size');
    params.delete('documento');
    setShowProspect(false);
    setShowAssociado(false);
    setSelectedCity(null);
    setSelectedUF(null);

    router.replace(`${pathname}?${params.toString()}`);
  }

  function handleSearchDocument(data: SearchFormSchema) {
    const params = new URLSearchParams(Array.from(searchParams.entries()));

    params.set('documento', data.documento);

    reset();

    router.replace(`${pathname}?${params.toString()}`);
  }

  return (
    <main className="relative mx-auto min-h-screen w-full max-w-[1200px] pb-16 pt-28">
      <div className="space-y-4 px-4">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-semibold">Stakeholders</h1>

          <Button
            onClick={() => setIsOpenCreateStakeholder(true)}
            type="button"
            size="sm"
          >
            <Plus className="mr-2 size-4" />
            Adicionar
          </Button>

          <CreateStakeholderDialog
            isOpen={isOpenCreateStakeholder}
            setIsOpen={setIsOpenCreateStakeholder}
          />
        </div>
        <div className="flex items-center justify-between">
          <form
            className="relative w-full max-w-xs"
            onSubmit={handleSubmit(handleSearchDocument)}
          >
            <Input
              placeholder="Buscar por documento..."
              className="-me-px h-9 pl-9"
              {...register('documento')}
            />

            <div className="pointer-events-none absolute inset-y-0 start-0 flex items-center justify-center ps-3 text-muted-foreground/80 peer-disabled:opacity-50">
              <Search size={16} strokeWidth={2} />
            </div>
          </form>

          <div className="flex items-center gap-2">
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

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline">
                  <ListFilter className="mr-2 size-4" />
                  Filtros
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-56">
                <DropdownMenuLabel>Filtrar por</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuCheckboxItem
                  checked={showProspect}
                  onCheckedChange={setShowProspect}
                >
                  Em prospecção
                </DropdownMenuCheckboxItem>
                <DropdownMenuCheckboxItem
                  checked={showAssociado}
                  onCheckedChange={setShowAssociado}
                >
                  Associado
                </DropdownMenuCheckboxItem>
              </DropdownMenuContent>
            </DropdownMenu>

            <Button
              title="Limpar filtros"
              variant="outline"
              onClick={handleClearFilters}
            >
              <FilterX className="size-4" />
              <span className="sr-only">Limpar filtros</span>
            </Button>
          </div>
        </div>

        {data && <DataTable columns={columns} data={data.stakeholders} />}

        {!isLoading && !data && (
          <p className="py-4 text-muted-foreground">
            Não foi possível encontrar sua busca...
          </p>
        )}

        {data?.stakeholders && (
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
