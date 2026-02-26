'use client'
import { useEffect, useState } from 'react'

export function Clock() {
  const [mounted, setMounted] = useState(false)
  const [time, setTime] = useState('')

  useEffect(() => {
    setMounted(true)
    const updateTime = () => {
      setTime(new Date().toLocaleTimeString())
    }
    updateTime()
    const interval = setInterval(updateTime, 1000)
    return () => clearInterval(interval)
  }, [])

  if (!mounted) return <span>--:--:--</span>

  return <span suppressHydrationWarning>{time}</span>
}
