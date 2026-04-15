import type { ReactNode } from 'react'

export const metadata = {
  title: 'Payment Site Donation Insights',
}

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body style={{ margin: 0, fontFamily: 'Segoe UI, Arial, sans-serif' }}>{children}</body>
    </html>
  )
}
