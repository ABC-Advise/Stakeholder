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
import { useToast } from '@/hooks/use-toast';
import { getLawyers } from '@/http/lawyers/get-lawyers';
import { updateLawyer } from '@/http/lawyers/update-lawyer';

import { Lawyer } from './columns';
import { LawyerSkeletonDialog } from './lawyer-skeleton-dialog';

const updateFormSchema = z.object({
  firstname: z
    .string()
    .min(1, { message: 'Primeiro nome é um campo obrigatório.' }),
  lastname: z
    .string()
    .min(1, { message: 'Último nome é um campo obrigatório.' }),
  oab: z.string().min(1, { message: 'OAB é um campo obrigatório.' }),
});

type UpdateFormSchema = z.infer<typeof updateFormSchema>;

interface EditLawyerDialogProps {
  lawyer: Lawyer;
}

export function EditLawyerDialog({ lawyer }: EditLawyerDialogProps) {
  const [isOpen, setIsOpen] = useState(false);

  const { toast } = useToast();

  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['lawyers', lawyer.advogado_id],
    queryFn: () => getLawyers({ advogado_id: lawyer.advogado_id }),
    enabled: isOpen,
  });

  const {
    register,
    handleSubmit,
    reset,
    formState: { isSubmitting, errors },
  } = useForm<UpdateFormSchema>({
    resolver: zodResolver(updateFormSchema as unknown as ZodType<any>),
  });

  const { mutateAsync: updateLawyerFn } = useMutation({
    mutationFn: updateLawyer,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lawyers'] });
    },
  });

  async function handleUpdateOffice(data: UpdateFormSchema) {
    try {
      await updateLawyerFn({
        advogado_id: lawyer.advogado_id,
        firstname: data.firstname,
        lastname: data.lastname,
        oab: data.oab,
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
          data.advogados.map(lawyer => {
            return (
              <form
                onSubmit={handleSubmit(handleUpdateOffice)}
                key={lawyer.advogado_id}
              >
                <DialogHeader>
                  <DialogTitle>
                    Editar {lawyer.firstname} {lawyer.lastname}
                  </DialogTitle>
                  <DialogDescription>
                    Editar informações do advogado
                  </DialogDescription>
                </DialogHeader>

                <div className="my-4 space-y-4">
                  <div className="space-y-1">
                    <Label>Primeiro nome</Label>
                    <Input
                      defaultValue={lawyer.firstname}
                      {...register('firstname')}
                    />
                    {errors.firstname && (
                      <p className="text-sm text-rose-500">
                        {errors.firstname.message}
                      </p>
                    )}
                  </div>
                  <div className="space-y-1">
                    <Label>Último nome</Label>
                    <Input
                      defaultValue={lawyer.lastname}
                      {...register('lastname')}
                    />
                    {errors.lastname && (
                      <p className="text-sm text-rose-500">
                        {errors.lastname.message}
                      </p>
                    )}
                  </div>
                  <div className="space-y-1">
                    <Label>OAB</Label>
                    <Input defaultValue={lawyer.oab} {...register('oab')} />
                    {errors.oab && (
                      <p className="text-sm text-rose-500">
                        {errors.oab.message}
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

        {isLoading && <LawyerSkeletonDialog />}
      </DialogContent>
    </Dialog>
  );
}
