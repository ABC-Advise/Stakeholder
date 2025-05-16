'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Loader2 } from 'lucide-react';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';

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
import { useToast } from '@/hooks/use-toast';
import { getOffices } from '@/http/offices/get-offices';
import { updateOffice } from '@/http/offices/update-office';

import { Office } from './columns';
import { OfficeSkeletonDialog } from './office-skeleton-dialog';

const upddateFormSchema = z.object({
  nome_fantasia: z
    .string()
    .min(1, { message: 'Nome fantasia é um campo obrigatório.' }),
  razao_social: z
    .string()
    .min(1, { message: 'Razão social é um campo obrigatório.' }),
});

type UpdateFormSchema = z.infer<typeof upddateFormSchema>;

interface EditOfficeDialogProps {
  office: Office;
}

export function EditOfficeDialog({ office }: EditOfficeDialogProps) {
  const [isOpen, setIsOpen] = useState(false);

  const { toast } = useToast();

  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['offices', office.escritorio_id],
    queryFn: () => getOffices({ escritorio_id: office.escritorio_id }),
    enabled: isOpen,
  });

  const {
    register,
    handleSubmit,
    reset,
    formState: { isSubmitting, errors },
  } = useForm<UpdateFormSchema>({
    resolver: zodResolver(upddateFormSchema),
  });

  const { mutateAsync: updateOfficeFn } = useMutation({
    mutationFn: updateOffice,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['offices'] });
    },
  });

  async function handleUpdateOffice(data: UpdateFormSchema) {
    try {
      await updateOfficeFn({
        escritorio_id: office.escritorio_id,
        razao_social: data.razao_social,
        nome_fantasia: data.nome_fantasia,
      });

      reset();

      setIsOpen(false);

      toast({
        title: 'Sucesso!',
        description: 'As informações sobre o escritório foram atualizadas.',
      });
    } catch (err) {
      console.log(err);
      toast({
        variant: 'destructive',
        title: 'Erro ao atualizar...',
        description:
          'Não foi possível atualizar as informações sobre o escritório.',
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
          data.escritorios.map(office => {
            return (
              <form
                onSubmit={handleSubmit(handleUpdateOffice)}
                key={office.escritorio_id}
              >
                <DialogHeader>
                  <DialogTitle>Editar {office.nome_fantasia}</DialogTitle>
                  <DialogDescription>
                    Editar informações do escritório
                  </DialogDescription>
                </DialogHeader>

                <div className="my-4 space-y-4">
                  <div className="space-y-1">
                    <Label>Nome fantansia</Label>
                    <Input
                      defaultValue={office.nome_fantasia}
                      {...register('nome_fantasia')}
                    />
                    {errors.nome_fantasia && (
                      <p className="text-sm text-rose-500">
                        {errors.nome_fantasia.message}
                      </p>
                    )}
                  </div>
                  <div className="space-y-1">
                    <Label>Razão social</Label>
                    <Input
                      defaultValue={office.razao_social}
                      {...register('razao_social')}
                    />
                    {errors.razao_social && (
                      <p className="text-sm text-rose-500">
                        {errors.razao_social.message}
                      </p>
                    )}
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

        {isLoading && <OfficeSkeletonDialog />}
      </DialogContent>
    </Dialog>
  );
}
