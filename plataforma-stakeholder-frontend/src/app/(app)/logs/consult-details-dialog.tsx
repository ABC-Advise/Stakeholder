'use client';

import { useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Check,
  ChevronDown,
  CircleDashed,
  Loader2,
  Search,
} from 'lucide-react';
import { useEffect, useState } from 'react';

import { Button } from '@/components/ui/button';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useToast } from '@/hooks/use-toast';
import { Consulta } from '@/http/consult/get-all-consult';
import { getLogsById, Log as LogProps } from '@/http/logs/get-logs-by-id';
import { cn } from '@/lib/utils';

import { Log } from './_components/log';

export type ConsultDetailsDialogProps = {
  data: Consulta;
};

export function ConsultDetailsDialog({ data }: ConsultDetailsDialogProps) {
  const [isOpen, setIsOpen] = useState(false);

  const [page, setPage] = useState<number>(1);
  const [size, setSize] = useState<number>(20);

  const [logs, setLogs] = useState<LogProps[]>([]);

  const { data: result, isLoading } = useQuery({
    queryKey: ['logs', data.consulta_id],
    queryFn: () => getLogsById({ consulta_id: data.consulta_id, page, size }),
    enabled: isOpen,
  });

  useEffect(() => {
    if (result && result.logs) {
      if (page === 1) {
        setLogs(result.logs);
      } else {
        setLogs(prev => [...prev, ...result.logs]);
      }
    }
  }, [result, page]);

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button
          variant="outline"
          className="size-9"
          onClick={() => setIsOpen(prev => !prev)}
        >
          <Search />
        </Button>
      </DialogTrigger>

      <DialogContent className="w-full max-w-3xl">
        <DialogHeader>
          <DialogTitle>Detalhes da consulta</DialogTitle>
          <DialogDescription>
            Visualizar informações e histórico.
          </DialogDescription>
        </DialogHeader>

        <div className="flex flex-col gap-4 p-2">
          <div className="flex items-center justify-between gap-2">
            <p className="text-sm font-medium">ID do registro</p>
            <p className="text-sm text-zinc-500">{data.consulta_id}</p>
          </div>
          <div className="flex items-center justify-between gap-2">
            <p className="text-sm font-medium">Documento</p>
            <p className="text-sm text-zinc-500">{data.documento}</p>
          </div>
          <div className="flex items-center justify-between gap-2">
            <p className="text-sm font-medium">Tipo</p>
            {data.is_cnpj ? (
              <div className="flex h-6 items-center justify-center rounded-md bg-sky-500/10 p-2 text-sm font-medium text-sky-700">
                Empresa
              </div>
            ) : (
              <div className="flex h-6 items-center justify-center rounded-md bg-green-500/10 p-2 text-sm font-medium text-green-600">
                Pessoa
              </div>
            )}
          </div>
          <div className="flex items-center justify-between gap-2">
            <p className="text-sm font-medium">Data</p>
            <p className="text-sm text-zinc-500">{data.data_consulta}</p>
          </div>
        </div>

        {logs && (
          <Collapsible className="flex flex-col rounded-lg border">
            <CollapsibleTrigger
              className="group flex w-full items-center justify-between bg-zinc-50 p-4 disabled:cursor-not-allowed disabled:opacity-70"
              disabled={data.status !== 'Finalizado'}
            >
              <div className="flex items-center gap-2">
                <ChevronDown className="size-4 transition-transform duration-300 group-data-[state=closed]:-rotate-90" />
                <p className="text-sm font-medium">Histórico de logs</p>
              </div>

              <div className="flex items-center gap-2">
                {data.status === 'Finalizado' ? (
                  <span className="text-sm text-muted-foreground">
                    Finalizado
                  </span>
                ) : (
                  <span className="text-sm text-muted-foreground">
                    Pendente
                  </span>
                )}

                <div
                  className={cn(
                    'flex size-5 items-center justify-center rounded-full',
                    data.status === 'Finalizado' && 'bg-emerald-500'
                  )}
                >
                  {data.status === 'Finalizado' ? (
                    <Check className="size-3.5 text-white" strokeWidth={3} />
                  ) : (
                    <CircleDashed className="size-3.5 animate-spin" />
                  )}
                </div>
              </div>
            </CollapsibleTrigger>

            {/* Animação suave para abertura/fechamento */}
            <CollapsibleContent className="overflow-hidden border-t transition-all duration-300 data-[state=closed]:animate-collapsible-up data-[state=open]:animate-collapsible-down">
              <ScrollArea className="h-72 w-full">
                <div className="flex h-72 flex-col justify-between">
                  {logs.map((log, index) => (
                    <Log key={`${log.log_consulta_id} - ${index}`} data={log} />
                  ))}

                  {logs && logs.length === 0 && (
                    <span className="p-4 text-center text-sm text-muted-foreground">
                      Nenhum log foi registrado.
                    </span>
                  )}

                  {logs.length > 0 && (
                    <button
                      type="button"
                      className="mt-auto flex h-8 shrink-0 items-center justify-center gap-2 border-t bg-muted hover:opacity-80"
                      onClick={() => setPage(prev => prev + 1)}
                      disabled={isLoading}
                    >
                      {isLoading && <Loader2 className="size-4 animate-spin" />}
                      <span className="text-sm">Ver mais</span>
                    </button>
                  )}
                </div>
              </ScrollArea>
            </CollapsibleContent>
          </Collapsible>
        )}

        {isLoading && !result && (
          <div className="flex h-20 items-center justify-center">
            <Loader2 className="size-4 animate-spin" />
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
