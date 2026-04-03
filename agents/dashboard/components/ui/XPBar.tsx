import React from 'react'

export function XPBar({
  xp,
  maxXp,
  level,
}: {
  xp:    number
  maxXp: number
  level: number
}): React.JSX.Element {
  // Guard: avoid NaN / Infinity when maxXp is 0, null, or undefined
  const safePct = maxXp > 0 ? Math.min(100, Math.round((xp / maxXp) * 100)) : 0

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, color: 'var(--text-secondary)', marginBottom: 2 }}>
        <span>LVL {level}</span>
        <span>{xp} / {maxXp} XP</span>
      </div>
      <div
        className="xp-bar"
        role="progressbar"
        aria-valuenow={safePct}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={`${safePct}% to next level`}
      >
        <div className="xp-bar-fill" style={{ width: `${safePct}%` }} />
      </div>
    </div>
  )
}
