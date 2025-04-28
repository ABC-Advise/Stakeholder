'use client'

import { ColumnDef } from '@tanstack/react-table'

import { MoreHorizontal } from 'lucide-react'

import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Checkbox } from '@/components/ui/checkbox'
import { EditProjetoDialog } from './edit-projeto-dialog'
import { ProjetoDetailsDialog } from './details-projeto-dialog'

export type Projeto = {
  projeto_id: number
  nome: string
  descricao: string
  data_inicio: string
  data_fim: string
}

export const columns: ColumnDef<Projeto>[] = [
  {
    accessorKey: 'nome',
    header: 'Nome do projeto',
    cell: ({ row }) => (
      <div className="font-semibold capitalize">{row.getValue('nome')}</div>
    ),
  },
  {
    accessorKey: 'descricao',
    header: 'Descrição',
    cell: ({ row }) => (
      <div className="font-semibold capitalize">
        {row.getValue('descricao')}
      </div>
    ),
  },
  {
    accessorKey: 'data_inicio',
    header: 'Data de início',
    cell: ({ row }) => (
      <div className="capitalize">{row.getValue('data_inicio')}</div>
    ),
  },
  {
    accessorKey: 'data_fim',
    header: 'Data de término',
    cell: ({ row }) => (
      <div className="capitalize">{row.getValue('data_fim')}</div>
    ),
  },
  {
    id: 'actions',
    enableHiding: false,
    cell: ({ row }) => {
      const projeto = row.original

      return (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="h-8 w-8 p-0">
              <span className="sr-only">Open menu</span>
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem asChild>
              <ProjetoDetailsDialog projeto={projeto} />
            </DropdownMenuItem>

            <DropdownMenuItem asChild>
              <EditProjetoDialog projeto={projeto} />
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      )
    },
  },
]
