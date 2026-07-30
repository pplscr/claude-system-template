-- Orchestrator database: task queue + agent executions + digest archive
-- psql -U postgres -d orchestrator -f init.sql

-- ── ENUMs ─────────────────────────────────────────────────────
CREATE TYPE task_status AS ENUM ('pending', 'claimed', 'running', 'done', 'failed');

-- ── TASKS: main orchestration queue ───────────────────────────
CREATE TABLE IF NOT EXISTS tasks (
    id          SERIAL PRIMARY KEY,
    space       VARCHAR(64) NOT NULL DEFAULT '',
    target      VARCHAR(64) NOT NULL DEFAULT 'mac-mini',
    priority    SMALLINT NOT NULL DEFAULT 50,
    status      task_status NOT NULL DEFAULT 'pending',
    payload     JSONB NOT NULL DEFAULT '{}',
    result      TEXT,
    error       TEXT,
    claimed_by  VARCHAR(128),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    claimed_at  TIMESTAMPTZ,
    done_at     TIMESTAMPTZ
);

-- Index for polling pending tasks ordered by priority
CREATE INDEX IF NOT EXISTS idx_tasks_pending
    ON tasks (status, priority DESC, created_at)
    WHERE status = 'pending';

-- Index for filtering by space
CREATE INDEX IF NOT EXISTS idx_tasks_space
    ON tasks (space, status);

-- ── DIGEST ARCHIVE: historical digest data ────────────────────
CREATE TABLE IF NOT EXISTS digest_archive (
    id          SERIAL PRIMARY KEY,
    type        VARCHAR(32) NOT NULL,        -- 'morning', 'midday', 'evening', 'weekly'
    date        DATE NOT NULL,
    data        JSONB NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (type, date)
);

CREATE INDEX IF NOT EXISTS idx_digest_date
    ON digest_archive (date DESC);

-- ── AGENT EXECUTIONS: track agent runs ────────────────────────
CREATE TABLE IF NOT EXISTS agent_executions (
    id          SERIAL PRIMARY KEY,
    task_id     INTEGER REFERENCES tasks(id),
    space       VARCHAR(64),
    agent       VARCHAR(128),
    model       VARCHAR(64),
    status      task_status NOT NULL DEFAULT 'running',
    started_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,
    duration_ms INTEGER,
    tokens_in   INTEGER,
    tokens_out  INTEGER,
    error       TEXT
);

CREATE INDEX IF NOT EXISTS idx_agent_exec_task
    ON agent_executions (task_id);

-- ── HEARTBEAT LOG ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS heartbeats (
    id          SERIAL PRIMARY KEY,
    source      VARCHAR(64) NOT NULL DEFAULT 'mac-mini',
    received_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_heartbeats_time
    ON heartbeats (received_at DESC);

-- ── SESSION COUNTERS: track Claude sessions ───────────────────
CREATE TABLE IF NOT EXISTS session_counters (
    id          SERIAL PRIMARY KEY,
    node        VARCHAR(32) NOT NULL,         -- 'mac-mini' | 'vuzol'
    active      SMALLINT NOT NULL DEFAULT 0,
    max_allowed SMALLINT NOT NULL DEFAULT 2,
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO session_counters (node, active, max_allowed)
VALUES ('vuzol', 0, 2), ('mac-mini', 0, 3)
ON CONFLICT DO NOTHING;
