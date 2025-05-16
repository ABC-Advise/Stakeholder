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

import { DeletePessoaDialog } from './delete-pessoa-dialog';
import { EditPessoaDialog } from './edit-pessoa-dialog';
import { PessoaDetailsDialog } from './pessoa-details-dialog';

export type Pessoa = {
  pessoa_id: number;
  firstname: string;
  lastname: string;
  cpf: string;
  linkedin: string;
  instagram: string;
  stakeholder: boolean;
  em_prospecao: boolean;
  pep: boolean;
  sexo: string;
  data_nascimento: string;
  nome_mae: string;
  idade: number;
  signo: string;
  obito: boolean;
  data_obito: string;
  renda_estimada: string;
  projeto_id: number;
};

export const columns: ColumnDef<Pessoa>[] = [
  {
    id: 'select',
    header: ({ table }) => (
      <Checkbox
        checked={
          table.getIsAllPageRowsSelected() ||
          (table.getIsSomePageRowsSelected() && 'indeterminate')
        }
        onCheckedChange={value => table.toggleAllPageRowsSelected(!!value)}
        aria-label="Select all"
      />
    ),
    cell: ({ row }) => (
      <Checkbox
        checked={row.getIsSelected()}
        onCheckedChange={value => row.toggleSelected(!!value)}
        aria-label="Select row"
      />
    ),
    enableSorting: false,
    enableHiding: false,
  },
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
    cell: ({ row }) => <div className="capitalize">{row.getValue('cpf')}</div>,
  },
  {
    id: 'actions',
    enableHiding: false,
    cell: ({ row }) => {
      const pessoa = row.original;

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
              <PessoaDetailsDialog pessoa={pessoa} />
            </DropdownMenuItem>

            <DropdownMenuItem asChild>
              <EditPessoaDialog pessoa={pessoa} />
            </DropdownMenuItem>

            <DropdownMenuSeparator />

            <DropdownMenuItem asChild>
              <DeletePessoaDialog pessoa={pessoa} />
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      );
    },
  },
];
