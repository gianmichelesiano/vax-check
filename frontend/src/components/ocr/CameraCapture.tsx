'use client'

import { useRef, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Camera, RotateCcw, Check, Image as ImageIcon } from 'lucide-react'
import { useTranslations } from '@/i18n/I18nProvider'

interface CameraCaptureProps {
  onCapture: (file: File) => void
  onCancel: () => void
}

export function CameraCapture({ onCapture, onCancel }: CameraCaptureProps) {
  const { t } = useTranslations()
  const [preview, setPreview] = useState<string | null>(null)
  const [capturedFile, setCapturedFile] = useState<File | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setCapturedFile(file)
    setPreview(URL.createObjectURL(file))
  }

  const handleRetake = () => {
    setPreview(null)
    setCapturedFile(null)
    if (inputRef.current) {
      inputRef.current.value = ''
    }
  }

  if (!preview) {
    return (
      <div className="flex flex-col items-center gap-4 py-8">
        <div
          onClick={() => inputRef.current?.click()}
          className="flex h-48 w-full cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-muted-foreground/30 bg-muted/30 transition-colors hover:border-primary/50"
        >
          <Camera className="mb-2 h-12 w-12 text-muted-foreground" />
          <p className="text-sm font-medium text-muted-foreground">{t('cameraCapture.prompt')}</p>
          <p className="mt-1 text-xs text-muted-foreground/70">
            {t('cameraCapture.hint')}
          </p>
        </div>
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          capture="environment"
          className="hidden"
          onChange={handleFileChange}
        />
        <div className="flex gap-2">
          <Button variant="outline" onClick={onCancel}>
            {t('cameraCapture.cancel')}
          </Button>
          <Button onClick={() => inputRef.current?.click()}>
            <ImageIcon className="mr-2 h-4 w-4" />
            {t('cameraCapture.choosePhoto')}
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col items-center gap-4 py-4">
      <div className="relative max-h-[60vh] w-full overflow-hidden rounded-xl">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={preview}
          alt="Anteprima libretto"
          className="mx-auto max-h-[60vh] w-auto rounded-xl object-contain"
        />
      </div>
      <p className="text-xs text-muted-foreground">
        {t('cameraCapture.privacyNote')}
      </p>
      <div className="flex w-full gap-2">
        <Button variant="outline" onClick={handleRetake} className="flex-1">
          <RotateCcw className="mr-2 h-4 w-4" />
          {t('cameraCapture.retake')}
        </Button>
        <Button onClick={() => capturedFile && onCapture(capturedFile)} className="flex-1">
          <Check className="mr-2 h-4 w-4" />
          {t('cameraCapture.usePhoto')}
        </Button>
      </div>
    </div>
  )
}
