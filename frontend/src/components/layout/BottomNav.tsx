'use client'

import { cn } from '@/lib/utils'
import { Users, BookText, Settings } from 'lucide-react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useTranslations } from '@/i18n/I18nProvider'

export function BottomNav() {
  const pathname = usePathname()
  const { t } = useTranslations()

  const tabs = [
    { href: '/', label: t('nav.patients'), icon: Users },
    { href: '/riferimenti', label: t('nav.references'), icon: BookText },
    { href: '/impostazioni', label: t('nav.settings'), icon: Settings },
  ]

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-40 border-t bg-background pb-safe">
      <div className="flex h-14">
        {tabs.map((tab) => {
          const Icon = tab.icon
          const active = pathname === tab.href
          return (
            <Link
              key={tab.href}
              href={tab.href}
              className={cn(
                'flex flex-1 flex-col items-center justify-center min-h-[56px] text-xs font-medium transition-colors',
                active ? 'text-primary' : 'text-muted-foreground',
              )}
            >
              <Icon className="h-5 w-5 mb-1" />
              {tab.label}
            </Link>
          )
        })}
      </div>
    </nav>
  )
}
