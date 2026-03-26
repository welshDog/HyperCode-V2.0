import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'HyperCode Mission Control',
  description: 'BROski\u221e — Full-Screen Agent Command Centre',
  viewport: 'width=device-width, initial-scale=1',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}): React.JSX.Element {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="hyper-root">
        {children}
      </body>
    </html>
  )
}
