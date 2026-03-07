CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0,
    daily_streak INTEGER DEFAULT 0,
    last_daily TEXT
);
