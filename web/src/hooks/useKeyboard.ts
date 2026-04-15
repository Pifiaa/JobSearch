import { useEffect } from 'react'

interface KeyMap {
  [key: string]: () => void
}

export function useKeyboard(keyMap: KeyMap, active = true) {
  useEffect(() => {
    if (!active) return

    function handleKeyDown(e: KeyboardEvent) {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLSelectElement) return
      const handler = keyMap[e.key]
      if (handler) {
        e.preventDefault()
        handler()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [keyMap, active])
}