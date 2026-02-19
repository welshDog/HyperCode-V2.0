import { describe, it, expect, vi, beforeEach } from 'vitest'

async function dispatchTask(fetchImpl: typeof fetch, agentsBase: string) {
  const payload = { prompt: 'Write a Python function add(a,b) that returns sum' }
  const listResp = await fetchImpl(`${agentsBase}/`)
  const agents = await listResp.json()
  const coder = (agents as any[]).find(a => a.name === 'Coder')
  if (!coder) throw new Error('Coder agent not found')
  const target = `${agentsBase}/${coder.id}/send`
  const resp = await fetchImpl(target, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  return resp.status
}

describe('Admin Button dispatch flow', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('validates payload and parses 202 response', async () => {
    const fetchMock = vi.fn()
    fetchMock
      .mockResolvedValueOnce({ json: async () => ([{ name: 'Coder', id: 'abc123' }]) })
      .mockResolvedValueOnce({ status: 202 })
    const status = await dispatchTask(fetchMock as any, 'http://localhost:8000/agents')
    // Ensure request payload correctness
    const body = JSON.parse(fetchMock.mock.calls[1][1].body)
    expect(body).toEqual({ prompt: expect.any(String) })
    expect(status).toBe(202)
  })

  it('throws when Coder agent not found', async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce({ json: async () => ([] as any[]) })
    await expect(dispatchTask(fetchMock as any, 'http://localhost:8000/agents')).rejects.toThrow('Coder agent not found')
  })
})

