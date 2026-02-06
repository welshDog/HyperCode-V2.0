const request = require('supertest');
const app = require('./server');
const { Pool } = require('pg');

// Mock PG Pool
jest.mock('pg', () => {
  const mPool = {
    query: jest.fn(),
  };
  return { Pool: jest.fn(() => mPool) };
});

describe('Hyper-Mission API', () => {
  let pool;

  beforeEach(() => {
    pool = new (require('pg').Pool)();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('GET /api/tasks returns sorted tasks', async () => {
    const mockTasks = [
      { id: 1, title: 'Task 1', impact: 5, effort: 5, urgency: 'medium' },
      { id: 2, title: 'Task 2', impact: 10, effort: 2, urgency: 'critical' }
    ];
    pool.query.mockResolvedValueOnce({ rows: mockTasks });

    const res = await request(app).get('/api/tasks');
    
    expect(res.statusCode).toEqual(200);
    expect(res.body.length).toEqual(2);
    // Task 2 should be first (Score: 10*1.5/2 = 7.5 vs 5*1.0/5 = 1.0)
    expect(res.body[0].title).toEqual('Task 2');
  });

  it('POST /api/tasks creates a task', async () => {
    const newTask = { title: 'New', impact: 5, effort: 5, urgency: 'medium' };
    pool.query.mockResolvedValueOnce({ rows: [{ id: 3, ...newTask, status: 'pending' }] });

    const res = await request(app).post('/api/tasks').send(newTask);
    
    expect(res.statusCode).toEqual(201);
    expect(res.body.id).toEqual(3);
  });

  it('PUT /api/tasks/:id/done validates done definition', async () => {
    const res = await request(app).put('/api/tasks/1/done').send({});
    expect(res.statusCode).toEqual(400);
    expect(res.body.error).toContain('Done Definition not met');
  });

  it('PUT /api/tasks/:id/done succeeds with evidence', async () => {
    pool.query.mockResolvedValueOnce({ rows: [{ id: 1, status: 'completed' }] });
    const res = await request(app).put('/api/tasks/1/done').send({
      evidence_link: 'http://github.com',
      peer_review_checked: true
    });
    expect(res.statusCode).toEqual(200);
    expect(res.body.status).toEqual('completed');
  });
});
