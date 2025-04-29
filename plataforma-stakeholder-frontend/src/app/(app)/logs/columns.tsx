'use client'

import { ColumnDef } from '@tanstack/react-table'

import { ConsultDetailsDialog } from './consult-details-dialog'
import { Consulta } from '@/http/consult/get-all-consult'

export const columns: ColumnDef<Consulta>[] = [
  {
    accessorKey: 'consulta_id',
    header: '',
    cell: ({ row }) => <ConsultDetailsDialog data={row.original} />,
  },
  {
    accessorKey: 'documento',
    header: 'Documento',
    cell: ({ row }) => (
      <div className="truncate capitalize">{row.getValue('documento')}</div>
    ),
  },
  {
    accessorKey: 'data_consulta',
    header: 'Realizado há',
    cell: ({ row }) => (
      <div className="text-muted-foreground">
        {row.getValue('data_consulta')}
      </div>
    ),
  },
  {
    accessorKey: 'status',
    header: 'Status',
    cell: ({ row }) => (
      <div className="flex items-center gap-1">
        <div
          className={`flex h-6 items-center justify-center rounded-md p-2 text-sm font-medium ${row.original.status === 'Finalizado' ? 'bg-green-500/10 text-green-600' : 'bg-amber-500/10 text-amber-600'}`}
        >
          {row.getValue('status')}
        </div>
      </div>
    ),
  },
  {
    accessorKey: 'is_cnpj',
    header: 'Tipo',
    cell: ({ row }) => (
      <div className="flex items-center gap-1">
        {row.getValue('is_cnpj') ? (
          <div className="flex h-6 items-center justify-center rounded-md bg-sky-500/10 p-2 font-medium text-sky-700">
            Empresa
          </div>
        ) : (
          <div className="flex h-6 items-center justify-center rounded-md bg-green-500/10 p-2 font-medium text-green-600">
            Pessoa
          </div>
        )}
      </div>
    ),
  },
]
