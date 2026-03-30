import { NextRequest, NextResponse } from 'next/server'

const CORE_URL = process.env.HYPERCODE_CORE_URL ?? 'http://hypercode-core:8000'

/** GET /api/orchestrator — system health from crew-orchestrator */
export async function GET(req: NextRequest) {
  try {
    const token = req.headers.get('authorization') ?? ''
    const res = await fetch(`${CORE_URL}/api/v1/orchestrator/system/health`, {
      headers: { Authorization: token, Accept: 'application/json' },
      cache: 'no-store',
    })
    if (!res.ok) throw new Error(`Orchestrator API ${res.status}`)
    return NextResponse.json(await res.json())
  } catch (err) {
    return NextResponse.json({ status: 'degraded', error: String(err) }, { status: 200 })
  }
}

/** POST /api/orchestrator — proxy execute to crew-orchestrator */
export async function POST(req: NextRequest) {
  try {
    const token = req.headers.get('authorization') ?? ''
    const body = await req.json()
    const res = await fetch(`${CORE_URL}/api/v1/orchestrator/execute`, {
      method: 'POST',
      headers: {
        Authorization: token,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
      cache: 'no-store',
    })
    const data = await res.json()
    return NextResponse.json(data, { status: res.status })
  } catch (err) {
    return NextResponse.json({ error: String(err) }, { status: 502 })
  }
}
