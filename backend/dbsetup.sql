-- =============================================================
-- dbsetup.sql  —  resume_matcher database bootstrap
-- Run: mysql -u root -p < dbsetup.sql
-- =============================================================

CREATE DATABASE IF NOT EXISTS resume_matcher
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE resume_matcher;

-- ── users ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(120)    NOT NULL,
    email           VARCHAR(255)    NOT NULL UNIQUE,
    password        VARCHAR(255)    NOT NULL,
    role            ENUM('candidate','company') NOT NULL,
    company         VARCHAR(120),
    industry        VARCHAR(80),
    job_role        VARCHAR(120),
    desired_role    VARCHAR(120),
    resume_score    FLOAT,
    email_verified  TINYINT         NOT NULL DEFAULT 0,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ── jobs ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jobs (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    company_id  INT         NOT NULL,
    title       VARCHAR(200) NOT NULL,
    company_name VARCHAR(120) NOT NULL,
    location    VARCHAR(120),
    job_type    VARCHAR(60),
    salary      VARCHAR(80),
    experience  VARCHAR(80),
    department  VARCHAR(80),
    skills      TEXT,
    description TEXT,
    status      ENUM('Active','Closed','Draft') NOT NULL DEFAULT 'Active',
    applicants  INT NOT NULL DEFAULT 0,
    posted_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ── applications ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS applications (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    job_id       INT      NOT NULL,
    candidate_id INT      NOT NULL,
    applied_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_application (job_id, candidate_id),
    FOREIGN KEY (job_id)       REFERENCES jobs(id)  ON DELETE CASCADE,
    FOREIGN KEY (candidate_id) REFERENCES users(id) ON DELETE CASCADE
);

-- =============================================================
-- NOTE: HR accounts and jobs are seeded by fix_passwords.py
-- after it generates a fresh bcrypt hash of "Demo@1234".
-- Do NOT run this file alone and expect seed data —
-- run fix_passwords.py as the second step.
-- =============================================================