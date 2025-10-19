import type { Metadata } from 'next'
import './globals.css'
import { Toaster } from '@/components/ui/toaster'
import Sidebar from '@/components/Sidebar'

export const metadata: Metadata = {
  title: 'Shift-Left Compliance Dashboard',
  description: 'Real-time compliance monitoring and risk management',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="body-font">
        <div className="flex h-screen overflow-hidden">
          <Sidebar />
          <main className="flex-1 overflow-y-auto">
            {children}
          </main>
        </div>
        <Toaster />
      </body>
    </html>
  )
}

