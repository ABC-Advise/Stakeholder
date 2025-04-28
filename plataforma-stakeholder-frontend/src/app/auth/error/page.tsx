import { Button } from '@/components/ui/button'
import Image from 'next/image'
import Link from 'next/link'

import Logo from '@/assets/logo.svg'

export default function Error() {
  return (
    <div className="flex w-full max-w-[400px] flex-col gap-4 p-4 dark:bg-zinc-900">
      <div className="flex flex-col items-center gap-2">
        <Image src={Logo} alt="" className="mx-auto size-20" />
        <h1 className="text-2xl font-semibold">Email inválido</h1>
        <span className="text-sm text-muted-foreground">
          O domínio do seu e-mail não é permitido.
        </span>
      </div>

      <Link href="/auth/sign-in">
        <Button className="mt-4 w-full" variant="outline">
          Voltar para o login
        </Button>
      </Link>
    </div>
  )
}
