import mysql.connector

conn = mysql.connector.connect(
    host="mysql-1d9d1dab-resume-matcher.a.aivencloud.com",
    port=28773,
    user="avnadmin",
    password="AVNS_cYiCNMjHmbmei7MvL8w",
    database="defaultdb",
    ssl_ca="C:\\hackathon\\backend\\ca.pem",
    ssl_verify_cert=True
)

print("✅ Connected to Aiven MySQL!")

cursor = conn.cursor()

commands = [
    """
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
        resume_filename VARCHAR(255)    DEFAULT NULL,
        email_verified  TINYINT         NOT NULL DEFAULT 0,
        created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS jobs (
        id           INT AUTO_INCREMENT PRIMARY KEY,
        company_id   INT          NOT NULL,
        title        VARCHAR(200) NOT NULL,
        company_name VARCHAR(120) NOT NULL,
        location     VARCHAR(120),
        job_type     VARCHAR(60),
        salary       VARCHAR(80),
        experience   VARCHAR(80),
        department   VARCHAR(80),
        skills       TEXT,
        description  TEXT,
        status       ENUM('Active','Closed','Draft') NOT NULL DEFAULT 'Active',
        applicants   INT NOT NULL DEFAULT 0,
        posted_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (company_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS applications (
        id           INT AUTO_INCREMENT PRIMARY KEY,
        job_id       INT      NOT NULL,
        candidate_id INT      NOT NULL,
        applied_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY uq_application (job_id, candidate_id),
        FOREIGN KEY (job_id)       REFERENCES jobs(id)  ON DELETE CASCADE,
        FOREIGN KEY (candidate_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """
]

for statement in commands:
    cursor.execute(statement.strip())
    print(f"✅ Table created successfully")

conn.commit()
cursor.close()
conn.close()
print("\n🎉 All tables created! Database is ready.")