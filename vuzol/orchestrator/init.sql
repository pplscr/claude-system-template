-- init.sql — PG schema for task orchestration
-- Run: sudo -u postgres psql -f init.sql

CREATE DATABASE orchestrator OWNER postgres;
\c orchestrator

CREATE TYPE task_status AS ENUM ('pending', 'claimed', 'running', 'done', 'failed');

CREATE TABLE tasks (
    id            SERIAL PRIMARY KEY,
    space         VARCHAR(64) NOT NULL,
    target        VARCHAR(64) DEFAULT 'mac-mini',
    priority      SMALLINT DEFAULT 0,
    status        task_status DEFAULT 'pending',
    payload       JSONB NOT NULL DEFAULT '{}',
    result        TEXT,
    error         TEXT,
    created_at    TIMESTAMPTZ DEFAULT now(),
    claimed_at    TIMESTAMPTZ,
    started_at    TIMESTAMPTZ,
    done_at       TIMESTAMPTZ,
    retries       SMALLINT DEFAULT 0,
    max_retries   SMALLINT DEFAULT 3
);

CREATE INDEX idx_tasks_status_priority ON tasks (status, priority DESC, created_at);
CREATE INDEX idx_tasks_created ON tasks (created_at DESC);
CREATE INDEX idx_tasks_space ON tasks (space);

-- Архів дайджестів
CREATE TABLE digest_archive (
    id          SERIAL PRIMARY KEY,
    type        VARCHAR(16) NOT NULL,   -- morning | midday | evening | weekly
    timestamp   TIMESTAMPTZ DEFAULT now(),
    data        JSONB NOT NULL DEFAULT '{}',
    message     TEXT
);

CREATE INDEX idx_digest_type_time ON digest_archive (type, timestamp DESC);

-- Історія виконання агентів (метрики)
CREATE TABLE agent_executions (
    id          SERIAL PRIMARY KEY,
    agent       VARCHAR(64) NOT NULL,
    space       VARCHAR(64) NOT NULL,
    task_id     INTEGER REFERENCES tasks(id),
    model       VARCHAR(128),
    provider    VARCHAR(32),
    duration_ms INTEGER,
    tokens_in   INTEGER,
    tokens_out  INTEGER,
    success     BOOLEAN,
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_agent_exec_time ON agent_executions (created_at DESC);
