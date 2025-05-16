'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { useQuery } from '@tanstack/react-query';
import { ChevronDown } from 'lucide-react';
import { useState } from 'react';
import { Controller, useForm } from 'react-hook-form';
import { z, ZodType } from 'zod';

import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';
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
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { getPessoas } from '@/http/pessoa/get-pessoas';
import { getProjetos } from '@/http/projetos/get-projetos';
import { formatCpfCnpj } from '@/utils/format-cpf-cnpj';

import { Pessoa } from './columns';
import { PessoaSkeletonDialog } from './pessoa-skeleton-dialog';

interface PessoaDetailsDialogProps {
  pessoa: Pessoa;
}

const updateFormSchema = z.object({
  firstname: z
    .string()
    .min(1, { message: 'Primeiro nome é um campo obrigatório.' }),
  lastname: z
    .string()
    .min(1, { message: 'Último nome é um campo obrigatório.' }),
  cpf: z.string().min(1, { message: 'CPF é um campo obrigatório.' }),
  stakeholder: z.boolean().default(false),
  em_prospecao: z.boolean().default(false),
  instagram: z.string().optional(),
  linkedin: z.string().optional(),
  projeto: z.string().nonempty('Selecione um projeto válido.'),
});

type UpdateFormSchema = z.infer<typeof updateFormSchema>;

export function PessoaDetailsDialog({ pessoa }: PessoaDetailsDialogProps) {
  const [isOpen, setIsOpen] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ['pessoas', pessoa.pessoa_id],
    queryFn: () => getPessoas({ pessoa_id: pessoa.pessoa_id }),
    enabled: isOpen,
  });

  const { data: projetos, isLoading: isLoadingProjetos } = useQuery({
    queryKey: ['projetos'],
    queryFn: () => getProjetos({}),
    enabled: isOpen,
  });

  const { control, register } = useForm<UpdateFormSchema>({
    resolver: zodResolver(updateFormSchema as unknown as ZodType<any>),
    defaultValues: {
      cpf: pessoa.cpf ?? '',
      firstname: pessoa.firstname ?? '',
      lastname: pessoa.lastname ?? '',
      stakeholder: pessoa.stakeholder ?? '',
      em_prospecao: pessoa.em_prospecao ?? '',
      instagram: pessoa.instagram ?? '',
      linkedin: pessoa.linkedin ?? '',
      projeto: pessoa.projeto_id.toString() ?? '',
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
          data.pessoas.map(pessoa => {
            return (
              <form key={pessoa.pessoa_id}>
                <DialogHeader>
                  <DialogTitle>
                    Visualizar {pessoa.firstname} {pessoa.lastname}
                  </DialogTitle>
                  <DialogDescription>Detalhes da pessoa</DialogDescription>
                </DialogHeader>

                <div className="my-4 space-y-4">
                  <div className="space-y-1">
                    <Label>Primeiro nome</Label>
                    <Input disabled {...register('firstname')} />
                  </div>
                  <div className="space-y-1">
                    <Label>Último nome</Label>
                    <Input disabled {...register('lastname')} />
                  </div>
                  <div className="space-y-1">
                    <Label>CPF</Label>
                    <Input
                      placeholder="00.000.000-00"
                      minLength={11}
                      maxLength={15}
                      disabled
                      {...register('cpf')}
                      onChange={e => {
                        const formattedValue = formatCpfCnpj(e.target.value);
                        e.target.value = formattedValue;
                      }}
                    />
                  </div>

                  <div className="space-y-1">
                    <Label>Projeto</Label>

                    <Controller
                      name="projeto"
                      control={control}
                      render={({ field }) => (
                        <Select
                          onValueChange={field.onChange}
                          value={field.value}
                          defaultValue={pessoa.projeto_id.toString()}
                          disabled
                        >
                          <SelectTrigger className="w-full">
                            <SelectValue placeholder="Selecione um projeto" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectGroup>
                              <SelectLabel>Projetos</SelectLabel>
                              {projetos?.projetos.map(projeto => (
                                <SelectItem
                                  key={projeto.projeto_id}
                                  value={projeto.projeto_id.toString()}
                                >
                                  {projeto.nome}
                                </SelectItem>
                              ))}
                            </SelectGroup>
                          </SelectContent>
                        </Select>
                      )}
                    />
                  </div>

                  <Controller
                    name="stakeholder"
                    control={control}
                    render={({ field }) => {
                      return (
                        <div className="flex items-start space-x-2 rounded-lg border p-3">
                          <Checkbox
                            checked={field.value}
                            onCheckedChange={field.onChange}
                            disabled
                          />
                          <div className="flex flex-col gap-1">
                            <Label
                              htmlFor="terms"
                              className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                            >
                              Stakeholder
                            </Label>
                            <span className="text-sm text-muted-foreground">
                              Ao marcar este campo, você informa que está pessoa
                              é um stakeholder.
                            </span>
                          </div>
                        </div>
                      );
                    }}
                  />

                  <Controller
                    name="em_prospecao"
                    control={control}
                    render={({ field }) => {
                      return (
                        <div className="flex items-start space-x-2 rounded-lg border p-3">
                          <Checkbox
                            checked={field.value}
                            onCheckedChange={field.onChange}
                            disabled
                          />
                          <div className="flex flex-col gap-1">
                            <Label
                              htmlFor="terms"
                              className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                            >
                              Em prospecção
                            </Label>
                            <span className="text-sm text-muted-foreground">
                              Ao marcar este campo, você informa que esta pessoa
                              está em prospecção.
                            </span>
                          </div>
                        </div>
                      );
                    }}
                  />

                  <Collapsible>
                    <CollapsibleTrigger className="group flex items-center gap-2">
                      <span className="text-sm font-medium">
                        Informações adicionais
                      </span>
                      <ChevronDown className="size-4 transition ease-linear group-data-[state=open]:rotate-180" />
                    </CollapsibleTrigger>

                    <CollapsibleContent>
                      <div className="mt-2 space-y-1">
                        <Label>Instagram</Label>
                        <Input disabled {...register('instagram')} />
                      </div>

                      <div className="space-y-1">
                        <Label>LinkedIn</Label>
                        <Input disabled {...register('linkedin')} />
                      </div>
                    </CollapsibleContent>
                  </Collapsible>
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

        {isLoading && <PessoaSkeletonDialog />}
      </DialogContent>
    </Dialog>
  );
}
