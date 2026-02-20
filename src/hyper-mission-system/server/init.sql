CREATE TABLE IF NOT EXISTS tasks (
  id SERIAL PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  impact INTEGER CHECK (impact BETWEEN 1 AND 10),
  effort INTEGER CHECK (effort BETWEEN 1 AND 10),
  urgency VARCHAR(50) CHECK (urgency IN ('critical', 'high', 'medium', 'low')),
  status VARCHAR(50) DEFAULT 'pending',
  due_date TIMESTAMP,
  evidence_link TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS subtasks (
  id SERIAL PRIMARY KEY,
  parent_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  duration_minutes INTEGER DEFAULT 15,
  is_done BOOLEAN DEFAULT FALSE
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_urgency ON tasks(urgency);
CREATE INDEX IF NOT EXISTS idx_subtasks_parent ON subtasks(parent_id);

-- Seed Data
INSERT INTO tasks (title, description, impact, effort, urgency, status) VALUES
('Implement Login', 'Auth0 integration', 10, 5, 'critical', 'pending'),
('Design DB Schema', 'Postgres tables', 9, 3, 'high', 'completed'),
('Setup CI/CD', 'GitHub Actions', 8, 8, 'medium', 'pending'),
('Fix Header CSS', 'Mobile responsiveness', 3, 2, 'low', 'pending'),
('API Rate Limiting', 'Redis implementation', 7, 5, 'high', 'pending'),
('User Profile Page', 'CRUD for users', 6, 4, 'medium', 'pending'),
('Email Notifications', 'SendGrid setup', 5, 3, 'low', 'pending'),
('Payment Gateway', 'Stripe integration', 10, 8, 'critical', 'pending'),
('Audit Logs', 'Track user actions', 4, 2, 'low', 'pending'),
('Data Export', 'CSV download', 5, 4, 'medium', 'pending'),
('Dark Mode', 'Theme switcher', 3, 3, 'low', 'pending'),
('Search Bar', 'Elasticsearch', 8, 9, 'high', 'pending'),
('Analytics Dashboard', 'Chart.js integration', 9, 7, 'critical', 'pending'),
('Mobile App Prototype', 'React Native', 7, 8, 'medium', 'pending'),
('SEO Optimization', 'Meta tags', 6, 2, 'medium', 'pending'),
('Cookie Consent', 'GDPR compliance', 9, 1, 'critical', 'pending'),
('Unit Tests', 'Jest setup', 8, 5, 'high', 'pending'),
('Documentation', 'Swagger', 7, 4, 'medium', 'pending'),
('Load Testing', 'K6 scripts', 6, 5, 'low', 'pending'),
('Deploy to Prod', 'AWS ECS', 10, 6, 'critical', 'pending')
ON CONFLICT DO NOTHING;
