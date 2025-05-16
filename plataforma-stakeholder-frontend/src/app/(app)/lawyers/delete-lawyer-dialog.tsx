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
import { deleteLawyer } from '@/http/lawyers/delete-lawyer';

import { Lawyer } from './columns';

interface DeleteLawyerDialogProps {
  lawyer: Lawyer;
}

export function DeleteLawyerDialog({ lawyer }: DeleteLawyerDialogProps) {
  const [isOpen, setIsOpen] = useState(false);

  const { toast } = useToast();

  const queryClient = useQueryClient();

  const { mutateAsync: deleteLawyerFn, isPending } = useMutation({
    mutationFn: deleteLawyer,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lawyers'] });
    },
  });

  async function handleDeleteLawyer(id: number) {
    try {
      await deleteLawyerFn({
        advogado_id: lawyer.advogado_id,
      });

      setIsOpen(false);

      toast({
        title: 'Advogado removido!',
        description: 'Você removeu o advogado com sucesso.',
      });
    } catch (err) {
      console.log(err);
      toast({
        variant: 'destructive',
        title: 'Erro ao tentar remover...',
        description: 'Não foi possível remover o advogado desejado.',
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
              Excluir {lawyer.firstname} {lawyer.lastname}
            </DialogTitle>
          </DialogHeader>

          <div className="my-4 space-y-4">
            <p>Deseja realmente excluir este advogado?</p>
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
              onClick={() => handleDeleteLawyer(lawyer.advogado_id)}
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
