import type { Metadata } from 'next'
import { TopNav } from '@/components/layout/TopNav'
import { BottomNav } from '@/components/layout/BottomNav'
import './globals.css'

export const metadata: Metadata = {
  title: 'VaxCheck',
  description: 'Analisi vaccinale per farmacie svizzere',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="it">
      <body className="min-h-screen bg-background font-sans antialiased">
        <TopNav />
        <main className="pb-20 md:pb-4">{children}</main>
        <BottomNav />
      </body>
    </html>
  )
}
