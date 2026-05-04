import { AlertTriangle } from 'lucide-react'
import type { DeprecatedProduct } from '@/lib/types'

interface DeprecatedBannerProps {
  product: DeprecatedProduct
}

export function DeprecatedBanner({ product }: DeprecatedBannerProps) {
  return (
    <div className="rounded-lg border border-amber-300 bg-amber-50 dark:bg-amber-950/20 dark:border-amber-800 p-4 space-y-1">
      <div className="flex items-start gap-2">
        <AlertTriangle className="h-4 w-4 text-amber-600 mt-0.5 shrink-0" />
        <div>
          <h4 className="font-medium text-sm text-amber-900 dark:text-amber-300">
            {product.name}
          </h4>
          <p className="text-xs text-amber-700 dark:text-amber-400">{product.reason}</p>
        </div>
      </div>
    </div>
  )
}
