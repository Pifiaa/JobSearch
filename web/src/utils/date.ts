export function timeAgo(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = Math.floor((now.getTime() - date.getTime()) / 1000)

  if (diff < 60)                  return 'hace un momento'
  if (diff < 3600)                return `hace ${Math.floor(diff / 60)}m`
  if (diff < 86400)               return `hace ${Math.floor(diff / 3600)}h`
  if (diff < 86400 * 7)           return `hace ${Math.floor(diff / 86400)}d`
  if (diff < 86400 * 30)          return `hace ${Math.floor(diff / (86400 * 7))}sem`

  return date.toLocaleDateString('es-CO', { day: 'numeric', month: 'short' })
}