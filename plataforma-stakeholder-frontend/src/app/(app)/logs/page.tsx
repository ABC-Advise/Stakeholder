'use client'

import { usePathname, useRouter, useSearchParams } from 'next/navigation'
import { z } from 'zod'

import { ArrowDownUp, FilterX, RefreshCw, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { DataTable } from './data-table'
import { columns } from './columns'
import { Pagination } from '@/components/pagination'
import { DateRangePicker } from '@/components/date-picker'
import { useState } from 'react'
import { DateRange } from 'react-day-picker'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useQuery } from '@tanstack/react-query'
import { getAllConsult } from '@/http/consult/get-all-consult'
import { DataTableSkeleton } from './data-table-skeleton'

export default function LawyersPage() {
  const searchParams = useSearchParams()

  const pathname = usePathname()
  const router = useRouter()

  const [oldFirst, setOldFirst] = useState<boolean | null>(null)
  const [dateRange, setDateRange] = useState<DateRange | undefined>()

  const [isRefreshing, setIsRefreshing] = useState(false) // estado de loading para refresh da tabela

  const page = z.coerce
    .number()
    .transform((page) => page)
    .parse(searchParams.get('page') ?? '1')

  const size = z.coerce
    .number()
    .transform((size) => size)
    .parse(searchParams.get('size') ?? '10')

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['consult', page, size, dateRange, oldFirst],
    queryFn: () =>
      getAllConsult({
        page,
        size,
        antigo_primeiro: oldFirst || null,
        data_inicio: dateRange?.from?.toISOString().split('T')[0],
        data_fim: dateRange?.to?.toISOString().split('T')[0], // transforma data para => 2025-01-01
      }),
    staleTime: 1000 * 60 * 5, // 5 minutes
    refetchInterval: 1000 * 60 * 15, // 15 minutes
  })

  function handlePaginate(page: number) {
    const params = new URLSearchParams(Array.from(searchParams.entries()))

    params.set('page', (page + 1).toString())

    router.replace(`${pathname}?${params.toString()}`)
  }

  function handleClearFilters() {
    const params = new URLSearchParams(Array.from(searchParams.entries()))

    params.delete('page')
    params.delete('size')

    setDateRange(undefined)
    setOldFirst(null)

    router.replace(`${pathname}?${params.toString()}`)
  }

  const handleRefresh = async () => {
    setIsRefreshing(true)
    await new Promise((resolve) => setTimeout(resolve, 500)) // delay de 500ms para animação de loading
    await refetch()
    setIsRefreshing(false)
  }

  return (
    <main className="relative mx-auto min-h-screen w-full max-w-[1200px] pb-16 pt-28">
      <div className="space-y-4 px-4">
        <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-center">
          <div className="flex items-start gap-2">
            <h1 className="text-2xl font-semibold">Consultas</h1>
          </div>

          <div className="flex flex-col gap-2 lg:flex-row lg:items-center">
            <Select>
              <SelectTrigger className="h-10 w-full md:w-[200px]">
                <SelectValue placeholder="Selecione um tipo" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="empresa">Empresa</SelectItem>
                <SelectItem value="pessoa">Pessoa</SelectItem>
              </SelectContent>
            </Select>

            <DateRangePicker date={dateRange} onDateChange={setDateRange} />

            <Button
              variant="outline"
              size="icon"
              onClick={() => setOldFirst(!oldFirst)}
            >
              <ArrowDownUp className="size-4" />
            </Button>

            <Button
              variant="outline"
              onClick={handleRefresh}
              disabled={isRefreshing}
            >
              <RefreshCw
                className={`size-4 ${isRefreshing && 'animate-spin'}`}
              />
              Atualizar
            </Button>
            <Button variant="outline" size="icon" onClick={handleClearFilters}>
              <FilterX className="size-4" />
              <span className="sr-only">Remover filtros</span>
            </Button>
          </div>
        </div>

        {data && <DataTable columns={columns} data={data.consultas} />}

        {!isLoading && !data && (
          <p className="py-4 text-muted-foreground">
            Não foi possível encontrar sua busca...
          </p>
        )}

        {data?.consultas && (
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
