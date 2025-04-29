'use client'

import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Controller, useForm } from 'react-hook-form'

import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { formatCpfCnpj } from '@/utils/format-cpf-cnpj'
import { useToast } from '@/hooks/use-toast'
import { ChevronDown, Loader2 } from 'lucide-react'
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible'
import { createPessoa } from '@/http/pessoa/create-pessoa'
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useQuery } from '@tanstack/react-query'
import { getProjetos } from '@/http/projetos/get-projetos'

const cpfPattern = /^\d{3}\.\d{3}\.\d{3}-\d{2}$/
const cnpjPattern = /^\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}$/

function removeNonNumeric(value: string) {
  return value.replace(/\D/g, '') // Remove todos os caracteres não numéricos
}

const createFormSchema = z.object({
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
  projeto: z.string().optional(),
})

type CreateFormSchema = z.infer<typeof createFormSchema>

interface CreatePessoaDialogProps {
  isOpen: boolean
  setIsOpen: (isOpen: boolean) => void
}

export function CreatePessoaDialog({
  isOpen,
  setIsOpen,
}: CreatePessoaDialogProps) {
  const { toast } = useToast()

  const {
    control,
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<CreateFormSchema>({
    resolver: zodResolver(createFormSchema),
  })

  const { data: projetos, isLoading: isLoadingProjetos } = useQuery({
    queryKey: ['projetos'],
    queryFn: () => getProjetos({}),
    enabled: isOpen,
  })

  async function handleCreatePessoa(data: CreateFormSchema) {
    try {
      await createPessoa({
        cpf: removeNonNumeric(data.cpf),
        firstname: data.firstname,
        lastname: data.lastname,
        stakeholder: data.stakeholder,
        em_prospecao: data.em_prospecao,
        instagram: data.instagram,
        linkedin: data.linkedin,
        projeto_id: Number(data.projeto),
      })

      setIsOpen(false)

      reset()

      toast({
        title: 'Sucesso!',
        description: 'Pessoa foi cadastrado com sucesso.',
      })
    } catch (err) {
      console.log(err)

      toast({
        variant: 'destructive',
        title: 'Ops...',
        description: 'Ocorreu um erro ao tentar cadastrar.',
      })
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogContent className="no-scrollbar max-h-[800px] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Adicionar pessoa</DialogTitle>
          <DialogDescription>
            Insira as informações necessárias para adicionar uma pessoa
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(handleCreatePessoa)} className="space-y-6">
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
                <p className="text-sm text-rose-500">{errors.cpf.message}</p>
              )}
            </div>

            <div className="space-y-1">
              <Label>Projeto</Label>

              <Controller
                name="projeto"
                control={control}
                render={({ field }) => (
                  <Select onValueChange={field.onChange} value={field.value}>
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
                <p className="text-sm text-red-500">{errors.projeto.message}</p>
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
                        Ao marcar este campo, você informa que está pessoa é um
                        stakeholder.
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
                        Ao marcar este campo, você informa que esta pessoa está
                        em prospecção.
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

          <div className="flex items-center gap-2">
            <DialogClose asChild>
              <Button variant="secondary" className="w-full">
                Cancelar
              </Button>
            </DialogClose>
            <Button type="submit" className="w-full" disabled={isSubmitting}>
              {isSubmitting ? (
                <Loader2 className="size-4 animate-spin" />
              ) : (
                'Salvar'
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
