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

import { Empresa } from './columns';

interface DeleteEmpresaDialogProps {
  empresa: Empresa;
}

export function DeleteEmpresaDialog({ empresa }: DeleteEmpresaDialogProps) {
  const [isOpen, setIsOpen] = useState(false);

  const { toast } = useToast();

  const queryClient = useQueryClient();

  const { mutateAsync: deleteEmpresaFn, isPending } = useMutation({
    mutationFn: deleteEmpresa,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['empresas'] });
    },
  });

  async function handleDeleteEmpresa(id: number) {
    try {
      await deleteEmpresaFn({
        empresa_id: empresa.empresa_id,
      });

      setIsOpen(false);

      toast({
        title: 'Empresa removido!',
        description: 'Você removeu o empresa com sucesso.',
      });
    } catch (err) {
      console.log(err);
      toast({
        variant: 'destructive',
        title: 'Erro ao tentar remover...',
        description: 'Não foi possível remover o empresa desejado.',
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
            <DialogTitle>Excluir {empresa.razao_social}</DialogTitle>
          </DialogHeader>

          <div className="my-4 space-y-4">
            <p>Deseja realmente excluir está empresa?</p>
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
              onClick={() => handleDeleteEmpresa(empresa.empresa_id)}
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
