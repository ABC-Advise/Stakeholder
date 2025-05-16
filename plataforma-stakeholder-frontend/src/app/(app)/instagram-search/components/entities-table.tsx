'use client';

import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  SortingState,
  useReactTable,
  VisibilityState,
  ColumnFiltersState,
} from '@tanstack/react-table';
import { Search, Loader2, ChevronDown } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useState } from 'react';

import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

import { type Entidade } from '../services/api';

interface EntitiesTableProps {
  data: Entidade[];
  onSearchIndividual: (entidade: Entidade) => Promise<void>; // Recebe a entidade inteira
  isLoading: boolean;
  tipo?: 'empresa' | 'pessoa' | 'advogado'; // nova prop
}

export function EntitiesTable({
  data,
  onSearchIndividual,
  isLoading,
  tipo,
}: EntitiesTableProps) {
  const router = useRouter();
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({});
  const [rowSelection, setRowSelection] = useState({});
  const [internalLoading, setInternalLoading] = useState<
    Record<string, boolean>
  >({}); // Loading por linha

  const handleSearchClick = async (entidade: Entidade) => {
    setInternalLoading(prev => ({ ...prev, [entidade.id]: true }));
    await onSearchIndividual(entidade);
    setInternalLoading(prev => ({ ...prev, [entidade.id]: false }));
    // Navega para a página de resultados APÓS iniciar a busca
    // Idealmente, a API de busca individual retornaria algo para indicar
    // que a busca começou e talvez até um link para os resultados.
    // Por agora, apenas navegamos.
    router.push(`/instagram-search/${entidade.tipo}/${entidade.id}`);
  };

  const columns: ColumnDef<Entidade>[] = [
    {
      accessorKey: 'nome',
      header: 'Nome/Razão Social',
      cell: ({ row }) => (
        <div className="font-medium">{row.getValue('nome')}</div>
      ),
    },
    {
      accessorKey: 'tipo',
      header: 'Tipo',
      cell: ({ row }) => (
        <div className="capitalize">{row.getValue('tipo')}</div>
      ),
      filterFn: (row, id, value) =>
        value === 'todos' || value === row.getValue(id),
    },
    {
      id: 'statusInstagramManual',
      header: 'Status Instagram',
      cell: ({ row }) => {
        const entidade = row.original as Entidade;
        const status =
          entidade.instagram && entidade.instagram.trim() !== ''
            ? 'Atribuído'
            : 'Não atribuído';
        const colorClass =
          status === 'Atribuído'
            ? 'bg-green-100 text-green-800'
            : 'bg-red-100 text-red-800';
        return (
          <span
            className={`px-2 py-1 rounded-full text-xs font-medium ${colorClass}`}
          >
            {status}
          </span>
        );
      },
    },
    {
      id: 'identificadorPrincipal',
      header:
        tipo === 'empresa'
          ? 'CNPJ'
          : tipo === 'pessoa'
            ? 'CPF'
            : tipo === 'advogado'
              ? 'OAB'
              : 'CNPJ/CPF/OAB',
      cell: ({ row }) => {
        const entidade = row.original as Entidade;
        if (tipo === 'empresa') return entidade.cnpj || '-';
        if (tipo === 'pessoa') return entidade.cpf || '-';
        if (tipo === 'advogado') return entidade.oab || '-';
        return '-';
      },
    },
    {
      id: 'actions',
      cell: ({ row }) => {
        const entidade = row.original;
        const isRowLoading = internalLoading[entidade.id] || false;
        // Função para redirecionar para busca por identificador
        const handleRedirectByIdentifier = () => {
          let tipoEntidade = (tipo || '').trim();
          let identifier = '';
          if (tipoEntidade === 'empresa')
            identifier = (entidade.cnpj || '').trim();
          else if (tipoEntidade === 'pessoa')
            identifier = (entidade.cpf || '').trim();
          else if (tipoEntidade === 'advogado')
            identifier = (entidade.cpf || entidade.oab || '').trim();
          if (!identifier) return;
          // Redireciona para a rota de busca por identificador
          router.push(`/instagram-search/${tipoEntidade}/${identifier}`);
        };
        return (
          <Button
            variant="outline"
            size="sm"
            onClick={handleRedirectByIdentifier}
            disabled={isRowLoading}
            className="flex items-center"
          >
            <Search className="mr-2 h-4 w-4" />
            Buscar
          </Button>
        );
      },
    },
  ];

  const table = useReactTable({
    data,
    columns,
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    onColumnVisibilityChange: setColumnVisibility,
    onRowSelectionChange: setRowSelection,
    state: {
      sorting,
      columnFilters,
      columnVisibility,
      rowSelection,
    },
    initialState: {
      pagination: {
        pageSize: 10, // Define o tamanho da página padrão
      },
    },
  });

  if (isLoading) {
    return (
      <div className="rounded-md border p-4">
        <div className="h-10 bg-gray-200 rounded mb-4 animate-pulse w-1/2"></div>{' '}
        {/* Placeholder for filters */}
        <div className="space-y-2">
          {[...Array(5)].map((_, i) => (
            <div
              key={i}
              className="h-12 bg-gray-200 rounded animate-pulse"
            ></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="w-full">
      {/* Filtros */}
      <div className="flex items-center py-4 gap-2 flex-wrap">
        <Input
          placeholder="Filtrar por nome..."
          value={(table.getColumn('nome')?.getFilterValue() as string) ?? ''}
          onChange={event =>
            table.getColumn('nome')?.setFilterValue(event.target.value)
          }
          className="max-w-sm"
        />
        <Select
          value={
            (table.getColumn('tipo')?.getFilterValue() as string) ?? 'todos'
          }
          onValueChange={value =>
            table.getColumn('tipo')?.setFilterValue(value)
          }
        >
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Filtrar por tipo" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="todos">Todos os Tipos</SelectItem>
            <SelectItem value="empresa">Empresa</SelectItem>
            <SelectItem value="pessoa">Pessoa</SelectItem>
            <SelectItem value="advogado">Advogado</SelectItem>
          </SelectContent>
        </Select>
        <Select
          value={
            (table
              .getColumn('statusInstagramManual')
              ?.getFilterValue() as string) ?? 'todos'
          }
          onValueChange={value =>
            table.getColumn('statusInstagramManual')?.setFilterValue(value)
          }
        >
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="Filtrar por status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="todos">Todos os Status</SelectItem>
            <SelectItem value="Atribuído">Atribuído</SelectItem>
            <SelectItem value="Não atribuído">Não atribuído</SelectItem>
          </SelectContent>
        </Select>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" className="ml-auto">
              Colunas <ChevronDown className="ml-2 h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            {table
              .getAllColumns()
              .filter(column => column.getCanHide())
              .map(column => {
                return (
                  <DropdownMenuCheckboxItem
                    key={column.id}
                    className="capitalize"
                    checked={column.getIsVisible()}
                    onCheckedChange={value => column.toggleVisibility(!!value)}
                  >
                    {column.id === 'ultimaBusca' ? 'Última Busca' : column.id}{' '}
                    {/* Melhorar exibição nome coluna */}
                  </DropdownMenuCheckboxItem>
                );
              })}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
      {/* Tabela */}
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map(headerGroup => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map(header => {
                  return (
                    <TableHead key={header.id}>
                      {header.isPlaceholder
                        ? null
                        : flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                    </TableHead>
                  );
                })}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map(row => (
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && 'selected'}
                >
                  {row.getVisibleCells().map(cell => (
                    <TableCell key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center"
                >
                  Nenhum resultado encontrado.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      {/* Paginação */}
      <div className="flex items-center justify-end space-x-2 py-4">
        <div className="flex-1 text-sm text-muted-foreground">
          {table.getFilteredRowModel().rows.length} linha(s) encontrada(s).
        </div>
        <div className="space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            Anterior
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            Próxima
          </Button>
        </div>
      </div>
    </div>
  );
}
