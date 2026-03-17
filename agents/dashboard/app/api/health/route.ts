import { NextResponse } from "next/server";
import { existsSync, readdirSync } from "node:fs";
import { join } from "node:path";

function hasStaticChunks(): { ok: boolean; reason?: string } {
  const staticDir = join(process.cwd(), ".next", "static");
  if (!existsSync(staticDir)) return { ok: false, reason: "static assets missing" };

  const chunksDir = join(staticDir, "chunks");
  if (!existsSync(chunksDir)) return { ok: false, reason: "static chunks missing" };

  try {
    const files = readdirSync(chunksDir);
    const hasJsChunk = files.some((f) => f.endsWith(".js"));
    if (!hasJsChunk) return { ok: false, reason: "no chunk files found" };
    return { ok: true };
  } catch {
    return { ok: false, reason: "failed to read chunks directory" };
  }
}

export function GET() {
  const staticCheck = hasStaticChunks();
  if (!staticCheck.ok) {
    return NextResponse.json(
      { status: "degraded", reason: staticCheck.reason, timestamp: new Date().toISOString() },
      { status: 503 }
    );
  }

  return NextResponse.json({
    status: "ok",
    timestamp: new Date().toISOString(),
    staticAssets: "present",
  });
}

