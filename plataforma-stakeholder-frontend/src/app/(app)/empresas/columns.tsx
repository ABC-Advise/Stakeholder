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

import { DeleteEmpresaDialog } from './delete-empresa-dialog';
import { EditEmpresaDialog } from './edit-empresa-dialog';
import { EmpresaDetailsDialog } from './empresa-details-dialog';

export type Empresa = {
  empresa_id: number;
  cnpj: string;
  razao_social: string;
  nome_fantasia: string;
  data_fundacao: string;
  quantidade_funcionarios: string;
  situacao_cadastral: string;
  codigo_natureza_juridica: string;
  natureza_juridica_descricao: string;
  natureza_juridica_tipo: string;
  faixa_funcionarios: string;
  faixa_faturamento: string;
  matriz: string;
  orgao_publico: string;
  ramo: string;
  tipo_empresa: string;
  ultima_atualizacao_pj: string;
  porte_id: number;
  segmento_id: number;
  linkedin: string;
  instagram: string;
  stakeholder: boolean;
  em_prospecao: boolean;
  projeto_id: string;
  projeto: any;
  cnae: string;
  descricao_cnae: string;
  porte: string;
  segmento: string;
};

export const columns: ColumnDef<Empresa>[] = [
  {
    accessorKey: 'razao_social',
    header: 'Razão Social',
    cell: ({ row }) => (
      <div className="font-semibold capitalize">
        {row.getValue('razao_social')}
      </div>
    ),
  },
  {
    accessorKey: 'nome_fantasia',
    header: 'Nome Fantasia',
    cell: ({ row }) => (
      <div className="font-semibold capitalize">
        {row.getValue('nome_fantasia')}
      </div>
    ),
  },
  {
    accessorKey: 'cnpj',
    header: 'CNPJ',
    cell: ({ row }) => <div className="capitalize">{row.getValue('cnpj')}</div>,
  },
  {
    id: 'actions',
    enableHiding: false,
    cell: ({ row }) => {
      const empresa = row.original;

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
              <EmpresaDetailsDialog empresa={empresa} />
            </DropdownMenuItem>

            <DropdownMenuItem asChild>
              <EditEmpresaDialog empresa={empresa} />
            </DropdownMenuItem>

            <DropdownMenuSeparator />

            <DropdownMenuItem asChild>
              <DeleteEmpresaDialog empresa={empresa} />
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      );
    },
  },
];
