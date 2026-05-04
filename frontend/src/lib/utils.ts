import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function initials(givenName: string, familyName: string): string {
  return `${givenName.charAt(0)}${familyName.charAt(0)}`.toUpperCase()
}

const avatarColors = [
  'bg-blue-100 text-blue-700',
  'bg-green-100 text-green-700',
  'bg-amber-100 text-amber-700',
  'bg-purple-100 text-purple-700',
  'bg-rose-100 text-rose-700',
  'bg-teal-100 text-teal-700',
]

export function avatarColor(name: string): string {
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  return avatarColors[Math.abs(hash) % avatarColors.length]
}

export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('de-CH', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

export function ageLabel(
  years: number,
  t: (key: string, params?: Record<string, string | number>) => string,
): string {
  if (years < 1) return t('common.lessThanYear')
  if (years === 1) return t('common.year')
  return t('common.years', { years })
}

export function sexLabel(
  sex: string,
  t: (key: string, params?: Record<string, string | number>) => string,
): string {
  if (sex === 'M') return t('common.male')
  if (sex === 'F') return t('common.female')
  return t('common.other')
}
