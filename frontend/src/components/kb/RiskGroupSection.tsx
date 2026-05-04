'use client'

import { useState } from 'react'
import { ChevronDown, ChevronRight } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import type { RiskGroupItem } from '@/lib/types'

interface RiskGroupSectionProps {
  title: string
  items: RiskGroupItem[]
  defaultOpen?: boolean
}

export function RiskGroupSection({ title, items, defaultOpen = false }: RiskGroupSectionProps) {
  const [open, setOpen] = useState(defaultOpen)

  return (
    <div className="rounded-lg border">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center justify-between w-full px-4 py-3 text-sm font-medium min-h-[44px] hover:bg-muted/50 transition-colors"
      >
        <span>
          {title} <span className="text-muted-foreground">({items.length})</span>
        </span>
        {open ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
      </button>

      {open && (
        <div className="px-4 pb-3 space-y-2">
          {items.map((item) => (
            <div
              key={item.code}
              className="rounded-md border bg-card p-3 space-y-1.5"
            >
              <div className="text-sm font-medium">{item.label}</div>
              {item.severity_threshold && (
                <p className="text-xs text-muted-foreground">{item.severity_threshold}</p>
              )}
              {item.note && (
                <p className="text-xs text-muted-foreground italic">{item.note}</p>
              )}
              <div className="flex flex-wrap gap-1 pt-1">
                {item.recommended.map((v) => (
                  <Badge key={v} variant="outline" className="text-[10px] px-1.5 py-0">
                    {v}
                  </Badge>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
