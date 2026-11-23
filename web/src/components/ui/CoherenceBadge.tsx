interface Props {
  vacanteCoherente: boolean | null
}

export default function CoherenceBadge({ vacanteCoherente }: Props) {
  if (vacanteCoherente !== false) return null

  return (
    <span
      title="La IA detectó varios cargos distintos mezclados en esta vacante"
      className="text-xs font-medium px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 flex items-center gap-1"
    >
      ⚠️ Varios cargos
    </span>
  )
}
