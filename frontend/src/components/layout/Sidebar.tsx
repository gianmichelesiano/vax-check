'use client'

import { useMemo } from 'react'
import { cn } from '@/lib/utils'
import type { Patient } from '@/lib/types'

const ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('')

interface SidebarProps {
  patients: Patient[]
  selectedLetter: string | null
  onLetterSelect: (letter: string | null) => void
}

export function Sidebar({ patients, selectedLetter, onLetterSelect }: SidebarProps) {
  const counts = useMemo(() => {
    const map: Record<string, number> = {}
    for (const p of patients) {
      const l = p.family_name[0]?.toUpperCase() ?? '#'
      map[l] = (map[l] ?? 0) + 1
    }
    return map
  }, [patients])

  return (
    <aside className="hidden md:flex flex-col w-20 border-r bg-card shrink-0 overflow-y-auto">
      <div className="flex flex-col gap-0.5 p-2 pt-3">
        {/* All patients button */}
        <button
          onClick={() => onLetterSelect(null)}
          className={cn(
            'w-full rounded-md py-1.5 text-xs font-semibold transition-colors',
            selectedLetter === null
              ? 'bg-primary text-primary-foreground'
              : 'text-muted-foreground hover:bg-accent hover:text-foreground',
          )}
        >
          Tutti
        </button>

        <div className="my-1 border-t" />

        {ALPHABET.map((letter) => {
          const count = counts[letter] ?? 0
          const active = selectedLetter === letter
          return (
            <button
              key={letter}
              disabled={count === 0}
              onClick={() => onLetterSelect(letter)}
              className={cn(
                'relative w-full rounded-md py-1.5 text-sm font-bold transition-colors',
                active
                  ? 'bg-primary text-primary-foreground'
                  : count > 0
                    ? 'text-foreground hover:bg-accent'
                    : 'text-muted-foreground/30 cursor-default',
              )}
            >
              {letter}
              {count > 0 && (
                <span
                  className={cn(
                    'absolute right-1.5 top-1/2 -translate-y-1/2 text-[9px] font-normal',
                    active ? 'text-primary-foreground/70' : 'text-muted-foreground',
                  )}
                >
                  {count}
                </span>
              )}
            </button>
          )
        })}
      </div>
    </aside>
  )
}
