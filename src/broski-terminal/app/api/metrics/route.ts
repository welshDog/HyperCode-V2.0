import { NextResponse } from 'next/server';
import { register, collectDefaultMetrics } from 'prom-client';

// Check if metrics are already collected to avoid duplicate registration during hot reloads
// @ts-ignore
if (!global.metricsRegistered) {
  collectDefaultMetrics({ register });
  // @ts-ignore
  global.metricsRegistered = true;
}

export async function GET() {
  try {
    const metrics = await register.metrics();
    return new NextResponse(metrics, {
      status: 200,
      headers: {
        'Content-Type': register.contentType,
        'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
      },
    });
  } catch (err) {
    return new NextResponse(String(err), { status: 500 });
  }
}

export const dynamic = 'force-dynamic';
