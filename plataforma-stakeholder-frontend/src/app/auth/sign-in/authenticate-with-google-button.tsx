'use client'

import { Button } from '@/components/ui/button'
import GoogleIcon from '@/assets/google-icon.svg'
import Image from 'next/image'
import { signIn } from 'next-auth/react'

export function AuthenticateWithGoogleButton() {
  const handleGoogleSignIn = async () => {
    signIn('google', { callbackUrl: '/' })
  }

  return (
    <Button onClick={handleGoogleSignIn} variant="outline" className="w-full">
      <Image src={GoogleIcon} alt="" className="mr-2 size-5" />
      <span>Continuar com o Google</span>
    </Button>
  )
}
