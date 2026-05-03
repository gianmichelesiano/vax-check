'use client'

import { cn } from '@/lib/utils'
import { Menu, Users, FlaskConical, Settings } from 'lucide-react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useState } from 'react'

export function TopNav() {
  const pathname = usePathname()
  const [open, setOpen] = useState(false)

  return (
    <header className="sticky top-0 z-40 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-14 items-center px-4">
        <button
          className="mr-3 md:hidden min-h-[44px] min-w-[44px] flex items-center justify-center"
          onClick={() => setOpen(!open)}
          aria-label="Menu"
        >
          <Menu className="h-5 w-5" />
        </button>

        <Link href="/" className="flex items-center space-x-2">
          <FlaskConical className="h-6 w-6 text-primary" />
          <span className="font-bold text-lg">VaxCheck</span>
        </Link>

        <nav className="hidden md:flex items-center space-x-4 ml-8">
          <Link
            href="/"
            className={cn(
              'text-sm font-medium transition-colors hover:text-primary min-h-[44px] flex items-center px-2',
              pathname === '/' ? 'text-primary' : 'text-muted-foreground',
            )}
          >
            <Users className="h-4 w-4 mr-2" />
            Pazienti
          </Link>
          <Link
            href="/impostazioni"
            className={cn(
              'text-sm font-medium transition-colors hover:text-primary min-h-[44px] flex items-center px-2',
              pathname === '/impostazioni' ? 'text-primary' : 'text-muted-foreground',
            )}
          >
            <Settings className="h-4 w-4 mr-2" />
            Impostazioni
          </Link>
        </nav>

        {open && (
          <div className="absolute top-14 left-0 right-0 border-b bg-background p-4 md:hidden z-50">
            <nav className="flex flex-col space-y-2">
              <Link
                href="/"
                className={cn(
                  'flex items-center text-sm font-medium min-h-[44px] px-2 rounded-md',
                  pathname === '/' ? 'bg-primary/10 text-primary' : 'text-muted-foreground',
                )}
                onClick={() => setOpen(false)}
              >
                <Users className="h-4 w-4 mr-2" />
                Pazienti
              </Link>
              <Link
                href="/impostazioni"
                className={cn(
                  'flex items-center text-sm font-medium min-h-[44px] px-2 rounded-md',
                  pathname === '/impostazioni' ? 'bg-primary/10 text-primary' : 'text-muted-foreground',
                )}
                onClick={() => setOpen(false)}
              >
                <Settings className="h-4 w-4 mr-2" />
                Impostazioni
              </Link>
            </nav>
          </div>
        )}
      </div>
    </header>
  )
}
