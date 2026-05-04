'use client'

import { useMemo, useState } from 'react'
import { Input } from '@/components/ui/input'
import { Search } from 'lucide-react'
import { ProductCard } from './ProductCard'
import { DeprecatedBanner } from './DeprecatedBanner'
import type { KBProduct, DeprecatedProduct } from '@/lib/types'
import { useTranslations } from '@/i18n/I18nProvider'

interface CatalogoTabProps {
  products: KBProduct[]
  deprecatedProducts: DeprecatedProduct[]
}

export function CatalogoTab({ products, deprecatedProducts }: CatalogoTabProps) {
  const { t } = useTranslations()
  const [search, setSearch] = useState('')

  const filtered = useMemo(() => {
    if (!search) return products
    const q = search.toLowerCase()
    return products.filter(
      (p) =>
        p.name.toLowerCase().includes(q) ||
        p.aliases.some((a) => a.toLowerCase().includes(q)) ||
        p.manufacturer?.toLowerCase().includes(q) ||
        p.antigens.some((ag) => ag.toLowerCase().includes(q)),
    )
  }, [products, search])

  return (
    <div className="space-y-4">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder={t('catalogo.searchPlaceholder')}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-10"
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {filtered.map((p) => (
          <ProductCard key={p.name} product={p} />
        ))}
      </div>

      {filtered.length === 0 && (
        <p className="text-center text-sm text-muted-foreground py-8">
          {t('catalogo.noResults')}
        </p>
      )}

      {deprecatedProducts.length > 0 && (
        <div className="space-y-2 pt-4 border-t">
          <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
            {t('catalogo.deprecatedTitle', { count: deprecatedProducts.length })}
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {deprecatedProducts.map((d) => (
              <DeprecatedBanner key={d.name} product={d} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
