'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { z, ZodType } from 'zod';

import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { getProjetos } from '@/http/projetos/get-projetos';

import { Projeto } from './columns';
import { ProjetoSkeletonDialog } from './projeto-skeleton-dialog';

interface ProjetoDetailsDialogProps {
  projeto: Projeto;
}

const updateFormSchema = z.object({
  nome: z.string(),
  descricao: z.string(),
  data_inicio: z.string(),
  data_fim: z.string(),
});

type UpdateFormSchema = z.infer<typeof updateFormSchema>;

export function ProjetoDetailsDialog({ projeto }: ProjetoDetailsDialogProps) {
  const [isOpen, setIsOpen] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ['projetos', projeto.projeto_id],
    queryFn: () => getProjetos({ projeto_id: projeto.projeto_id }),
    enabled: isOpen,
  });

  const { control, register } = useForm<UpdateFormSchema>({
    resolver: zodResolver(updateFormSchema as unknown as ZodType<any>),
    defaultValues: {
      nome: projeto.nome,
      descricao: projeto.descricao,
      data_inicio: projeto.data_inicio,
      data_fim: projeto.data_fim,
    },
  });

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="ghost" size="sm" className="w-full justify-start">
          Visualizar
        </Button>
      </DialogTrigger>

      <DialogContent>
        {data &&
          data.projetos.map(projeto => {
            return (
              <form key={projeto.projeto_id}>
                <DialogHeader>
                  <DialogTitle>Visualizar {projeto.nome}</DialogTitle>
                  <DialogDescription>Detalhes do projeto</DialogDescription>
                </DialogHeader>
                <div className="my-4 space-y-4">
                  <div className="space-y-1">
                    <Label>Nome do projeto</Label>
                    <Input {...register('nome')} disabled />
                  </div>

                  <div className="space-y-1">
                    <Label>Descrição do projeto</Label>
                    <Textarea {...register('descricao')} disabled />
                  </div>

                  <div className="flex flex-col gap-1">
                    <Label htmlFor="startDate">Data de início</Label>
                    <input
                      type="date"
                      id="startDate"
                      {...register('data_inicio')}
                      disabled
                      className="rounded border p-2 text-muted-foreground"
                    />
                  </div>

                  <div className="flex flex-col gap-1">
                    <Label htmlFor="endDate">Data de término</Label>
                    <input
                      type="date"
                      id="endDate"
                      {...register('data_fim')}
                      disabled
                      className="rounded-md border p-2 text-muted-foreground"
                    />
                  </div>
                </div>

                <DialogFooter className="flex w-full justify-end">
                  <DialogClose asChild>
                    <Button type="button" className="w-1/2">
                      Fechar
                    </Button>
                  </DialogClose>
                </DialogFooter>
              </form>
            );
          })}

        {isLoading && <ProjetoSkeletonDialog />}
      </DialogContent>
    </Dialog>
  );
}
