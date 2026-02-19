import { NextResponse } from 'next/server';

export async function GET() {
  // In a real application, this would fetch from a database or external service (e.g., Patreon API, Ko-fi API)
  const stats = {
    supporters: 42,
    discordCount: 150,
    fundingCurrent: 1250,
    fundingGoal: 10000,
    currency: "USD"
  };

  return NextResponse.json(stats);
}
