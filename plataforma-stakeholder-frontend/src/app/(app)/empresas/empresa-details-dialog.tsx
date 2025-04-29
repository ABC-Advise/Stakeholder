'use client'

import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Empresa } from './columns'
import { EmpresaSkeletonDialog } from './empresa-skeleton-dialog'
import { getEmpresas } from '@/http/empresa/get-empresas'
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible'
import { ChevronDown } from 'lucide-react'
import { Checkbox } from '@/components/ui/checkbox'
import { Controller, useForm } from 'react-hook-form'
import { formatCpfCnpj } from '@/utils/format-cpf-cnpj'
import { z, ZodType } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { getProjetos } from '@/http/projetos/get-projetos'

interface EmpresaDetailsDialogProps {
  empresa: Empresa
}

const updateFormSchema = z.object({
  nome_fantasia: z
    .string()
    .min(1, { message: 'Nome fantasia é um campo obrigatório.' }),
  razao_social: z
    .string()
    .min(1, { message: 'Razão social é um campo obrigatório.' }),
  cnpj: z.string().min(1, { message: 'CNPJ é um campo obrigatório.' }),
  stakeholder: z.boolean().default(false),
  em_prospecao: z.boolean().default(false),
  instagram: z.string().optional(),
  linkedin: z.string().optional(),
  projeto: z.string().nonempty('Selecione um projeto válido.'),
})

type UpdateFormSchema = z.infer<typeof updateFormSchema>

export function EmpresaDetailsDialog({ empresa }: EmpresaDetailsDialogProps) {
  const [isOpen, setIsOpen] = useState(false)

  const { data, isLoading } = useQuery({
    queryKey: ['empresas', empresa.empresa_id],
    queryFn: () => getEmpresas({ empresa_id: empresa.empresa_id }),
    enabled: isOpen,
  })

  const { data: projetos, isLoading: isLoadingProjetos } = useQuery({
    queryKey: ['projetos'],
    queryFn: () => getProjetos({}),
    enabled: isOpen,
  })

  const { control, register } = useForm<UpdateFormSchema>({
    resolver: zodResolver(updateFormSchema as unknown as ZodType<any>),
    defaultValues: {
      cnpj: empresa.cnpj,
      razao_social: empresa.razao_social,
      nome_fantasia: empresa.nome_fantasia,
      stakeholder: empresa.stakeholder,
      em_prospecao: empresa.em_prospecao,
      instagram: empresa.instagram,
      linkedin: empresa.linkedin,
      projeto: empresa.projeto_id.toString() ?? '',
    },
  })

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="ghost" size="sm" className="w-full justify-start">
          Visualizar
        </Button>
      </DialogTrigger>

      <DialogContent>
        {data &&
          data.empresas.map((empresa) => {
            return (
              <form key={empresa.empresa_id}>
                <DialogHeader>
                  <DialogTitle>Visualizar</DialogTitle>
                  <DialogDescription>Detalhes da empresa</DialogDescription>
                </DialogHeader>

                <div className="my-4 space-y-4">
                  <div className="space-y-1">
                    <Label>Razão social</Label>
                    <Input disabled {...register('razao_social')} />
                  </div>
                  <div className="space-y-1">
                    <Label>Nome fantasia</Label>
                    <Input disabled {...register('nome_fantasia')} />
                  </div>
                  <div className="space-y-1">
                    <Label>CNPJ</Label>
                    <Input
                      placeholder="00.000.000/0000-00"
                      minLength={11}
                      maxLength={15}
                      disabled
                      {...register('cnpj')}
                      onChange={(e) => {
                        const formattedValue = formatCpfCnpj(e.target.value)
                        e.target.value = formattedValue
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
                          defaultValue={empresa.projeto_id.toString()}
                          disabled
                        >
                          <SelectTrigger className="w-full">
                            <SelectValue placeholder="Selecione um projeto" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectGroup>
                              <SelectLabel>Projetos</SelectLabel>
                              {projetos?.projetos.map((projeto) => (
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
                              Ao marcar este campo, você informa que está
                              empresa é um stakeholder.
                            </span>
                          </div>
                        </div>
                      )
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
                              Ao marcar este campo, você informa que esta
                              empresa está em prospecção.
                            </span>
                          </div>
                        </div>
                      )
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
            )
          })}

        {isLoading && <EmpresaSkeletonDialog />}
      </DialogContent>
    </Dialog>
  )
}
