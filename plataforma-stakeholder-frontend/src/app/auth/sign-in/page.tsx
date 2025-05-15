import Image from 'next/image'
import Link from 'next/link'

import Logo from '@/assets/logo.svg'

export default function SignIn() {
  return (
    <div className="space-y-4 text-center">
      <Image src={Logo} alt="" className="mx-auto size-20" />
      <div className="space-y-1">
        <h1 className="text-3xl font-semibold tracking-tight">Entrar</h1>
        <p className="text-sm text-gray-600">Faça login para continuar</p>
      </div>

      <p className="text-sm text-muted-foreground">
        Ao clicar em continuar, você concorda com nossos{' '}
        <Link href="" className="underline">
          Termos de Serviço
        </Link>{' '}
        e{' '}
        <Link href="" className="underline">
          Política de Privacidade
        </Link>
        .
      </p>
    </div>
  )
}
