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
import { deleteOffice } from '@/http/offices/delete-office';

import { Office } from './columns';

interface DeleteOfficeDialogProps {
  office: Office;
}

export function DeleteOfficeDialog({ office }: DeleteOfficeDialogProps) {
  const [isOpen, setIsOpen] = useState(false);

  const { toast } = useToast();

  const queryClient = useQueryClient();

  const { mutateAsync: deleteOfficeFn, isPending } = useMutation({
    mutationFn: deleteOffice,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['offices'] });
    },
  });

  async function handleDeleteOffice(id: number) {
    try {
      await deleteOfficeFn({
        escritorio_id: office.escritorio_id,
      });

      setIsOpen(false);

      toast({
        title: 'Escritório removido!',
        description: 'Você removeu o escritório com sucesso.',
      });
    } catch (err) {
      console.log(err);
      toast({
        variant: 'destructive',
        title: 'Erro ao tentar remover...',
        description: 'Não foi possível remover o escritório desejado.',
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
            <DialogTitle>Excluir {office.nome_fantasia}</DialogTitle>
          </DialogHeader>

          <div className="my-4 space-y-4">
            <p>Deseja realmente excluir este escritório?</p>
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
              onClick={() => handleDeleteOffice(office.escritorio_id)}
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
