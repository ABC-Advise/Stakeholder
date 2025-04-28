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
import { getPessoas } from '@/http/pessoa/get-pessoas'
import { updatePessoa } from '@/http/pessoa/update-pessoa'
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible'
import { Checkbox } from '@/components/ui/checkbox'
import { formatCpfCnpj } from '@/utils/format-cpf-cnpj'
import { Pessoa } from './columns'
import { removeNonNumeric } from '@/utils/remove-format'
import { PessoaSkeletonDialog } from './pessoa-skeleton-dialog'
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
})

type UpdateFormSchema = z.infer<typeof updateFormSchema>

interface EditPessoaDialogProps {
  pessoa: Pessoa
}

export function EditPessoaDialog({ pessoa }: EditPessoaDialogProps) {
  const [isOpen, setIsOpen] = useState(false)

  const { toast } = useToast()

  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['pessoas', pessoa.pessoa_id],
    queryFn: () => getPessoas({ pessoa_id: pessoa.pessoa_id }),
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
      cpf: pessoa.cpf ?? '',
      firstname: pessoa.firstname ?? '',
      lastname: pessoa.lastname ?? '',
      stakeholder: pessoa.stakeholder ?? '',
      em_prospecao: pessoa.em_prospecao ?? '',
      instagram: pessoa.instagram ?? '',
      linkedin: pessoa.linkedin ?? '',
    },
  })

  const { mutateAsync: updatePessoaFn } = useMutation({
    mutationFn: updatePessoa,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pessoas'] })
    },
  })

  async function handleUpdatePessoa(data: UpdateFormSchema) {
    try {
      await updatePessoaFn({
        pessoa_id: pessoa.pessoa_id,
        cpf: removeNonNumeric(data.cpf),
        firstname: data.firstname,
        lastname: data.lastname,
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
          data.pessoas.map((pessoa) => {
            return (
              <form
                onSubmit={handleSubmit(handleUpdatePessoa)}
                key={pessoa.pessoa_id}
              >
                <DialogHeader>
                  <DialogTitle>
                    Editar {pessoa.firstname} {pessoa.lastname}
                  </DialogTitle>
                  <DialogDescription>
                    Editar informações da pessoa
                  </DialogDescription>
                </DialogHeader>

                <div className="my-4 space-y-4">
                  <div className="space-y-1">
                    <Label>Primeiro nome</Label>
                    <Input {...register('firstname')} />
                    {errors.firstname && (
                      <p className="text-sm text-rose-500">
                        {errors.firstname.message}
                      </p>
                    )}
                  </div>
                  <div className="space-y-1">
                    <Label>Último nome</Label>
                    <Input {...register('lastname')} />
                    {errors.lastname && (
                      <p className="text-sm text-rose-500">
                        {errors.lastname.message}
                      </p>
                    )}
                  </div>
                  <div className="space-y-1">
                    <Label>CPF</Label>
                    <Input
                      placeholder="00.000.000-00"
                      minLength={11}
                      maxLength={15}
                      {...register('cpf')}
                      onChange={(e) => {
                        const formattedValue = formatCpfCnpj(e.target.value)
                        e.target.value = formattedValue
                      }}
                    />
                    {errors.cpf && (
                      <p className="text-sm text-rose-500">
                        {errors.cpf.message}
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
                          defaultValue={pessoa.projeto_id.toString()}
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
                              Ao marcar este campo, você informa que está pessoa
                              é um stakeholder.
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
                              Ao marcar este campo, você informa que esta pessoa
                              está em prospecção.
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

        {isLoading && <PessoaSkeletonDialog />}
      </DialogContent>
    </Dialog>
  )
}
