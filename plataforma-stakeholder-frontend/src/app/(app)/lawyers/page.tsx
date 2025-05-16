'use client';

import { DropdownMenuCheckboxItemProps } from '@radix-ui/react-dropdown-menu';
import { useQuery } from '@tanstack/react-query';
import { ChevronDown, FilterX, ListFilter, Search } from 'lucide-react';
import { usePathname, useRouter, useSearchParams } from 'next/navigation';
import { ChangeEvent, FormEvent, useState } from 'react';
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
import { getLawyers } from '@/http/lawyers/get-lawyers';

import { columns } from './columns';
import { DataTable } from './data-table';
import { DataTableSkeleton } from './data-table-skeleton';

type Checked = DropdownMenuCheckboxItemProps['checked'];

const searchSchema = z.object({
  query: z.string().min(1),
});

type SearchScchema = z.infer<typeof searchSchema>;

export default function LawyersPage() {
  const [searchType, setSearchType] = useState('oab');
  const [searchQuery, setSearchQuery] = useState('');

  const [isOpenCreateStakeholder, setIsOpenCreateStakeholder] = useState(false);

  const [showClients, setShowClients] = useState<Checked>(true);
  const [showProspect, setShowProspect] = useState<Checked>(false);

  const searchParams = useSearchParams();

  const oab = searchParams.get('oab') ?? null;
  const cpf = searchParams.get('cpf') ?? null;
  const nome = searchParams.get('nome') ?? null;
  const sobrenome = searchParams.get('sobrenome') ?? null;
  const stakeholder = searchParams.get('stakeholder') ?? null;

  const pathname = usePathname();
  const router = useRouter();

  const page = z.coerce
    .number()
    .transform(page => page)
    .parse(searchParams.get('page') ?? '1');

  const size = z.coerce
    .number()
    .transform(size => size)
    .parse(searchParams.get('size') ?? '10');

  const { data, isLoading } = useQuery({
    queryKey: ['lawyers', page, size, oab, cpf, nome, sobrenome, stakeholder],
    queryFn: () =>
      getLawyers({ page, size, oab, cpf, nome, sobrenome, stakeholder }),
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
    const params = new URLSearchParams(Array.from(searchParams.entries()));

    const data = new FormData(e.currentTarget);
    const query = data.get('query')?.toString();

    if (query) {
      if (searchType === 'oab') {
        params.set('oab', query);
      }

      if (searchType === 'cpf') {
        params.set('cpf', query);
      }

      if (searchType === 'nome') {
        params.set('nome', query);
      }

      if (searchType === 'sobrenome') {
        params.set('sobrenome', query);
      }

      router.replace(`${pathname}?${params.toString()}`);
    }

    e.currentTarget.reset();
  }

  function handleSearchLawyerByStakeholder(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const params = new URLSearchParams(Array.from(searchParams.entries()));

    const data = new FormData(e.currentTarget);
    const documento = data.get('documento')?.toString();

    if (documento) {
      params.set('stakeholder', documento);
    }

    router.replace(`${pathname}?${params.toString()}`);

    e.currentTarget.reset();
  }

  function handleClearFilters() {
    const params = new URLSearchParams(Array.from(searchParams.entries()));

    params.delete('oab');
    params.delete('cpf');
    params.delete('nome');
    params.delete('sobrenome');
    params.delete('stakeholder');
    params.delete('page');
    params.delete('size');

    router.replace(`${pathname}?${params.toString()}`);
  }

  return (
    <main className="relative mx-auto min-h-screen w-full max-w-[1200px] pb-16 pt-28">
      <div className="space-y-4 px-4">
        <h1 className="text-3xl font-semibold">Advogados</h1>

        <div className="flex items-start justify-between">
          <div className="flex items-start gap-2">
            {/* search lawyers by oab, cnpj */}
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
                  defaultValue="oab"
                  value={searchType}
                  onChange={handleSelectChange}
                >
                  <option value="oab">OAB</option>
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

            <form
              onSubmit={handleSearchLawyerByStakeholder}
              className="flex w-full flex-col gap-1"
            >
              <Input
                name="documento"
                placeholder="Digite o CNPJ ou CPF"
                minLength={11}
                maxLength={15}
                // onChange={(e) => {
                //   const formattedValue = formatCpfCnpj(e.target.value)
                //   e.target.value = formattedValue
                // }}
              />
              <span className="text-xs text-muted-foreground">
                Encontre advogados que atenda a um stakeholder
              </span>
            </form>
          </div>

          <div className="flex items-center gap-2">
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

        {data && <DataTable columns={columns} data={data.advogados} />}

        {!isLoading && !data && (
          <p className="py-4 text-muted-foreground">
            Não foi possível encontrar sua busca...
          </p>
        )}

        {data?.advogados && (
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
