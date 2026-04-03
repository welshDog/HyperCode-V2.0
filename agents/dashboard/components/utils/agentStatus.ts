/**
 * Normalises the many status strings that agents can emit
 * into a simple boolean "is this agent healthy?"
 *
 * Accepted healthy values (case-insensitive):
 *   'healthy' | 'online' | 'running' | 'ok'
 */
export function isAgentHealthy(status: string | undefined | null): boolean {
  if (!status) return false
  const s = status.trim().toLowerCase()
  return s === 'healthy' || s === 'online' || s === 'running' || s === 'ok'
}
