'use client';

import { DropdownMenuCheckboxItemProps } from '@radix-ui/react-dropdown-menu';
import { useQuery } from '@tanstack/react-query';
import { FilterX, ListFilter, Search } from 'lucide-react';
import { useSearchParams, useRouter, usePathname } from 'next/navigation';
import { useState } from 'react';
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
import { getOffices } from '@/http/offices/get-offices';

import { columns } from './columns';
import { DataTable } from './data-table';
import { DataTableSkeleton } from './data-table-skeleton';

type Checked = DropdownMenuCheckboxItemProps['checked'];

export default function OfficesPage() {
  const searchParams = useSearchParams();
  const pathname = usePathname();
  const router = useRouter();

  const [isOpenCreateStakeholder, setIsOpenCreateStakeholder] = useState(false);

  const [showClients, setShowClients] = useState<Checked>(true);
  const [showProspect, setShowProspect] = useState<Checked>(false);

  const page = z.coerce
    .number()
    .transform(page => page)
    .parse(searchParams.get('page') ?? '1');

  const size = z.coerce
    .number()
    .transform(size => size)
    .parse(searchParams.get('size') ?? '10');

  const { data, isLoading } = useQuery({
    queryKey: ['offices', page, size],
    queryFn: () => getOffices({ page, size }),
  });

  function handlePaginate(page: number) {
    const params = new URLSearchParams(Array.from(searchParams.entries()));

    params.set('page', (page + 1).toString());

    router.replace(`${pathname}?${params.toString()}`);
  }

  return (
    <main className="relative mx-auto min-h-screen w-full max-w-[1200px] pb-16 pt-28">
      <div className="space-y-4 px-4">
        <h1 className="text-3xl font-semibold">Escritórios</h1>

        <div className="flex items-center justify-between">
          <form className="relative w-full max-w-xs">
            <Input
              placeholder="Buscar por documento..."
              className="-me-px h-9 pl-9"
            />

            <div className="pointer-events-none absolute inset-y-0 start-0 flex items-center justify-center ps-3 text-muted-foreground/80 peer-disabled:opacity-50">
              <Search size={16} strokeWidth={2} />
            </div>
          </form>

          <div className="flex items-center gap-2">
            <Button title="Limpar filtros" variant="outline">
              <FilterX className="size-4" />
              <span className="sr-only">Limpar filtros</span>
            </Button>
          </div>
        </div>
        {data && <DataTable columns={columns} data={data.escritorios} />}

        {!isLoading && !data && (
          <p className="py-4 text-muted-foreground">
            Não foi possível encontrar sua busca...
          </p>
        )}

        {data?.escritorios && (
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
