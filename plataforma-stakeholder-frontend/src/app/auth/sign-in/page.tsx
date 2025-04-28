import Image from 'next/image'
import Link from 'next/link'

import Logo from '@/assets/logo.svg'
import { AuthenticateWithGoogleButton } from './authenticate-with-google-button'

export default function SignIn() {
  return (
    <div className="space-y-4 text-center">
      <Image src={Logo} alt="" className="mx-auto size-20" />
      <div className="space-y-1">
        <h1 className="text-3xl font-semibold tracking-tight">Entrar</h1>
        <p className="text-muted-foreground">
          Acesse a plataforma com sua conta.
        </p>
      </div>

      <AuthenticateWithGoogleButton />

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
