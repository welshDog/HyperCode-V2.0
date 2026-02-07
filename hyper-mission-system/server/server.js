const express = require('express');
const cors = require('cors');
const morgan = require('morgan');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const xss = require('xss-clean');
const hpp = require('hpp');
const compression = require('compression');
const { Pool } = require('pg');
require('dotenv').config();

const app = express();
const port = process.env.PORT || 5000;

// Security & Optimization Middleware
app.use(helmet()); // Set security headers
app.use(xss()); // Prevent XSS attacks
app.use(hpp()); // Prevent HTTP Parameter Pollution
app.use(compression()); // Compress responses

// Rate Limiting
const limiter = rateLimit({
  windowMs: 10 * 60 * 1000, // 10 mins
  max: 100 // limit each IP to 100 requests per windowMs
});
app.use('/api', limiter);

// Standard Middleware
app.use(cors());
app.use(express.json({ limit: '10kb' })); // Body limit
app.use(morgan('dev'));

// Database
const pool = new Pool({
  connectionString: process.env.DATABASE_URL
});

// Priority Matrix Logic
const calculatePriority = (impact, effort, urgency) => {
  const urgencyScores = { 'critical': 1.5, 'high': 1.2, 'medium': 1.0, 'low': 0.8 };
  return (impact * urgencyScores[urgency]) / effort;
};

// Routes

// Get all tasks (with optional sorting)
app.get('/api/tasks', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM tasks');
    // Sort by weighted priority in memory for now or move logic to SQL
    const tasks = result.rows.map(task => ({
      ...task,
      priority_score: calculatePriority(task.impact, task.effort, task.urgency)
    }));
    tasks.sort((a, b) => b.priority_score - a.priority_score);
    res.json(tasks);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Server error' });
  }
});

// Create Task
app.post('/api/tasks', async (req, res) => {
  const { title, description, impact, effort, urgency, due_date } = req.body;
  try {
    const result = await pool.query(
      'INSERT INTO tasks (title, description, impact, effort, urgency, due_date, status) VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING *',
      [title, description, impact, effort, urgency, due_date, 'pending']
    );
    res.status(201).json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Server error' });
  }
});

// Breakdown Task (Mock Engine)
app.post('/api/tasks/:id/breakdown', async (req, res) => {
  const { id } = req.params;
  try {
    // 1. Fetch parent task
    const parent = await pool.query('SELECT * FROM tasks WHERE id = $1', [id]);
    if (parent.rows.length === 0) return res.status(404).json({ error: 'Task not found' });
    
    // 2. Mock Breakdown Logic (would be LLM)
    const subtasks = [
      { title: `Research ${parent.rows[0].title}`, duration: 15 },
      { title: `Draft outline for ${parent.rows[0].title}`, duration: 15 },
      { title: `Review requirements`, duration: 15 }
    ];
    
    // 3. Insert subtasks
    const createdSubtasks = [];
    for (const st of subtasks) {
      const result = await pool.query(
        'INSERT INTO subtasks (parent_id, title, duration_minutes, is_done) VALUES ($1, $2, $3, $4) RETURNING *',
        [id, st.title, st.duration, false]
      );
      createdSubtasks.push(result.rows[0]);
    }
    
    res.status(201).json(createdSubtasks);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Server error' });
  }
});

// Mark Done (with validation)
app.put('/api/tasks/:id/done', async (req, res) => {
  const { id } = req.params;
  const { evidence_link, peer_review_checked } = req.body;
  
  if (!evidence_link || !peer_review_checked) {
    return res.status(400).json({ error: 'Done Definition not met: Missing evidence or peer review.' });
  }
  
  try {
    const result = await pool.query(
      'UPDATE tasks SET status = $1, evidence_link = $2 WHERE id = $3 RETURNING *',
      ['completed', evidence_link, id]
    );
    if (result.rows.length === 0) return res.status(404).json({ error: 'Task not found' });
    res.json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Server error' });
  }
});

// Dashboard Stats
app.get('/api/dashboard', async (req, res) => {
  try {
    const total = await pool.query('SELECT COUNT(*) FROM tasks');
    const completed = await pool.query("SELECT COUNT(*) FROM tasks WHERE status = 'completed'");
    const velocity = 5; // Mock velocity
    
    res.json({
      percent_complete: (parseInt(completed.rows[0].count) / parseInt(total.rows[0].count)) * 100 || 0,
      velocity_trend: 'stable',
      next_action: 'Review pending high-priority items',
      blockers: 0
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Server error' });
  }
});

// Standup Generator
app.get('/api/standup', async (req, res) => {
  try {
    const yesterday = await pool.query("SELECT title FROM tasks WHERE status = 'completed' AND due_date < NOW()");
    const today = await pool.query("SELECT title FROM tasks WHERE status = 'pending' LIMIT 3");
    
    const summary = {
      yesterday: yesterday.rows.map(t => t.title),
      today: today.rows.map(t => t.title),
      impediments: ["None"]
    };
    // Mock email sending
    console.log("Sending email:", summary);
    res.json(summary);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Server error' });
  }
});

if (require.main === module) {
  app.listen(port, () => {
    console.log(`Server running on port ${port}`);
  });
}

module.exports = app; // For testing
