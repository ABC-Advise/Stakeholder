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
import { useToast } from '@/hooks/use-toast'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ChevronDown, Loader2 } from 'lucide-react'
import { useState } from 'react'
import { Controller, useForm } from 'react-hook-form'
import { z, ZodType } from 'zod'
import { Empresa } from './columns'
import { getEmpresas } from '@/http/empresa/get-empresas'
import { updateEmpresa } from '@/http/empresa/update-empresa'
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible'
import { Checkbox } from '@/components/ui/checkbox'
import { formatCpfCnpj } from '@/utils/format-cpf-cnpj'
import { EmpresaSkeletonDialog } from './empresa-skeleton-dialog'
import { removeNonNumeric } from '@/utils/remove-format'
import { getProjetos } from '@/http/projetos/get-projetos'
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

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

interface EditEmpresaDialogProps {
  empresa: Empresa
}

export function EditEmpresaDialog({ empresa }: EditEmpresaDialogProps) {
  const [isOpen, setIsOpen] = useState(false)

  const { toast } = useToast()

  const queryClient = useQueryClient()

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

  const {
    control,
    register,
    handleSubmit,
    reset,
    formState: { isSubmitting, errors },
  } = useForm<UpdateFormSchema>({
    resolver: zodResolver(updateFormSchema as unknown as ZodType<any>),
    defaultValues: {
      cnpj: empresa.cnpj,
      razao_social: empresa.razao_social,
      nome_fantasia: empresa.nome_fantasia,
      stakeholder: empresa.stakeholder,
      em_prospecao: empresa.em_prospecao,
      instagram: empresa.instagram,
      linkedin: empresa.linkedin,
      projeto: empresa.projeto_id,
    },
  })

  const { mutateAsync: updateEmpresaFn } = useMutation({
    mutationFn: updateEmpresa,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['empresas'] })
    },
  })

  async function handleUpdateEmpresa(data: UpdateFormSchema) {
    try {
      await updateEmpresaFn({
        empresa_id: empresa.empresa_id,
        cnpj: removeNonNumeric(data.cnpj),
        nome_fantasia: data.nome_fantasia,
        razao_social: data.razao_social,
        stakeholder: data.stakeholder,
        em_prospecao: data.em_prospecao,
        instagram: data.instagram,
        linkedin: data.linkedin,
        projeto_id: Number(data.projeto),
      })

      reset()

      setIsOpen(false)

      toast({
        title: 'Sucesso!',
        description: 'As informações sobre o escritório foram atualizadas.',
      })
    } catch (err) {
      console.log(err)
      toast({
        variant: 'destructive',
        title: 'Erro ao atualizar...',
        description:
          'Não foi possível atualizar as informações sobre o escritório.',
      })
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
          data.empresas.map((empresa) => {
            return (
              <form
                onSubmit={handleSubmit(handleUpdateEmpresa)}
                key={empresa.empresa_id}
              >
                <DialogHeader>
                  <DialogTitle>Editar</DialogTitle>
                  <DialogDescription>
                    Editar informações da empresa
                  </DialogDescription>
                </DialogHeader>

                <div className="my-4 space-y-4">
                  <div className="space-y-1">
                    <Label>Razão social</Label>
                    <Input {...register('razao_social')} />
                    {errors.razao_social && (
                      <p className="text-sm text-rose-500">
                        {errors.razao_social.message}
                      </p>
                    )}
                  </div>
                  <div className="space-y-1">
                    <Label>Nome fantasia</Label>
                    <Input {...register('nome_fantasia')} />
                    {errors.nome_fantasia && (
                      <p className="text-sm text-rose-500">
                        {errors.nome_fantasia.message}
                      </p>
                    )}
                  </div>
                  <div className="space-y-1">
                    <Label>CNPJ</Label>
                    <Input
                      placeholder="00.000.000/0000-00"
                      minLength={11}
                      maxLength={15}
                      {...register('cnpj')}
                      onChange={(e) => {
                        const formattedValue = formatCpfCnpj(e.target.value)
                        e.target.value = formattedValue
                      }}
                    />
                    {errors.cnpj && (
                      <p className="text-sm text-rose-500">
                        {errors.cnpj.message}
                      </p>
                    )}
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
                    {errors.projeto && (
                      <p className="text-sm text-red-500">
                        {errors.projeto.message}
                      </p>
                    )}
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
                        <Input {...register('instagram')} />
                        {errors.instagram && (
                          <p className="text-sm text-rose-500">
                            {errors.instagram.message}
                          </p>
                        )}
                      </div>

                      <div className="space-y-1">
                        <Label>LinkedIn</Label>
                        <Input {...register('linkedin')} />
                        {errors.linkedin && (
                          <p className="text-sm text-rose-500">
                            {errors.linkedin.message}
                          </p>
                        )}
                      </div>
                    </CollapsibleContent>
                  </Collapsible>
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
            )
          })}

        {isLoading && <EmpresaSkeletonDialog />}
      </DialogContent>
    </Dialog>
  )
}
