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
import { getOffices } from '@/http/offices/get-offices'
import { useQuery } from '@tanstack/react-query'
import { Loader2 } from 'lucide-react'
import { useState } from 'react'
import { Lawyer } from './columns'
import { getLawyers } from '@/http/lawyers/get-lawyers'
import { LawyerSkeletonDialog } from './lawyer-skeleton-dialog'

interface LawyerDetailsDialogProps {
  lawyer: Lawyer
}

export function LawyerDetailsDialog({ lawyer }: LawyerDetailsDialogProps) {
  const [isOpen, setIsOpen] = useState(false)

  const { data, isLoading } = useQuery({
    queryKey: ['lawyers', lawyer.advogado_id],
    queryFn: () => getLawyers({ advogado_id: lawyer.advogado_id }),
    enabled: isOpen,
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
          data.advogados.map((lawyer) => {
            return (
              <form key={lawyer.advogado_id}>
                <DialogHeader>
                  <DialogTitle>
                    Visualizar {lawyer.firstname} {lawyer.lastname}
                  </DialogTitle>
                  <DialogDescription>Detalhes do advogado</DialogDescription>
                </DialogHeader>

                <div className="my-4 space-y-4">
                  <div className="space-y-1">
                    <Label>Primeiro nome</Label>
                    <Input defaultValue={lawyer.firstname} disabled />
                  </div>
                  <div className="space-y-1">
                    <Label>Último nome</Label>
                    <Input defaultValue={lawyer.lastname} disabled />
                  </div>
                  <div className="space-y-1">
                    <Label>CPF</Label>
                    <Input
                      defaultValue={
                        lawyer.cpf !== 'None' ? lawyer.cpf : 'Não informado'
                      }
                      disabled
                    />
                  </div>
                  <div className="space-y-1">
                    <Label>OAB</Label>
                    <Input defaultValue={lawyer.oab} disabled />
                  </div>
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

        {isLoading && <LawyerSkeletonDialog />}
      </DialogContent>
    </Dialog>
  )
}
