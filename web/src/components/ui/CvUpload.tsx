import { useEffect, useRef, useState } from 'react'

interface CvInfo {
  exists: boolean
  size_kb?: number
  last_modified?: string
}

export default function CvUpload() {
  const [info, setInfo]       = useState<CvInfo | null>(null)
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState<{ text: string; ok: boolean } | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    fetch('/api/cv/info')
      .then((r) => r.json())
      .then(setInfo)
      .catch(() => setInfo({ exists: false }))
  }, [])

  async function handleFile(file: File) {
    if (!file) return
    setUploading(true)
    setMessage(null)
    try {
      const form = new FormData()
      form.append('cv', file)
      const res = await fetch('/api/cv/upload', { method: 'POST', body: form })
      const data = await res.json()
      if (!res.ok) {
        setMessage({ text: data.error ?? 'Error al subir', ok: false })
        return
      }
      setInfo({ exists: true, size_kb: data.size_kb, last_modified: data.last_modified })
      setMessage({ text: '✓ CV actualizado', ok: true })
    } catch {
      setMessage({ text: 'Error de red', ok: false })
    } finally {
      setUploading(false)
    }
  }

  const label = info?.exists
    ? `CV · ${info.size_kb} KB`
    : 'Subir CV'

  return (
    <div className="flex items-center gap-2">
      {message && (
        <span className={`text-xs px-2 py-1 rounded-full ${message.ok ? 'text-green-600 bg-green-50' : 'text-red-600 bg-red-50'}`}>
          {message.text}
        </span>
      )}
      <button
        onClick={() => inputRef.current?.click()}
        disabled={uploading}
        title={info?.last_modified ? `Modificado: ${info.last_modified}` : undefined}
        className="text-sm border border-gray-200 text-gray-600 px-3 py-1.5 rounded-lg hover:border-blue-300 hover:text-blue-600 disabled:opacity-50 transition-colors font-medium"
      >
        {uploading ? '⏳ Subiendo...' : `📄 ${label}`}
      </button>
      <input
        ref={inputRef}
        type="file"
        accept=".pdf"
        className="hidden"
        onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
      />
    </div>
  )
}