'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Loader2 } from 'lucide-react';
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
import { useToast } from '@/hooks/use-toast';
import { getProjetos } from '@/http/projetos/get-projetos';
import { updateProjeto } from '@/http/projetos/update-projeto';
import { removeNonNumeric } from '@/utils/remove-format';

import { Projeto } from './columns';
import { ProjetoSkeletonDialog } from './projeto-skeleton-dialog';

const updateFormSchema = z.object({
  nome: z.string(),
  descricao: z.string(),
  data_inicio: z.string(),
  data_fim: z.string(),
});

type UpdateFormSchema = z.infer<typeof updateFormSchema>;

interface EditProjetoDialogProps {
  projeto: Projeto;
}

export function EditProjetoDialog({ projeto }: EditProjetoDialogProps) {
  const [isOpen, setIsOpen] = useState(false);

  const { toast } = useToast();

  const queryClient = useQueryClient();

  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const { data, isLoading } = useQuery({
    queryKey: ['projetos', projeto.projeto_id],
    queryFn: () => getProjetos({ projeto_id: projeto.projeto_id }),
    enabled: isOpen,
  });

  const {
    control,
    register,
    handleSubmit,
    reset,
    formState: { isSubmitting, errors },
  } = useForm<UpdateFormSchema>({
    resolver: zodResolver(updateFormSchema as unknown as ZodType<any>),
    defaultValues: {
      nome: projeto.nome,
      descricao: projeto.descricao,
      data_inicio: projeto.data_inicio ?? '',
      data_fim: projeto.data_fim ?? '',
    },
  });

  const { mutateAsync: updateProjetoFn } = useMutation({
    mutationFn: updateProjeto,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projetos'] });
    },
  });

  async function handleUpdateProjeto(data: UpdateFormSchema) {
    try {
      console.log(data);

      await updateProjetoFn({
        projeto_id: projeto.projeto_id,
        nome: data.nome,
        descricao: data.descricao,
        data_inicio: data.data_inicio,
        data_fim: data.data_fim,
      });

      reset();

      setIsOpen(false);

      toast({
        title: 'Sucesso!',
        description: 'Projeto atualizado com sucesso!',
      });
    } catch (err) {
      console.log(err);
      toast({
        variant: 'destructive',
        title: 'Erro ao atualizar...',
        description: 'Ocorreu algum erro ao tentar atualizar!',
      });
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="ghost" size="sm" className="w-full justify-start">
          Editar
        </Button>
      </DialogTrigger>

      <DialogContent>
        {data &&
          data.projetos.map(projeto => {
            return (
              <form
                onSubmit={handleSubmit(handleUpdateProjeto)}
                key={projeto.projeto_id}
              >
                <DialogHeader>
                  <DialogTitle>Editar {projeto.nome}</DialogTitle>
                  <DialogDescription>
                    Editar informações da projeto
                  </DialogDescription>
                </DialogHeader>

                <div className="my-4 space-y-4">
                  <div className="space-y-1">
                    <Label>Nome do projeto</Label>
                    <Input {...register('nome')} />
                    {errors.nome && (
                      <p className="text-sm text-rose-500">
                        {errors.nome.message}
                      </p>
                    )}
                  </div>

                  <div className="space-y-1">
                    <Label>Descrição do projeto</Label>
                    <Textarea {...register('descricao')} />
                    {errors.descricao && (
                      <p className="text-sm text-rose-500">
                        {errors.descricao.message}
                      </p>
                    )}
                  </div>

                  <div className="flex flex-col gap-1">
                    <Label htmlFor="startDate">Data de início</Label>
                    <input
                      type="date"
                      id="startDate"
                      {...register('data_inicio')}
                      className="rounded border p-2"
                    />
                  </div>

                  <div className="flex flex-col gap-1">
                    <Label htmlFor="endDate">Data de término</Label>
                    <input
                      type="date"
                      id="endDate"
                      {...register('data_fim')}
                      className="rounded-md border p-2"
                    />
                  </div>
                </div>

                <DialogFooter>
                  <DialogClose asChild>
                    <Button
                      type="button"
                      variant="ghost"
                      className="w-full"
                      onClick={() => setIsOpen(!isOpen)}
                    >
                      Cancelar
                    </Button>
                  </DialogClose>
                  <Button
                    type="submit"
                    disabled={isSubmitting}
                    className="w-full"
                  >
                    {isSubmitting ? (
                      <Loader2 className="size-4 animate-spin" />
                    ) : (
                      'Salvar'
                    )}
                  </Button>
                </DialogFooter>
              </form>
            );
          })}

        {isLoading && <ProjetoSkeletonDialog />}
      </DialogContent>
    </Dialog>
  );
}
