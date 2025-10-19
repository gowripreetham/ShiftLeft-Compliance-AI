'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useState, useEffect } from 'react'
import { LayoutDashboard, FileText, TrendingUp, Settings, BarChart3, Camera, Moon, Sun } from 'lucide-react'
import { cn } from '@/lib/utils'
import Logo from './Logo'

const navigation = [
  { path: '/', label: 'Overview', icon: LayoutDashboard },
  { path: '/findings', label: 'Issues', icon: FileText },
  { path: '/trends', label: 'Analytics', icon: TrendingUp },
  { path: '/posture', label: 'Controls', icon: BarChart3 },
  { path: '/analyze-screenshot', label: 'Scan', icon: Camera },
  { path: '/settings', label: 'Settings', icon: Settings },
]

export default function Sidebar() {
  const pathname = usePathname()
  const [isDark, setIsDark] = useState(false)

  useEffect(() => {
    // Check for saved theme preference or default to light mode
    const savedTheme = localStorage.getItem('theme')
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    const shouldBeDark = savedTheme === 'dark' || (!savedTheme && prefersDark)
    
    setIsDark(shouldBeDark)
    document.documentElement.classList.toggle('dark', shouldBeDark)
  }, [])

  const toggleTheme = () => {
    const newTheme = !isDark
    setIsDark(newTheme)
    localStorage.setItem('theme', newTheme ? 'dark' : 'light')
    document.documentElement.classList.toggle('dark', newTheme)
  }

  return (
    <div className="w-64 bg-white dark:bg-black border-r border-[#DDDDDD] dark:border-[#333333] flex flex-col">
      <div className="p-4 border-b border-[#DDDDDD] dark:border-[#333333]">
        <div className="flex items-center space-x-3">
          <div className="flex items-center justify-center">
            <Logo />
          </div>
          <div>
            <h1 className="text-base font-semibold text-black dark:text-white">Shift-Left</h1>
            <p className="text-xs text-black/60 dark:text-white/60 font-medium">Command Center</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 p-3 space-y-0.5">
        {navigation.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.path

          return (
            <Link
              key={item.path}
              href={item.path}
              className={cn(
                'flex items-center space-x-3 px-3 py-2 text-sm font-medium',
                isActive
                  ? 'bg-black dark:bg-white text-white dark:text-black'
                  : 'text-black dark:text-white hover:bg-[#F6F6F6] dark:hover:bg-[#1A1A1A]'
              )}
            >
              <Icon className="h-4 w-4" />
              <span>{item.label}</span>
            </Link>
          )
        })}
      </nav>

      {/* Theme Toggle */}
      <div className="p-3 border-t border-[#DDDDDD] dark:border-[#333333]">
        <button
          onClick={toggleTheme}
          className="w-full flex items-center space-x-3 px-3 py-2 text-sm font-medium text-black dark:text-white hover:bg-[#F6F6F6] dark:hover:bg-[#1A1A1A]"
        >
          {isDark ? (
            <>
              <Moon className="h-4 w-4" />
              <span>Dark Mode</span>
            </>
          ) : (
            <>
              <Sun className="h-4 w-4" />
              <span>Light Mode</span>
            </>
          )}
        </button>
      </div>
    </div>
  )
}

