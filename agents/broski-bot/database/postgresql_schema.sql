-- BROski Bot v4.0 - PostgreSQL Schema
-- Production-ready database with 20+ tables

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Users table
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    username TEXT NOT NULL,
    discriminator TEXT,
    broski_tokens INTEGER DEFAULT 1000 CHECK(broski_tokens >= 0),
    xp INTEGER DEFAULT 0 CHECK(xp >= 0),
    level INTEGER DEFAULT 1 CHECK(level >= 1),
    profile_data JSONB DEFAULT '{}'::jsonb,
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    last_active TIMESTAMPTZ DEFAULT NOW(),
    risk_score INTEGER DEFAULT 50 CHECK(risk_score BETWEEN 0 AND 100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_last_active ON users(last_active);
CREATE INDEX idx_users_xp ON users(xp DESC);
CREATE INDEX idx_users_level ON users(level DESC);
CREATE INDEX idx_users_profile_data ON users USING GIN(profile_data);

-- Economy transactions
CREATE TABLE economy_transactions (
    transaction_id BIGSERIAL PRIMARY KEY,
    from_user_id BIGINT REFERENCES users(user_id),
    to_user_id BIGINT REFERENCES users(user_id),
    amount INTEGER NOT NULL,
    transaction_type TEXT NOT NULL,
    reason TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_transactions_from ON economy_transactions(from_user_id, timestamp DESC);
CREATE INDEX idx_transactions_to ON economy_transactions(to_user_id, timestamp DESC);
CREATE INDEX idx_transactions_type ON economy_transactions(transaction_type);

-- Focus sessions
CREATE TABLE focus_sessions (
    session_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id),
    duration_minutes INTEGER NOT NULL CHECK(duration_minutes > 0),
    tokens_earned INTEGER DEFAULT 0,
    xp_earned INTEGER DEFAULT 0,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'completed', 'cancelled')),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_focus_user ON focus_sessions(user_id, created_at DESC);
CREATE INDEX idx_focus_status ON focus_sessions(status) WHERE status = 'active';

-- Quests (FIXED with title column!)
CREATE TABLE quests (
    quest_id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    reward INTEGER DEFAULT 100 CHECK(reward > 0),
    xp_reward INTEGER DEFAULT 100 CHECK(xp_reward > 0),
    difficulty TEXT DEFAULT 'easy' CHECK(difficulty IN ('easy', 'medium', 'hard', 'legendary')),
    quest_type TEXT DEFAULT 'daily',
    requirement INTEGER DEFAULT 1,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_quests_active ON quests(active) WHERE active = TRUE;
CREATE INDEX idx_quests_type ON quests(quest_type);

-- User quests progress
CREATE TABLE user_quests (
    user_id BIGINT REFERENCES users(user_id),
    quest_id BIGINT REFERENCES quests(quest_id),
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    progress INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'completed', 'failed')),
    metadata JSONB DEFAULT '{}'::jsonb,
    PRIMARY KEY (user_id, quest_id)
);

CREATE INDEX idx_user_quests_status ON user_quests(user_id, status);

-- Message analytics (NEW - for moderation)
CREATE TABLE message_analytics (
    message_id BIGINT PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id),
    channel_id BIGINT NOT NULL,
    guild_id BIGINT NOT NULL,
    content TEXT,
    content_length INTEGER,
    word_count INTEGER,
    toxicity_score REAL CHECK(toxicity_score BETWEEN 0 AND 1),
    sentiment TEXT CHECK(sentiment IN ('positive', 'negative', 'neutral')),
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_messages_user ON message_analytics(user_id, timestamp DESC);
CREATE INDEX idx_messages_channel ON message_analytics(channel_id, timestamp DESC);
CREATE INDEX idx_messages_toxicity ON message_analytics(toxicity_score DESC) WHERE toxicity_score > 0.5;

-- Moderation actions (NEW)
CREATE TABLE moderation_actions (
    action_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id),
    moderator_id BIGINT,
    action_type TEXT NOT NULL CHECK(action_type IN ('warn', 'mute', 'kick', 'ban', 'unmute', 'unban')),
    reason TEXT,
    duration_minutes INTEGER,
    expires_at TIMESTAMPTZ,
    evidence JSONB DEFAULT '{}'::jsonb,
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'expired', 'revoked')),
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_mod_actions_user ON moderation_actions(user_id, timestamp DESC);
CREATE INDEX idx_mod_actions_active ON moderation_actions(expires_at, status) WHERE status = 'active';

-- Events (NEW)
CREATE TABLE events (
    event_id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    voice_channel_id BIGINT,
    text_channel_id BIGINT,
    max_attendees INTEGER,
    created_by BIGINT REFERENCES users(user_id),
    status TEXT DEFAULT 'scheduled' CHECK(status IN ('scheduled', 'active', 'completed', 'cancelled')),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_events_start ON events(start_time);
CREATE INDEX idx_events_status ON events(status) WHERE status IN ('scheduled', 'active');

-- Event RSVPs (NEW)
CREATE TABLE event_rsvps (
    event_id BIGINT REFERENCES events(event_id) ON DELETE CASCADE,
    user_id BIGINT REFERENCES users(user_id),
    rsvp_status TEXT DEFAULT 'going' CHECK(rsvp_status IN ('going', 'maybe', 'declined')),
    actually_attended BOOLEAN DEFAULT FALSE,
    satisfaction_rating INTEGER CHECK(satisfaction_rating BETWEEN 1 AND 5),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (event_id, user_id)
);

-- Gig marketplace (Phase 4B)
CREATE TABLE gigs (
    gig_id BIGSERIAL PRIMARY KEY,
    poster_id BIGINT REFERENCES users(user_id),
    title TEXT NOT NULL,
    description TEXT,
    category TEXT,
    budget INTEGER NOT NULL CHECK(budget > 0),
    deadline TIMESTAMPTZ,
    status TEXT DEFAULT 'open' CHECK(status IN ('open', 'in_progress', 'completed', 'cancelled')),
    hired_user_id BIGINT REFERENCES users(user_id),
    escrow_amount INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_gigs_status ON gigs(status, created_at DESC);
CREATE INDEX idx_gigs_poster ON gigs(poster_id);

-- Gig applications
CREATE TABLE gig_applications (
    application_id BIGSERIAL PRIMARY KEY,
    gig_id BIGINT REFERENCES gigs(gig_id) ON DELETE CASCADE,
    applicant_id BIGINT REFERENCES users(user_id),
    message TEXT,
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'accepted', 'rejected')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(gig_id, applicant_id)
);

-- Auto-update triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_timestamp 
BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_gigs_timestamp 
BEFORE UPDATE ON gigs
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
