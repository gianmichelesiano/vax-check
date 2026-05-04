'use client'

import useSWR from 'swr'
import { api } from '@/lib/api'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import type { VaccineProduct } from '@/lib/types'
import { useTranslations } from '@/i18n/I18nProvider'

interface ProductSelectorProps {
  value: string
  onChange: (value: string) => void
}

export function ProductSelector({ value, onChange }: ProductSelectorProps) {
  const { t } = useTranslations()

  const { data: products, isLoading } = useSWR('products', () => api.catalog.products(), {
    revalidateOnFocus: false,
    revalidateOnReconnect: false,
    dedupingInterval: 600000,
  })

  return (
    <Select value={value} onValueChange={onChange}>
      <SelectTrigger>
        <SelectValue placeholder={isLoading ? t('productSelector.loading') : t('productSelector.placeholder')} />
      </SelectTrigger>
      <SelectContent>
        {(products ?? []).sort((a, b) => a.name.localeCompare(b.name)).map((p) => (
          <SelectItem key={p.name} value={p.name}>
            <div className="flex items-center gap-2 min-h-[44px]">
              <span className="font-medium">{p.name}</span>
              <span className="text-xs text-muted-foreground">
                {p.antigens.join(' · ')}
              </span>
            </div>
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}
