'use client'

import { ColumnDef } from '@tanstack/react-table'

import { MoreHorizontal } from 'lucide-react'

import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Checkbox } from '@/components/ui/checkbox'
import { EditLawyerDialog } from './edit-lawyer-dialog'
import { LawyerDetailsDialog } from './lawyer-details-dialog'
import { DeleteLawyerDialog } from './delete-lawyer-dialog'

export type Lawyer = {
  advogado_id: number
  firstname: string
  lastname: string
  oab: string
  cpf: string
  linkedin: string
  instagram: string
}

export const columns: ColumnDef<Lawyer>[] = [
  {
    accessorKey: 'firstname',
    header: 'Primeiro nome',
    cell: ({ row }) => (
      <div className="font-semibold capitalize">
        {row.getValue('firstname')}
      </div>
    ),
  },
  {
    accessorKey: 'lastname',
    header: 'Último nome',
    cell: ({ row }) => (
      <div className="font-semibold capitalize">{row.getValue('lastname')}</div>
    ),
  },
  {
    accessorKey: 'cpf',
    header: 'CPF',
    cell: ({ row }) => (
      <div className="capitalize">
        {row.getValue('cpf') !== 'None' ? row.getValue('cpf') : 'Não informado'}
      </div>
    ),
  },
  {
    accessorKey: 'oab',
    header: 'OAB',
    cell: ({ row }) => <div className="capitalize">{row.getValue('oab')}</div>,
  },
  {
    id: 'actions',
    enableHiding: false,
    cell: ({ row }) => {
      const lawyer = row.original

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
              <LawyerDetailsDialog lawyer={lawyer} />
            </DropdownMenuItem>

            <DropdownMenuItem asChild>
              <EditLawyerDialog lawyer={lawyer} />
            </DropdownMenuItem>

            <DropdownMenuSeparator />

            <DropdownMenuItem asChild>
              <DeleteLawyerDialog lawyer={lawyer} />
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      )
    },
  },
]
