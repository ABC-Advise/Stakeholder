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
import { deletePessoa } from '@/http/pessoa/delete-pessoa';

import { Pessoa } from './columns';

interface DeletePessoaDialogProps {
  pessoa: Pessoa;
}

export function DeletePessoaDialog({ pessoa }: DeletePessoaDialogProps) {
  const [isOpen, setIsOpen] = useState(false);

  const { toast } = useToast();

  const queryClient = useQueryClient();

  const { mutateAsync: deletePessoaFn, isPending } = useMutation({
    mutationFn: deletePessoa,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pessoas'] });
    },
  });

  async function handleDeletePessoa(id: number) {
    try {
      await deletePessoaFn({
        pessoa_id: pessoa.pessoa_id,
      });

      setIsOpen(false);

      toast({
        title: 'Pessoa removido!',
        description: 'Você removeu o pessoa com sucesso.',
      });
    } catch (err) {
      console.log(err);
      toast({
        variant: 'destructive',
        title: 'Erro ao tentar remover...',
        description: 'Não foi possível remover o pessoa desejado.',
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
              Excluir {pessoa.firstname} {pessoa.lastname}
            </DialogTitle>
          </DialogHeader>

          <div className="my-4 space-y-4">
            <p>Deseja realmente excluir está pessoa?</p>
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
              disabled={isPending}
              className="w-full"
              onClick={() => handleDeletePessoa(pessoa.pessoa_id)}
            >
              {isPending ? (
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
