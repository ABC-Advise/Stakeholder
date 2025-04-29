'use client'

import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
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
import { Controller, useForm } from 'react-hook-form'

import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { formatCpfCnpj } from '@/utils/format-cpf-cnpj'
import { useToast } from '@/hooks/use-toast'
import { Loader2 } from 'lucide-react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { getStakeholders } from '@/http/stakeholders/get-stakeholders'
import { useState } from 'react'
import { Stakeholder } from './columns'
import { StakeholderSkeletonDialog } from './stakeholder-skeleton-dialog'
import { updateStakeholder } from '@/http/stakeholders/update-stakeholder'
import { updateEmpresa } from '@/http/empresa/update-empresa'
import { updatePessoa } from '@/http/pessoa/update-pessoa'
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
} from '@/components/ui/select'
import { SelectValue } from '@radix-ui/react-select'
import { getProjetos } from '@/http/projetos/get-projetos'

const cpfPattern = /^\d{3}\.\d{3}\.\d{3}-\d{2}$/
const cnpjPattern = /^\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}$/

function removeNonNumeric(value: string) {
  return value.replace(/\D/g, '') // Remove todos os caracteres não numéricos
}

const editStakeholderFormSchema = z
  .object({
    documento: z.string(),
    prospeccao: z.boolean().default(false),
    stakeholder: z.boolean().default(true),
    associado: z.boolean().default(true),
    projeto: z.string().optional(),
  })
  .refine(
    (data) => {
      if (data.prospeccao && !data.stakeholder) {
        return false
      }
      return true
    },
    {
      message: 'O cliente em prospecção deve ser um stakeholder.',
      path: ['stakeholder'],
    },
  )

type EditStakeholderFormSchema = z.infer<typeof editStakeholderFormSchema>

interface EditStakeholderDialogProps {
  stakeholder: Stakeholder
}

export function EditStakeholderDialog({
  stakeholder,
}: EditStakeholderDialogProps) {
  const [isOpen, setIsOpen] = useState(false)

  const { toast } = useToast()
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['stakeholders', stakeholder.document],
    queryFn: () => getStakeholders({ documento: stakeholder.document }),
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
    watch,
    formState: { errors, isSubmitting },
  } = useForm<EditStakeholderFormSchema>({
    resolver: zodResolver(editStakeholderFormSchema),
    defaultValues: {
      documento: stakeholder.document ?? '',
      prospeccao: stakeholder.em_prospecao ?? false,
      stakeholder: stakeholder.stakeholder ?? false,
      associado: stakeholder.associado ?? false,
    },
  })

  async function handleEditStakeholder(data: EditStakeholderFormSchema) {
    try {
      if (stakeholder.is_CNPJ) {
        await updateEmpresa({
          empresa_id: stakeholder.entidade_id,
          cnpj: data.documento,
          stakeholder: data.stakeholder,
          em_prospecao: data.prospeccao,
          projeto_id: data.projeto ? Number(data.projeto) : undefined,
        })
      } else {
        await updatePessoa({
          pessoa_id: stakeholder.entidade_id,
          cpf: data.documento,
          stakeholder: data.stakeholder,
          em_prospecao: data.prospeccao,
          associado: data.associado ?? false,
          projeto_id: data.projeto ? Number(data.projeto) : undefined,
        })
      }

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

  const prospeccao = watch('prospeccao')
  const stakeholderCheckbox = watch('stakeholder')

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="ghost" size="sm" className="w-full justify-start">
          Editar
        </Button>
      </DialogTrigger>

      <DialogContent>
        <DialogHeader>
          <DialogTitle>Editar stakeholder</DialogTitle>
          <DialogDescription>
            Editar as informações necessárias para adicionar um stakeholder
          </DialogDescription>
        </DialogHeader>

        {data &&
          data.stakeholders.map((stakeholder) => {
            return (
              <form
                onSubmit={handleSubmit(handleEditStakeholder)}
                key={stakeholder.document}
                className="space-y-6"
              >
                <div className="space-y-4">
                  <div className="space-y-1">
                    <Label>
                      CNPJ/CPF<span className="text-rose-500">*</span>
                    </Label>
                    <Input
                      placeholder="Digite o CNPJ ou CPF"
                      minLength={11}
                      maxLength={15}
                      disabled
                      {...register('documento')}
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
                        <div className="flex items-start space-x-2">
                          <Checkbox
                            checked={field.value}
                            onCheckedChange={(checked) => {
                              // Impede desmarcar se prospecção estiver marcada
                              if (prospeccao && !checked) return
                              field.onChange(checked)
                            }}
                          />
                          <div className="flex flex-col gap-1">
                            <Label
                              htmlFor="terms"
                              className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                            >
                              Stakeholder
                            </Label>
                            <span className="text-sm text-muted-foreground">
                              Ao desmarcar este campo, o cliente deixará de ser
                              um stakeholder
                            </span>
                            {errors.stakeholder && (
                              <span className="text-sm text-red-500">
                                {errors.stakeholder.message}
                              </span>
                            )}
                          </div>
                        </div>
                      )
                    }}
                  />

                  <Controller
                    name="prospeccao"
                    control={control}
                    render={({ field }) => {
                      return (
                        <div className="flex items-start space-x-2">
                          <Checkbox
                            checked={field.value}
                            disabled={!stakeholderCheckbox} // Desabilita se stakeholder for falso
                            onCheckedChange={(checked) => {
                              field.onChange(checked)
                            }}
                          />
                          <div className="flex flex-col gap-1">
                            <Label
                              htmlFor="prospeccao"
                              className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                            >
                              Em prospecção
                            </Label>
                            <span className="text-sm text-muted-foreground">
                              Ao marcar este campo, você informa que este
                              cliente está em prospecção.
                            </span>
                          </div>
                        </div>
                      )
                    }}
                  />

                  <Controller
                    name="associado"
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
                              Associado
                            </Label>
                            <span className="text-sm text-muted-foreground">
                              Ao marcar este campo, você informa que este
                              cliente é um associado a um escritório.
                            </span>
                          </div>
                        </div>
                      )
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
                      'Salvar'
                    )}
                  </Button>
                </DialogFooter>
              </form>
            )
          })}

        {isLoading && <StakeholderSkeletonDialog />}
      </DialogContent>
    </Dialog>
  )
}
