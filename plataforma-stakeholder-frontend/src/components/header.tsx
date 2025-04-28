'use client'

import Link from 'next/link'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from './ui/dropdown-menu'
import { Button } from './ui/button'
import {
  ArrowLeft,
  BadgeHelp,
  BriefcaseBusiness,
  Building,
  GitFork,
  Info,
  Loader2,
  Menu,
  Settings2,
  UserRoundPlus,
  Users,
} from 'lucide-react'
import {
  DialogHeader,
  DialogFooter,
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogTitle,
} from './ui/dialog'
import { Input } from './ui/input'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { usePathname, useRouter, useSearchParams } from 'next/navigation'
import { useState } from 'react'
import { Label } from './ui/label'
import { useQueryClient } from '@tanstack/react-query'
import { NavLink } from './nav-link'

const searchStakeholder = z.object({
  documento: z.string(),
})

type SearchStakeholder = z.infer<typeof searchStakeholder>

export function Header() {
  const queryClient = useQueryClient()

  const searchParams = useSearchParams()
  const pathname = usePathname()
  const router = useRouter()

  const [isModalOpen, setIsModalOpen] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { isSubmitting },
  } = useForm<SearchStakeholder>({
    resolver: zodResolver(searchStakeholder),
  })

  async function handleSearchStakeholder(data: SearchStakeholder) {
    const params = new URLSearchParams(Array.from(searchParams.entries()))

    params.set('documento', data.documento)

    setIsModalOpen(false)

    router.replace(`/?${params.toString()}`)
  }

  return (
    <header className="fixed left-0 top-0 z-50 flex w-full items-center justify-between border-b bg-background p-4">
      <div className="flex items-center gap-2">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="icon">
              <Menu className="size-5" />
            </Button>
          </DropdownMenuTrigger>

          <DropdownMenuContent align="start" className="w-[200px] p-2">
            <DropdownMenuGroup>
              <DropdownMenuItem onClick={() => setIsModalOpen(true)}>
                <UserRoundPlus className="mr-2 size-4" />
                <span>Consultar CNPJ/CPF</span>
              </DropdownMenuItem>
            </DropdownMenuGroup>

            <DropdownMenuSeparator />

            <DropdownMenuGroup>
              <Link href="/stakeholders">
                <DropdownMenuItem>
                  <Users className="mr-2 size-4" />
                  <span>Stakeholders</span>
                </DropdownMenuItem>
              </Link>

              <Link href="/offices">
                <DropdownMenuItem>
                  <Building className="mr-2 size-4" />
                  <span>Escritórios</span>
                </DropdownMenuItem>
              </Link>

              <Link href="/lawyers">
                <DropdownMenuItem>
                  <BriefcaseBusiness className="mr-2 size-4" />
                  <span>Advogados</span>
                </DropdownMenuItem>
              </Link>

              <Link href="/empresas">
                <DropdownMenuItem>
                  <GitFork className="mr-2 size-4" />
                  <span>Empresas</span>
                </DropdownMenuItem>
              </Link>

              <Link href="/pessoas">
                <DropdownMenuItem>
                  <UserRoundPlus className="mr-2 size-4" />
                  <span>Pessoas</span>
                </DropdownMenuItem>
              </Link>
            </DropdownMenuGroup>

            <DropdownMenuSeparator />

            <DropdownMenuGroup>
              <Link href="/about">
                <DropdownMenuItem>
                  <Info className="mr-2 size-4" />
                  <span>Sobre</span>
                </DropdownMenuItem>
              </Link>

              <Link href="/help">
                <DropdownMenuItem>
                  <BadgeHelp className="mr-2 size-4" />
                  <span>Ajuda</span>
                </DropdownMenuItem>
              </Link>
            </DropdownMenuGroup>
          </DropdownMenuContent>
        </DropdownMenu>

        <NavLink href="/">
          <span className="text-lg font-semibold">Stakeholders</span>
        </NavLink>
      </div>

      <div className="flex items-center gap-2">
        <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Consultar CNPJ/CPF</DialogTitle>
              <DialogDescription>
                Digite o número do documento para consultar
              </DialogDescription>
            </DialogHeader>

            <form onSubmit={handleSubmit(handleSearchStakeholder)}>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="documento">Documento</Label>
                  <Input
                    id="documento"
                    placeholder="Digite o CNPJ ou CPF"
                    {...register('documento')}
                  />
                </div>
              </div>

              <DialogFooter className="mt-6">
                <DialogClose asChild>
                  <Button type="button" variant="outline">
                    Cancelar
                  </Button>
                </DialogClose>

                <Button type="submit" disabled={isSubmitting}>
                  {isSubmitting && (
                    <Loader2 className="mr-2 size-4 animate-spin" />
                  )}
                  Consultar
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>
    </header>
  )
}
