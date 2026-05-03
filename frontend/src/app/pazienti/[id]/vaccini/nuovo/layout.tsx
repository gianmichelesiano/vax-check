export function generateStaticParams() {
  return [{ id: 'placeholder' }]
}

export default function VaccinationLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
