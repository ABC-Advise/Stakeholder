'use client'

import { cn } from '@/lib/utils'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { ComponentProps } from 'react'

interface NavLinkProps extends ComponentProps<typeof Link> {}

export function NavLink(props: NavLinkProps) {
  const pathname = usePathname()

  const isCurrent = props.href.toString() === pathname

  return (
    <Link
      data-current={isCurrent}
      {...props}
      className={cn(
        'rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-muted',
        isCurrent && 'bg-muted text-accent-foreground',
      )}
    />
  )
}
