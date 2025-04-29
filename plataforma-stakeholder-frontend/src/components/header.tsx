'use client'

// import { AccountMenu } from './account-menu'

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
              <DropdownMenuItem className="outline-none">
                <BadgeHelp className="mr-2 size-4" />
                <span>Ajuda</span>
              </DropdownMenuItem>

              <DropdownMenuItem className="outline-none">
                <Info className="mr-2 size-4" />
                <span>Sobre</span>
              </DropdownMenuItem>
            </DropdownMenuGroup>
          </DropdownMenuContent>
        </DropdownMenu>

        <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>Consultar CNPJ</DialogTitle>
              <DialogDescription>
                Informe um CNPJ ou CPF para buscar os relacionamentos de um
                stakeholder.
              </DialogDescription>
            </DialogHeader>

            <form
              onSubmit={handleSubmit(handleSearchStakeholder)}
              className="space-y-4"
            >
              <div className="space-y-1">
                <Label htmlFor="documento">Digite um CNPJ/CPF</Label>
                <Input
                  id="documento"
                  placeholder="00.000.000/0000-00"
                  className="col-span-3"
                  {...register('documento')}
                />
              </div>

              <DialogFooter>
                <DialogClose asChild>
                  <Button variant="ghost" type="button" className="w-full">
                    Cancelar
                  </Button>
                </DialogClose>
                <Button type="submit" className="w-full">
                  {isSubmitting ? (
                    <Loader2 className="size-4 animate-spin" />
                  ) : (
                    'Continuar'
                  )}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>

        <div className="flex items-center gap-2">
          <NavLink href="/">Inicio</NavLink>
          <NavLink href="/stakeholders">Stakeholders</NavLink>
          <NavLink href="/offices">Escritórios</NavLink>
          <NavLink href="/lawyers">Advogados</NavLink>
          <NavLink href="/empresas">Empresas</NavLink>
          <NavLink href="/pessoas">Pessoas</NavLink>
          <NavLink href="/projetos">Projetos</NavLink>
          <NavLink href="/logs">Consultas</NavLink>
        </div>
      </div>

      {/* <AccountMenu /> */}
    </header>
  )
}
