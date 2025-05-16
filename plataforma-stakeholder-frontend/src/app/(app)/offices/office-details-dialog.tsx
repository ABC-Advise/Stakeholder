'use client';

import { useQuery } from '@tanstack/react-query';
import { Loader2 } from 'lucide-react';
import { useState } from 'react';

import { Button } from '@/components/ui/button';
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
import { getOffices } from '@/http/offices/get-offices';

import { Office } from './columns';
import { OfficeSkeletonDialog } from './office-skeleton-dialog';

interface EditOfficeDialogProps {
  office: Office;
}

export function OfficeDetailsDialog({ office }: EditOfficeDialogProps) {
  const [isOpen, setIsOpen] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ['offices', office.escritorio_id],
    queryFn: () => getOffices({ escritorio_id: office.escritorio_id }),
    enabled: isOpen,
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
          data.escritorios.map(office => {
            return (
              <form key={office.escritorio_id}>
                <DialogHeader>
                  <DialogTitle>Visualizar {office.nome_fantasia}</DialogTitle>
                  <DialogDescription>Detalhes do escritório</DialogDescription>
                </DialogHeader>

                <div className="my-4 space-y-4">
                  <div className="space-y-1">
                    <Label>Nome fantansia</Label>
                    <Input defaultValue={office.nome_fantasia} disabled />
                  </div>
                  <div className="space-y-1">
                    <Label>Razão social</Label>
                    <Input defaultValue={office.razao_social} disabled />
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
            );
          })}

        {isLoading && <OfficeSkeletonDialog />}
      </DialogContent>
    </Dialog>
  );
}
