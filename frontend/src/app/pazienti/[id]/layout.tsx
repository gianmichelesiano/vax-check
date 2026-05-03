export function generateStaticParams() {
  return [{ id: 'placeholder' }]
}

export default function PatientLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
