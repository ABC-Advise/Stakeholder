'use client'

import { Button } from '@/components/ui/button'
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
import { useForm } from 'react-hook-form'

import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { useToast } from '@/hooks/use-toast'
import { Loader2 } from 'lucide-react'
import { createProjeto } from '@/http/projetos/create-projeto'
import { Textarea } from '@/components/ui/textarea'
import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'

const createFormSchema = z.object({
  nome: z.string(),
  descricao: z.string(),
})

type CreateFormSchema = z.infer<typeof createFormSchema>

interface CreateProjetoDialogProps {
  isOpen: boolean
  setIsOpen: (isOpen: boolean) => void
}

export function CreateProjetoDialog({
  isOpen,
  setIsOpen,
}: CreateProjetoDialogProps) {
  const { toast } = useToast()

  const queryClient = useQueryClient()

  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')

  const {
    control,
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<CreateFormSchema>({
    resolver: zodResolver(createFormSchema),
  })

  const { mutateAsync: createProjetoFn } = useMutation({
    mutationFn: createProjeto,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projetos'] })
    },
  })

  async function handleCreatePessoa(data: CreateFormSchema) {
    try {
      await createProjetoFn({
        nome: data.nome,
        descricao: data.descricao,
        data_inicio: startDate,
        data_fim: endDate,
      })

      setIsOpen(false)

      reset()

      toast({
        title: 'Sucesso!',
        description: 'Projeto cadastrado com sucesso!',
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
              <Label>Nome do projeto</Label>
              <Input {...register('nome')} />
              {errors.nome && (
                <p className="text-sm text-rose-500">{errors.nome.message}</p>
              )}
            </div>

            <div className="space-y-1">
              <Label>Descrição do projeto</Label>
              <Textarea {...register('descricao')} />
              {errors.descricao && (
                <p className="text-sm text-rose-500">
                  {errors.descricao.message}
                </p>
              )}
            </div>

            <div className="flex flex-col gap-1">
              <Label htmlFor="startDate">Data de início</Label>
              <input
                type="date"
                id="startDate"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="rounded border p-2"
              />
            </div>

            <div className="flex flex-col gap-1">
              <Label htmlFor="endDate">Data de término</Label>
              <input
                type="date"
                id="endDate"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="rounded-md border p-2"
              />
            </div>
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
