'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Loader2 } from 'lucide-react';
import { useState } from 'react';

import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { useToast } from '@/hooks/use-toast';
import { deleteEmpresa } from '@/http/empresa/delete-empresa';
import { deletePessoa } from '@/http/pessoa/delete-pessoa';

import { Stakeholder } from './columns';

interface DeleteStakeholderDialogProps {
  stakeholder: Stakeholder;
}

export function DeleteStakeholderDialog({
  stakeholder,
}: DeleteStakeholderDialogProps) {
  const [isOpen, setIsOpen] = useState(false);

  const { toast } = useToast();

  const queryClient = useQueryClient();

  const { mutateAsync: deleteEmpresaFn, isPending: isPendingEmpresa } =
    useMutation({
      mutationFn: deleteEmpresa,
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['stakeholders'] });
      },
    });

  const { mutateAsync: deletePessoaFn, isPending: isPendingPessoa } =
    useMutation({
      mutationFn: deletePessoa,
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['stakeholders'] });
      },
    });

  async function handleDeleteStakeholder(id: number) {
    try {
      if (stakeholder.is_CNPJ) {
        await deleteEmpresaFn({
          empresa_id: id,
        });
      } else {
        await deletePessoaFn({
          pessoa_id: id,
        });
      }

      setIsOpen(false);

      toast({
        title: 'Stakeholder removido!',
        description: 'Você removeu o stakeholder com sucesso.',
      });
    } catch (err) {
      console.log(err);
      toast({
        variant: 'destructive',
        title: 'Erro ao tentar remover...',
        description: 'Não foi possível remover o stakeholder desejado.',
      });
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button
          variant="ghost"
          size="sm"
          className="w-full justify-start text-rose-500 hover:text-rose-600"
        >
          Excluir
        </Button>
      </DialogTrigger>

      <DialogContent>
        <form>
          <DialogHeader>
            <DialogTitle>
              Excluir {stakeholder.nome1} {stakeholder.nome2}
            </DialogTitle>
          </DialogHeader>

          <div className="my-4 space-y-4">
            <p>Deseja realmente excluir este stakeholder?</p>
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
              type="button"
              variant="destructive"
              disabled={isPendingEmpresa || isPendingPessoa}
              className="w-full"
              onClick={() => handleDeleteStakeholder(stakeholder.entidade_id)}
            >
              {isPendingPessoa || isPendingEmpresa ? (
                <Loader2 className="size-4 animate-spin" />
              ) : (
                'Remover'
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
