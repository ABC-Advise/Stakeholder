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

import { getProjetos } from '@/http/projetos/get-projetos'
import { CreateProjetoDialog } from './create-projeto-dialog'

export default function ProjetoPage() {
  const [isOpenCreateStakeholder, setIsOpenCreateStakeholder] = useState(false)
  const searchParams = useSearchParams()

  const [searchType, setSearchType] = useState('cpf')

  const pathname = usePathname()
  const router = useRouter()

  const page = z.coerce
    .number()
    .transform((page) => page)
    .parse(searchParams.get('page') ?? '1')

  const size = z.coerce
    .number()
    .transform((size) => size)
    .parse(searchParams.get('size') ?? '10')

  const { data, isLoading } = useQuery({
    queryKey: ['projetos', page, size],
    queryFn: () =>
      getProjetos({
        page,
        size,
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

  // function handleFilter(e: FormEvent<HTMLFormElement>) {
  //   e.preventDefault()

  //   const data = new FormData(e.currentTarget)
  //   const query = data.get('query')?.toString()

  //   const params = new URLSearchParams(Array.from(searchParams.entries()))

  //   if (query) {
  //     if (searchType === 'cpf') {
  //       params.set('cpf', query)
  //     }

  //     if (searchType === 'nome') {
  //       params.set('nome', query)
  //     }

  //     if (searchType === 'sobrenome') {
  //       params.set('sobrenome', query)
  //     }

  //     router.replace(`${pathname}?${params.toString()}`)
  //   }

  //   e.currentTarget.reset()
  // }

  function handleClearFilters() {
    const params = new URLSearchParams(Array.from(searchParams.entries()))
    params.delete('page')
    params.delete('size')

    router.replace(`${pathname}?${params.toString()}`)
  }

  return (
    <main className="relative mx-auto min-h-screen w-full max-w-[1200px] pb-16 pt-28">
      <div className="space-y-4 px-4">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-semibold">Projetos</h1>

          <div className="flex items-center gap-2">
            <Button
              onClick={() => setIsOpenCreateStakeholder(true)}
              type="button"
              size="sm"
            >
              <Plus className="mr-2 size-4" />
              Adicionar
            </Button>

            <CreateProjetoDialog
              isOpen={isOpenCreateStakeholder}
              setIsOpen={setIsOpenCreateStakeholder}
            />
          </div>
        </div>

        <div className="flex items-end justify-end">
          <Button
            title="Limpar filtros"
            variant="outline"
            onClick={handleClearFilters}
          >
            <FilterX className="size-4" />
            <span className="sr-only">Limpar filtros</span>
          </Button>
        </div>

        {data && <DataTable columns={columns} data={data.projetos} />}

        {data?.projetos && (
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
