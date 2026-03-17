/**
 * Brain Dump → Task Chunker
 * Parses a raw brain dump string into scored, tagged micro-tasks.
 * Works offline (rule-based) or online (LLM-enhanced via API).
 */

export type TaskPriority = 'critical' | 'high' | 'medium' | 'low';

export interface MicroTask {
  id: string;
  text: string;
  effort: 1 | 2 | 3 | 4 | 5;   // 1 = 5 mins, 5 = 2+ hours
  priority: TaskPriority;
  tags: string[];
  done: boolean;
}

// ── Keyword maps ────────────────────────────────────────────────────────────

const CRITICAL_KEYWORDS = ['urgent', 'asap', 'critical', 'broken', 'down', 'crash', 'fix now', 'emergency'];
const HIGH_KEYWORDS     = ['important', 'must', 'need to', 'required', 'deadline', 'today', 'block'];
const LOW_KEYWORDS      = ['maybe', 'idea', 'could', 'someday', 'nice to have', 'consider', 'explore'];

const TAG_MAP: Record<string, string[]> = {
  '🐍 python':    ['python', 'py', 'pip', 'venv', 'django', 'fastapi', 'flask'],
  '⚛️ react':     ['react', 'tsx', 'jsx', 'next', 'component', 'hook', 'state'],
  '🐳 docker':    ['docker', 'container', 'compose', 'image', 'dockerfile'],
  '🗄️ database':  ['database', 'db', 'postgres', 'redis', 'sql', 'migration', 'schema'],
  '🤖 agent':     ['agent', 'crew', 'healer', 'orchestrator', 'llm', 'ai', 'model'],
  '🧪 tests':     ['test', 'spec', 'jest', 'pytest', 'coverage', 'assert'],
  '🔒 security':  ['security', 'auth', 'token', 'password', 'secret', 'permission'],
  '📡 api':       ['api', 'endpoint', 'route', 'fetch', 'request', 'response', 'http'],
  '🎨 ui':        ['ui', 'style', 'css', 'design', 'layout', 'responsive', 'theme'],
  '📝 docs':      ['doc', 'readme', 'comment', 'document', 'guide', 'write up'],
};

const EFFORT_SIGNALS: Array<{ keywords: string[]; effort: MicroTask['effort'] }> = [
  { keywords: ['quick', 'tiny', 'just', 'small', '5 min', '2 min', 'one line'], effort: 1 },
  { keywords: ['simple', 'easy', 'short', '10 min', '15 min'],                  effort: 2 },
  { keywords: ['refactor', 'update', 'tweak', 'add', 'change', '30 min'],       effort: 3 },
  { keywords: ['build', 'create', 'implement', 'setup', 'migrate', '1 hour'],   effort: 4 },
  { keywords: ['design', 'architect', 'rework', 'overhaul', 'rewrite', 'big'],  effort: 5 },
];

// ── Helpers ──────────────────────────────────────────────────────────────────

export function generateId(): string {
  return Math.random().toString(36).slice(2, 9);
}

function lower(s: string) { return s.toLowerCase(); }

export function detectPriority(text: string): TaskPriority {
  const t = lower(text);
  if (CRITICAL_KEYWORDS.some(k => t.includes(k))) return 'critical';
  if (HIGH_KEYWORDS.some(k => t.includes(k)))     return 'high';
  if (LOW_KEYWORDS.some(k => t.includes(k)))      return 'low';
  return 'medium';
}

export function detectTags(text: string): string[] {
  const t = lower(text);
  return Object.entries(TAG_MAP)
    .filter(([, keywords]) => keywords.some(k => t.includes(k)))
    .map(([tag]) => tag);
}

export function scoreEffort(text: string): MicroTask['effort'] {
  const t = lower(text);
  for (const { keywords, effort } of EFFORT_SIGNALS) {
    if (keywords.some(k => t.includes(k))) return effort;
  }
  // Default: length heuristic
  const words = text.trim().split(/\s+/).length;
  if (words <= 5)  return 1;
  if (words <= 10) return 2;
  if (words <= 20) return 3;
  return 4;
}

/**
 * Split raw brain dump text into candidate task lines.
 * Handles: bullet lines, numbered lists, newline-separated thoughts.
 */
export function splitIntoLines(raw: string): string[] {
  return raw
    .split(/\n/)
    .map(l => l.replace(/^[-*•\d.]+\s*/, '').trim())
    .filter(l => l.length > 3);
}

/**
 * Full local parse: no API needed.
 * Returns tasks sorted: critical → high → medium → low.
 */
export function parseBrainDump(raw: string): MicroTask[] {
  const lines = splitIntoLines(raw);
  const ORDER: Record<TaskPriority, number> = { critical: 0, high: 1, medium: 2, low: 3 };

  return lines
    .map(text => ({
      id:       generateId(),
      text,
      effort:   scoreEffort(text),
      priority: detectPriority(text),
      tags:     detectTags(text),
      done:     false,
    } satisfies MicroTask))
    .sort((a, b) => ORDER[a.priority] - ORDER[b.priority]);
}

/** Effort label helpers */
export const EFFORT_LABELS: Record<MicroTask['effort'], string> = {
  1: '~5 min',
  2: '~15 min',
  3: '~30 min',
  4: '~1 hr',
  5: '2+ hrs',
};

export const PRIORITY_COLOURS: Record<TaskPriority, string> = {
  critical: 'var(--hc-color-error,   #ff4d4d)',
  high:     'var(--hc-color-warning, #f5a623)',
  medium:   'var(--hc-color-info,    #4a9eff)',
  low:      'var(--hc-color-muted,   #888)',
};
