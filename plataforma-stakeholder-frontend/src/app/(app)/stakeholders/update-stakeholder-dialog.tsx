'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Loader2 } from 'lucide-react';
import { useState } from 'react';
import { Controller, useForm } from 'react-hook-form';
import { z } from 'zod';

import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
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
import { Separator } from '@/components/ui/separator';
import { useToast } from '@/hooks/use-toast';
import { getStakeholders } from '@/http/stakeholders/get-stakeholders';
import { updateStakeholder } from '@/http/stakeholders/update-stakeholder';
import { formatCpfCnpj } from '@/utils/format-cpf-cnpj';

import { Stakeholder } from './columns';
import { StakeholderSkeletonDialog } from './stakeholder-skeleton-dialog';

const updateStakeholderFormSchema = z.object({
  camada_stakeholder: z.boolean().default(true),
  camada_advogados: z.boolean().default(false),
  stakeholder_advogado: z.boolean().default(false),
});

type UpdateStakeholderFormSchema = z.infer<typeof updateStakeholderFormSchema>;

interface UpdateStakeholderDialogProps {
  stakeholder: Stakeholder;
}

export function UpdateStakeholderDialog({
  stakeholder,
}: UpdateStakeholderDialogProps) {
  const [isOpen, setIsOpen] = useState(false);

  const { toast } = useToast();
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['stakeholders', stakeholder.document],
    queryFn: () => getStakeholders({ documento: stakeholder.document }),
    enabled: isOpen,
  });

  const { mutateAsync: updateStakeholderFn } = useMutation({
    mutationFn: updateStakeholder,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['stakeholders', 'consult'] });
    },
  });

  const {
    control,
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<UpdateStakeholderFormSchema>({
    resolver: zodResolver(updateStakeholderFormSchema),
    defaultValues: {
      camada_stakeholder: false,
      camada_advogados: false,
      stakeholder_advogado: false,
    },
  });

  async function handleUpdateStakeholder(data: UpdateStakeholderFormSchema) {
    try {
      await updateStakeholderFn({
        documento: stakeholder.document,
        prospeccao: stakeholder.em_prospecao,
        camada_stakeholder: data.camada_stakeholder,
        camada_advogados: data.camada_advogados,
        stakeholder_advogado: data.stakeholder_advogado,
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
          Atualizar
        </Button>
      </DialogTrigger>

      {data &&
        data.stakeholders.map(stakeholder => {
          return (
            <DialogContent key={stakeholder.document}>
              <DialogHeader>
                <DialogTitle>Atualizar relacionamentos</DialogTitle>
                <DialogDescription>
                  Atualize os relaciomentos de um stakeholder.
                </DialogDescription>
              </DialogHeader>

              <form
                onSubmit={handleSubmit(handleUpdateStakeholder)}
                key={stakeholder.document}
                className="space-y-6"
              >
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <p className="text-sm text-muted-foreground">
                      Stakeholder:
                    </p>
                    <p className="text-sm font-medium">{stakeholder.nome1}</p>
                  </div>

                  <Separator />

                  <Controller
                    name="stakeholder_advogado"
                    control={control}
                    render={({ field }) => {
                      return (
                        <div className="flex items-start space-x-2">
                          <Checkbox
                            checked={field.value}
                            onCheckedChange={field.onChange}
                            disabled={stakeholder.document.length > 11}
                          />
                          <div className="flex flex-col gap-1">
                            <Label
                              htmlFor="terms"
                              className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                            >
                              Stakeholder advogado
                            </Label>
                            <span className="text-sm text-muted-foreground">
                              Ao marcar este campo, este stakeholder será
                              considerado um advogado.
                            </span>
                          </div>
                        </div>
                      );
                    }}
                  />

                  <Controller
                    name="camada_stakeholder"
                    control={control}
                    render={({ field }) => {
                      return (
                        <div className="flex items-start space-x-2">
                          <Checkbox
                            checked={field.value}
                            onCheckedChange={field.onChange}
                          />
                          <div className="flex flex-col gap-1">
                            <Label
                              htmlFor="terms"
                              className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                            >
                              Camada de stakeholder
                            </Label>
                            <span className="text-sm text-muted-foreground">
                              Ao marcar este campo, será atualizado os
                              relacionamentos deste stakeholder.
                            </span>
                          </div>
                        </div>
                      );
                    }}
                  />

                  <Controller
                    name="camada_advogados"
                    control={control}
                    render={({ field }) => {
                      return (
                        <div className="flex items-start space-x-2">
                          <Checkbox
                            checked={field.value}
                            onCheckedChange={field.onChange}
                          />
                          <div className="flex flex-col gap-1">
                            <Label
                              htmlFor="terms"
                              className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                            >
                              Camada de advogados
                            </Label>
                            <span className="text-sm text-muted-foreground">
                              Ao marcar este campo, será atualizado os
                              relacionamentos de advogados deste stakeholder.
                            </span>
                          </div>
                        </div>
                      );
                    }}
                  />
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
                      'Confirmar'
                    )}
                  </Button>
                </DialogFooter>
              </form>

              {isLoading && <StakeholderSkeletonDialog />}
            </DialogContent>
          );
        })}
    </Dialog>
  );
}
