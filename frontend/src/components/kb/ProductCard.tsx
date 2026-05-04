import type { KBProduct } from '@/lib/types'
import { Badge } from '@/components/ui/badge'

interface ProductCardProps {
  product: KBProduct
}

function ageRangeLabel(range?: Record<string, number>): string {
  if (!range) return ''
  const minM = range.min_months
  const maxM = range.max_months
  if (minM != null && maxM != null) {
    if (maxM >= 12 * 100) return `≥ ${Math.round(minM / 12)} anni`
    if (maxM >= 12) return `${minM} mesi – ${Math.round(maxM / 12)} anni`
    return `${minM} – ${maxM} mesi`
  }
  return ''
}

export function ProductCard({ product }: ProductCardProps) {
  return (
    <div className="rounded-lg border p-4 space-y-2">
      <div>
        <h4 className="font-medium text-sm">{product.name}</h4>
        {product.aliases.length > 0 && (
          <p className="text-xs text-muted-foreground">{product.aliases.join(', ')}</p>
        )}
      </div>

      <div className="flex flex-wrap gap-1">
        {product.antigens.map((ag) => (
          <Badge key={ag} variant="secondary" className="text-[10px] px-1.5 py-0">
            {ag}
          </Badge>
        ))}
      </div>

      <div className="flex items-center justify-between text-xs text-muted-foreground">
        {product.manufacturer && <span>{product.manufacturer}</span>}
        {ageRangeLabel(product.age_range) && <span>{ageRangeLabel(product.age_range)}</span>}
      </div>

      {product.notes && (
        <p className="text-xs text-muted-foreground italic">{product.notes}</p>
      )}
    </div>
  )
}
