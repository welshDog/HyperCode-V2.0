"use client";

type Politeness = "polite" | "assertive";

export function LiveRegion({
  message,
  politeness = "polite",
  atomic = true,
  relevant = "additions text",
  busy,
}: {
  message: string;
  politeness?: Politeness;
  atomic?: boolean;
  relevant?: string;
  busy?: boolean;
}) {
  const role = politeness === "assertive" ? "alert" : "status";
  return (
    <div
      className="sr-only"
      role={role}
      aria-live={politeness}
      aria-atomic={atomic}
      aria-relevant={relevant}
      aria-busy={busy}
    >
      {message}
    </div>
  );
}

