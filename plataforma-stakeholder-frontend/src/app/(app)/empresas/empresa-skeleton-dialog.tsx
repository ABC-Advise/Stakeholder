'use client'

import {
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Skeleton } from '@/components/ui/skeleton'

export function EmpresaSkeletonDialog() {
  return (
    <div>
      <DialogHeader>
        <Skeleton className="h-5 w-52" />
        <Skeleton className="h-4 w-60" />
      </DialogHeader>

      <div className="my-4 space-y-4">
        <div className="space-y-1">
          <Skeleton className="h-5 w-24" />
          <Skeleton className="h-10 w-full" />
        </div>
        <div className="space-y-1">
          <Skeleton className="h-5 w-24" />
          <Skeleton className="h-10 w-full" />
        </div>

        <div className="space-y-1">
          <Skeleton className="h-5 w-24" />
          <Skeleton className="h-10 w-full" />
        </div>
      </div>

      <DialogFooter className="flex w-full justify-end">
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-10 w-full" />
      </DialogFooter>
    </div>
  )
}
