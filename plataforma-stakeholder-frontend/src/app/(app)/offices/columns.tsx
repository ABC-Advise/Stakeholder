'use client';

import { ColumnDef } from '@tanstack/react-table';
import { ArrowUpDown, MoreHorizontal } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

import { DeleteOfficeDialog } from './delete-office-dialog';
import { EditOfficeDialog } from './edit-office-dialog';
import { OfficeDetailsDialog } from './office-details-dialog';

export type Office = {
  escritorio_id: number;
  razao_social: string;
  nome_fantasia: string;
  linkedin: string;
  instagram: string;
};

export const columns: ColumnDef<Office>[] = [
  {
    accessorKey: 'nome_fantasia',
    header: 'Nome fantasia',
    cell: ({ row }) => (
      <div className="font-semibold capitalize">
        {row.getValue('nome_fantasia')}
      </div>
    ),
  },
  {
    accessorKey: 'razao_social',
    header: 'Razão Social',
    cell: ({ row }) => (
      <div className="capitalize">{row.getValue('razao_social')}</div>
    ),
  },
  {
    id: 'actions',
    enableHiding: false,
    cell: ({ row }) => {
      const office = row.original;

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
              <OfficeDetailsDialog office={office} />
            </DropdownMenuItem>

            <DropdownMenuItem asChild>
              <EditOfficeDialog office={office} />
            </DropdownMenuItem>

            <DropdownMenuSeparator />

            <DropdownMenuItem asChild>
              <DeleteOfficeDialog office={office} />
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      );
    },
  },
];
