export function generateStaticParams() {
  return [{ id: 'placeholder' }]
}

export default function ReportLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
