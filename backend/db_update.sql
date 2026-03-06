-- =============================================================
-- db_update.sql  —  incremental migrations
-- Apply after initial dbsetup.sql if needed
-- =============================================================

USE resume_matcher;

-- Example: add profile_pic column if not exists
-- ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_pic VARCHAR(500);

-- Ensure email_verified default is correct
ALTER TABLE users MODIFY COLUMN email_verified TINYINT NOT NULL DEFAULT 0;

-- Ensure applicants default is correct
ALTER TABLE jobs MODIFY COLUMN applicants INT NOT NULL DEFAULT 0;

-- Add index on email for faster login lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Add index on company_id for faster job fetches
CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company_id);

-- Add index on status for job listings
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);