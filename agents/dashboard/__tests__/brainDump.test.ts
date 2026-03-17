import {
  parseBrainDump,
  detectPriority,
  detectTags,
  scoreEffort,
  splitIntoLines,
} from '../lib/brainDump';

describe('splitIntoLines', () => {
  it('splits newline-separated thoughts', () => {
    const result = splitIntoLines('fix auth bug\nupdate readme\nrefactor agent');
    expect(result).toHaveLength(3);
  });

  it('strips bullet prefixes', () => {
    const result = splitIntoLines('- fix the thing\n• another task\n* third one');
    expect(result[0]).toBe('fix the thing');
    expect(result[1]).toBe('another task');
    expect(result[2]).toBe('third one');
  });

  it('strips numbered list prefixes', () => {
    const result = splitIntoLines('1. first task\n2. second task');
    expect(result[0]).toBe('first task');
    expect(result[1]).toBe('second task');
  });

  it('filters out very short lines', () => {
    const result = splitIntoLines('ok\nfix the auth bug\nhi');
    expect(result).toHaveLength(1);
  });
});

describe('detectPriority', () => {
  it('returns critical for urgent keywords', () => {
    expect(detectPriority('fix auth ASAP it is broken')).toBe('critical');
    expect(detectPriority('urgent: server is down')).toBe('critical');
  });

  it('returns high for must/need/today keywords', () => {
    expect(detectPriority('must update the deployment today')).toBe('high');
    expect(detectPriority('need to fix the blocking issue')).toBe('high');
  });

  it('returns low for maybe/someday keywords', () => {
    expect(detectPriority('maybe explore chroma embeddings someday')).toBe('low');
    expect(detectPriority('nice to have: dark mode on settings page')).toBe('low');
  });

  it('defaults to medium for neutral text', () => {
    expect(detectPriority('refactor the polling logic')).toBe('medium');
  });
});

describe('detectTags', () => {
  it('detects python tag', () => {
    expect(detectTags('update the fastapi endpoint')).toContain('🐍 python');
  });

  it('detects docker tag', () => {
    expect(detectTags('fix the dockerfile and compose setup')).toContain('🐳 docker');
  });

  it('detects multiple tags', () => {
    const tags = detectTags('write pytest tests for the api endpoint');
    expect(tags).toContain('🧪 tests');
    expect(tags).toContain('📡 api');
  });

  it('returns empty array for untagged text', () => {
    expect(detectTags('take a break and stretch')).toEqual([]);
  });
});

describe('scoreEffort', () => {
  it('scores quick tasks as 1', () => {
    expect(scoreEffort('quick fix to the readme')).toBe(1);
  });

  it('scores build/create tasks as 4', () => {
    expect(scoreEffort('build the new auth system')).toBe(4);
  });

  it('scores rewrite/overhaul as 5', () => {
    expect(scoreEffort('overhaul the entire agent architecture big rework')).toBe(5);
  });

  it('uses word-count heuristic for neutral text', () => {
    expect(scoreEffort('update the thing')).toBeLessThanOrEqual(2);
  });
});

describe('parseBrainDump', () => {
  it('returns micro-tasks with all fields', () => {
    const tasks = parseBrainDump('fix auth bug urgently\nmaybe explore embeddings');
    expect(tasks.length).toBe(2);
    tasks.forEach(t => {
      expect(t).toHaveProperty('id');
      expect(t).toHaveProperty('text');
      expect(t).toHaveProperty('effort');
      expect(t).toHaveProperty('priority');
      expect(t).toHaveProperty('tags');
      expect(t).toHaveProperty('done', false);
    });
  });

  it('sorts critical tasks first', () => {
    const tasks = parseBrainDump(
      'maybe nice to have feature\nurgent: server is down\nnormal update'
    );
    expect(tasks[0].priority).toBe('critical');
  });

  it('handles bullet + numbered mixed input', () => {
    const tasks = parseBrainDump(
      '1. fix the docker compose setup\n- update the fastapi routes\n• write tests for agent'
    );
    expect(tasks.length).toBe(3);
  });

  it('returns empty array for empty input', () => {
    expect(parseBrainDump('')).toEqual([]);
    expect(parseBrainDump('\n\n  ')).toEqual([]);
  });

  it('effort values are within 1-5 range', () => {
    const tasks = parseBrainDump(
      'quick fix\nsimple update\nrefactor the agent polling\nbuild new auth\noverhaul entire system'
    );
    tasks.forEach(t => {
      expect(t.effort).toBeGreaterThanOrEqual(1);
      expect(t.effort).toBeLessThanOrEqual(5);
    });
  });
});
