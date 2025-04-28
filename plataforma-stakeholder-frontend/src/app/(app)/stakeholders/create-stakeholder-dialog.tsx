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
import { createStakeholder } from '@/http/stakeholders/create-stakeholder'
import { useToast } from '@/hooks/use-toast'
import { Loader2 } from 'lucide-react'
import { removeNonNumeric } from '@/utils/remove-format'
import { useEffect, useState } from 'react'

const cpfPattern = /^\d{3}\.\d{3}\.\d{3}-\d{2}$/
const cnpjPattern = /^\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}$/

const createStakeholderFormSchema = z.object({
  documento: z
    .string()
    .min(11, { message: 'Este campo deve ter pelo menos 11 caracteres.' })
    .refine((value) => cpfPattern.test(value) || cnpjPattern.test(value), {
      message: 'Invalid CPF or CNPJ format',
    }),
  camada_advogados: z.boolean().default(false),
  associado: z.boolean().default(false),
  prospeccao: z.boolean().default(false),
})

type CreateStakeholderFormSchema = z.infer<typeof createStakeholderFormSchema>

interface CreateStakeholderDialogProps {
  isOpen: boolean
  setIsOpen: (isOpen: boolean) => void
}

export function CreateStakeholderDialog({
  isOpen,
  setIsOpen,
}: CreateStakeholderDialogProps) {
  const { toast } = useToast()

  const [inputDocumentoLenght, setInputDocumentoLenght] = useState(0)

  const {
    control,
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<CreateStakeholderFormSchema>({
    resolver: zodResolver(createStakeholderFormSchema),
  })

  async function handleCreateStakeholder(data: CreateStakeholderFormSchema) {
    try {
      await createStakeholder({
        documento: removeNonNumeric(data.documento), // Remove a formatação
        prospeccao: data.prospeccao,
        camada_advogados: data.camada_advogados,
        associado: data.associado,
      })

      setIsOpen(false)

      reset()

      toast({
        title: 'Sucesso!',
        description: 'Stakeholder foi cadastrado com sucesso.',
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
          <DialogTitle>Adicionar stakeholder</DialogTitle>
          <DialogDescription>
            Insira as informações necessárias para adicionar um stakeholder
          </DialogDescription>
        </DialogHeader>

        <form
          onSubmit={handleSubmit(handleCreateStakeholder)}
          className="space-y-6"
        >
          <div className="space-y-6">
            <div className="space-y-1">
              <Label>
                CNPJ/CPF<span className="text-rose-500">*</span>
              </Label>
              <Input
                placeholder="Digite o CNPJ ou CPF"
                minLength={11}
                maxLength={15}
                {...register('documento')}
                onChange={(e) => {
                  const formattedValue = formatCpfCnpj(e.target.value)
                  e.target.value = formattedValue

                  setInputDocumentoLenght(e.target.value.length)
                }}
              />

              {errors.documento && (
                <p className="pt-2 text-sm text-rose-500">
                  {errors.documento.message}
                </p>
              )}
            </div>

            <Controller
              name="camada_advogados"
              control={control}
              render={({ field }) => {
                return (
                  <div className="flex items-start space-x-2">
                    <Checkbox
                      checked={field.value}
                      onCheckedChange={field.onChange}
                      disabled={inputDocumentoLenght > 14}
                    />
                    <div className="flex flex-col gap-1">
                      <Label
                        htmlFor="terms"
                        className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                      >
                        Camada de advogados
                      </Label>
                      <span className="text-sm text-muted-foreground">
                        Ao marcar este campo, será atualizado os relacionamentos
                        de advogados deste stakeholder.
                      </span>
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
                        Ao marcar este campo, você informa que este cliente está
                        em prospecção.
                      </span>
                    </div>
                  </div>
                )
              }}
            />

            {/* <Controller
              name="stakeholder_advogado"
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
                        Atualizar apenas advogados
                      </Label>
                      <span className="text-sm text-muted-foreground">
                        Ao marcar este campo, você informa que este cliente é um
                        advogado.
                      </span>
                    </div>
                  </div>
                )
              }}
            /> */}

            <Controller
              name="associado"
              control={control}
              render={({ field }) => {
                return (
                  <div className="flex items-start space-x-2">
                    <Checkbox
                      checked={field.value}
                      onCheckedChange={field.onChange}
                      disabled={inputDocumentoLenght > 14}
                    />
                    <div className="flex flex-col gap-1">
                      <Label
                        htmlFor="terms"
                        className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                      >
                        Associado
                      </Label>
                      <span className="text-sm text-muted-foreground">
                        Ao marcar este campo, você informa que este cliente é um
                        associado a um escritório.
                      </span>
                    </div>
                  </div>
                )
              }}
            />
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
