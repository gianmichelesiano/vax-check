'use client'

import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Shield, AlertTriangle } from 'lucide-react'
import { useTranslations } from '@/i18n/I18nProvider'

interface ConsentModalProps {
  open: boolean
  onAccept: () => void
  onManual: () => void
}

export function ConsentModal({ open, onAccept, onManual }: ConsentModalProps) {
  const { t } = useTranslations()

  return (
    <Dialog open={open} onOpenChange={() => {}}>
      <DialogContent className="max-w-sm">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-blue-600" />
            {t('consentModal.title')}
          </DialogTitle>
        </DialogHeader>
        <div className="space-y-3 text-sm text-muted-foreground">
          <p>
            {t('consentModal.intro', { provider: 'Anthropic Claude' })}
          </p>
          <ul className="list-disc space-y-1 pl-4">
            <li>{t('consentModal.detail1')}</li>
            <li>{t('consentModal.detail2')}</li>
            <li>{t('consentModal.detail3')}</li>
            <li>{t('consentModal.detail4')}</li>
          </ul>
          <div className="flex items-start gap-2 rounded-md bg-amber-50 p-3 text-amber-800">
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
            <p className="text-xs">
              {t('consentModal.altText')}
            </p>
          </div>
        </div>
        <div className="flex flex-col gap-2 pt-2">
          <Button onClick={onAccept} className="w-full">
            {t('consentModal.accept')}
          </Button>
          <Button variant="outline" onClick={onManual} className="w-full">
            {t('consentModal.manual')}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
