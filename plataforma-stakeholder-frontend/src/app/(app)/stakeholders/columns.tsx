'use client';

import { ColumnDef } from '@tanstack/react-table';
import { MoreHorizontal } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

import { DeleteStakeholderDialog } from './delete-stakeholder-dialog';
import { EditStakeholderDialog } from './edit-stakeholder-dialog';
import { UpdateStakeholderDialog } from './update-stakeholder-dialog';

export type Stakeholder = {
  entidade_id: number;
  document: string;
  is_CNPJ: boolean;
  nome1: string;
  nome2: string;
  porte_id: number;
  segmento_id: number;
  linkedin: string;
  instagram: string;
  stakeholder: boolean;
  em_prospecao: boolean;
  associado: boolean | null;
};

export const columns: ColumnDef<Stakeholder>[] = [
  {
    accessorKey: 'nome1',
    header: 'Razão social',
    cell: ({ row }) => (
      <div className="capitalize">{row.getValue('nome1')}</div>
    ),
  },
  {
    accessorKey: 'nome2',
    header: 'Nome fantasia',
    cell: ({ row }) => (
      <div className="capitalize">{row.getValue('nome2')}</div>
    ),
  },
  {
    accessorKey: 'document',
    header: 'Documento',
    cell: ({ row }) => (
      <div className="lowercase">{row.getValue('document')}</div>
    ),
  },
  {
    accessorKey: 'is_CNPJ',
    header: 'Tipo',
    cell: ({ row }) => {
      console.log(row.original);
      return (
        <div className="flex items-center gap-1">
          {row.getValue('is_CNPJ') ? (
            <div className="flex h-6 items-center justify-center rounded-md bg-sky-500/10 p-2 font-medium text-sky-700">
              Empresa
            </div>
          ) : (
            <div className="flex h-6 items-center justify-center rounded-md bg-green-500/10 p-2 font-medium text-green-600">
              Pessoa
            </div>
          )}

          {row.original.em_prospecao ? (
            <div className="flex h-6 items-center justify-center whitespace-nowrap rounded-md bg-amber-500/10 p-2 font-medium text-amber-600">
              Em prospecção
            </div>
          ) : null}

          {row.original.associado ? (
            <div className="flex h-6 items-center justify-center rounded-md bg-rose-500/10 p-2 font-medium text-rose-600">
              Associado
            </div>
          ) : null}
        </div>
      );
    },
  },
  {
    id: 'actions',
    enableHiding: false,
    cell: ({ row }) => {
      const data = row.original;

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
              <UpdateStakeholderDialog stakeholder={data} />
            </DropdownMenuItem>
            <DropdownMenuItem asChild>
              <EditStakeholderDialog stakeholder={data} />
            </DropdownMenuItem>

            <DropdownMenuSeparator />

            <DropdownMenuItem asChild>
              <DeleteStakeholderDialog stakeholder={data} />
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      );
    },
  },
];
