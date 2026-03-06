# 🤖 AI Resume Matcher

> An intelligent dual-portal platform that uses NLP and semantic AI to match resumes against job descriptions in real time — built for the **Kreative Genesis 2026** Hackathon.

---

## 📌 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Environment Configuration](#environment-configuration)
- [Database Schema](#database-schema)
- [API Reference](#api-reference)
- [How It Works](#how-it-works)
- [Screenshots](#screenshots)
- [Team](#team)

---

## Overview

**AI Resume Matcher** is a full-stack web application with two separate portals:

- **Candidate Portal** — Job seekers upload their resume PDF and instantly receive an AI-generated match score, skill gap analysis, industry benchmark comparison, and actionable recommendations against any job description.
- **HR Portal** — Recruiters post jobs, view a ranked leaderboard of all applicants sorted by AI score, and shortlist top candidates — all automated.

The core AI engine uses **SentenceTransformer embeddings** and **cosine similarity** to semantically compare resumes to job descriptions, going far beyond simple keyword matching.

---

## Features

### 👤 Candidate Portal
- 📄 Resume PDF upload with text extraction via `pdfplumber`
- 🎯 Semantic AI match score (0–100%) with animated score gauge
- 🧠 Matched & missing skill breakdown with **trend tags** (rising / niche skills)
- 📊 Industry percentile benchmark (e.g., "better than 74% of applicants")
- 💡 AI-generated recommendation text with typing animation
- 📈 Score history line chart — track improvement over multiple analyses
- 📥 One-click **PDF report export** with full analysis details
- 👤 Profile management with persistent master resume storage
- 🔐 Firebase email verification + OTP-based signup

### 🏢 HR Portal
- 📝 Job posting with AI-assisted JD preset templates (10+ roles)
- 🏆 **Ranked applicant leaderboard** sorted by AI match score
- ✅ One-click shortlist / unshortlist per candidate
- 📋 Multi-job management (create, activate, close, delete jobs)
- 🔐 Company registration with OTP email verification

### 🔒 Authentication & Security
- Firebase Auth for email verification
- bcrypt password hashing on the backend
- OTP-verified password reset via Gmail SMTP
- Role-based access control (candidate vs. company)
- Firebase token sync for seamless password management

### 🎨 UI/UX
- Light / Dark theme toggle (default: light)
- Responsive design for desktop and mobile
- Confetti celebration on high match scores
- Smooth animations throughout

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | HTML5, CSS3, Vanilla JavaScript, Chart.js |
| **Backend** | Python 3.11+, FastAPI, Uvicorn |
| **AI / NLP** | `sentence-transformers` (all-MiniLM-L6-v2), `scikit-learn` (cosine similarity) |
| **PDF Parsing** | `pdfplumber` |
| **Database** | MySQL 8+ |
| **Auth** | Firebase Authentication, `bcrypt` |
| **Email** | Gmail SMTP (OTP delivery) |
| **Deployment** | Static frontend + Uvicorn server |

---

## Project Structure

```
ai-resume-matcher/
│
├── frontend/
│   ├── auth.html          # Login / Signup / Forgot password
│   ├── candidate.html     # Candidate dashboard (upload, score, jobs)
│   ├── company.html       # HR dashboard (post jobs, leaderboard)
│   ├── style.css          # Shared styles
│   └── app.js             # Shared JS utilities
│
├── backend/
│   ├── main.py            # FastAPI app — all routes & business logic
│   ├── utils.py           # Shared utilities
│   ├── skills.py          # Skills taxonomy & extraction logic
│   ├── dbsetup.sql        # Database schema bootstrap
│   ├── db_update.sql      # Schema migration patches
│   ├── setup_db.py        # DB setup helper script
│   ├── requirements.txt   # Python dependencies
│   └── uploads/           # Stored resume files (gitignored)
│
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- MySQL 8+
- Node.js (optional, for local static server)
- A Gmail account (for OTP emails)
- A Firebase project (for email verification)

---

### Backend Setup

**1. Clone the repository**

```bash
git clone https://github.com/your-username/ai-resume-matcher.git
cd ai-resume-matcher/backend
```

**2. Create and activate a virtual environment**

```bash
python -m venv venv
source venv/bin/activate       # Linux / macOS
venv\Scripts\activate          # Windows
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Set up the MySQL database**

```bash
mysql -u root -p < dbsetup.sql
```

**5. Configure credentials** (see [Environment Configuration](#environment-configuration))

**6. Run the backend server**

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be live at `http://localhost:8000`. Visit `http://localhost:8000/docs` for the interactive Swagger UI.

---

### Frontend Setup

The frontend is plain HTML/CSS/JS — no build step required.

**Option A — Open directly in browser**

```bash
open frontend/auth.html
```

**Option B — Serve with a local static server**

```bash
cd frontend
npx serve .
# or
python -m http.server 5500
```

Make sure the API base URL in `app.js` points to your running backend:

```javascript
const API = "http://localhost:8000";
```

---

## Environment Configuration

Open `backend/main.py` and update the config block at the top:

```python
# ── Database ──────────────────────────────────────────────────
DB_HOST      = "localhost"
DB_USER      = "root"
DB_PASSWORD  = "your_mysql_password"
DB_NAME      = "resume_matcher"

# ── Email (Gmail SMTP for OTP) ────────────────────────────────
SMTP_EMAIL    = "yourapp@gmail.com"
SMTP_PASSWORD = "xxxx xxxx xxxx xxxx"   # 16-char Gmail App Password
SMTP_PORT     = 587
```

For Gmail App Passwords: [Google Account → Security → 2-Step Verification → App Passwords](https://myaccount.google.com/apppasswords)

**Firebase Setup**

Update the Firebase config object in `frontend/auth.html`:

```javascript
const firebaseConfig = {
  apiKey:            "YOUR_API_KEY",
  authDomain:        "YOUR_PROJECT.firebaseapp.com",
  projectId:         "YOUR_PROJECT_ID",
  storageBucket:     "YOUR_PROJECT.appspot.com",
  messagingSenderId: "YOUR_SENDER_ID",
  appId:             "YOUR_APP_ID"
};
```

In your Firebase console, enable **Email/Password** authentication under Authentication → Sign-in methods.

---

## Database Schema

```sql
-- Users (candidates + HR accounts)
CREATE TABLE users (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(120)    NOT NULL,
    email           VARCHAR(255)    NOT NULL UNIQUE,
    password        VARCHAR(255)    NOT NULL,           -- bcrypt hash
    role            ENUM('candidate','company') NOT NULL,
    company         VARCHAR(120),
    industry        VARCHAR(80),
    job_role        VARCHAR(120),
    desired_role    VARCHAR(120),
    resume_score    FLOAT,
    email_verified  TINYINT         NOT NULL DEFAULT 0,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Jobs posted by HR accounts
CREATE TABLE jobs (
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
    applicants   INT          NOT NULL DEFAULT 0,
    posted_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Applications (candidate → job)
CREATE TABLE applications (
    id           INT      AUTO_INCREMENT PRIMARY KEY,
    job_id       INT      NOT NULL,
    candidate_id INT      NOT NULL,
    applied_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_application (job_id, candidate_id),
    FOREIGN KEY (job_id)       REFERENCES jobs(id)  ON DELETE CASCADE,
    FOREIGN KEY (candidate_id) REFERENCES users(id) ON DELETE CASCADE
);

-- OTP tokens for email verification and password reset
CREATE TABLE otp_tokens (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    email      VARCHAR(255) NOT NULL,
    otp        VARCHAR(10)  NOT NULL,
    purpose    VARCHAR(50)  NOT NULL,
    expires_at DATETIME     NOT NULL,
    used       TINYINT      NOT NULL DEFAULT 0
);
```

---

## API Reference

### Auth

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/signup` | Register a new user (candidate or company) |
| `POST` | `/auth/login` | Login with email + password |
| `POST` | `/auth/send-otp` | Send OTP email for verification or reset |
| `POST` | `/auth/verify-otp` | Verify OTP code |
| `POST` | `/auth/reset-password` | Reset password using verified OTP |
| `POST` | `/auth/sync-password` | Sync Firebase password to backend |
| `POST` | `/auth/change-password` | Change password (authenticated) |
| `GET`  | `/auth/profile/{user_id}` | Get user profile |
| `PUT`  | `/auth/profile/{user_id}` | Update user profile |
| `POST` | `/auth/profile/{user_id}/resume` | Upload and store master resume |
| `GET`  | `/auth/profile/{user_id}/resume` | Download stored resume |

### Jobs

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/jobs` | List all active jobs |
| `GET`  | `/jobs/company/{company_id}` | List jobs posted by a company |
| `POST` | `/jobs` | Create a new job posting |
| `PUT`  | `/jobs/{job_id}/status` | Update job status (Active/Closed/Draft) |
| `DELETE` | `/jobs/{job_id}` | Delete a job posting |

### Applications

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/apply` | Apply to a job |
| `GET`  | `/applications/job/{job_id}` | Get ranked applicants for a job |
| `GET`  | `/applications/candidate/{candidate_id}` | Get candidate's applied jobs |

### AI Matching

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/match` | Analyse resume PDF against a job description |
| `POST` | `/bulk-match` | Batch match multiple resumes |

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/health` | Health check endpoint |
| `GET`  | `/list-resumes` | List all stored resume files |

---

## How It Works

### AI Scoring Pipeline

```
Candidate uploads resume PDF
        ↓
pdfplumber extracts raw text
        ↓
PII stripped (emails, phone numbers)
        ↓
SentenceTransformer encodes resume + JD
into dense vector embeddings
        ↓
Cosine similarity computed → semantic score
        ↓
Regex-based skill extraction from both resume & JD
→ matched skills, missing skills
        ↓
Experience years parsed from resume text
        ↓
Weighted final score calculated:
  Semantic similarity  → 50%
  Skill overlap        → 30%
  Experience match     → 20%
        ↓
JSON response: score, recommendation,
matched skills, missing skills, evidence snippets
```

### Score Interpretation

| Score Range | Label |
|---|---|
| 80 – 100% | ✅ Strong Match |
| 60 – 79%  | 🟡 Good Match |
| 40 – 59%  | 🟠 Moderate Match |
| 0 – 39%   | 🔴 Low Match |

---

## Screenshots

> _Add screenshots of the candidate dashboard, HR leaderboard, match score results, and the auth flow here._

| Candidate Dashboard | HR Dashboard |
|---|---|
|<img width="1816" height="924" alt="image" src="https://github.com/user-attachments/assets/9265eabf-78f6-4a7e-b9f1-d50556cf7cfa" />
 |<img width="1836" height="870" alt="image" src="https://github.com/user-attachments/assets/aa5e780e-463b-468c-9b63-5831ce24c68a" />
 |

| Match Score Results | Job Listings |
|---|---|
|<img width="1803" height="918" alt="image" src="https://github.com/user-attachments/assets/85cc82a4-c45c-4a94-9903-6f8702774c68" />
|<img width="1814" height="934" alt="image" src="https://github.com/user-attachments/assets/f865ca39-d1fc-4cea-a65a-307584ac8973" />
|

---

## Team

| Name | Role |
|---|---|
| [ALAGIRI K | Full Stack Development |
| [AMAL C SIMON] | AI / NLP Integration |
| [GNANASANKAR M] | UI/UX & Frontend |
| [CHANTHRIHA J] | Backend & Database |

**Hackathon:** Kreative Genesis 2026
**Domain:** AI & AUTOMATION

---

## License

This project was built for the Kreative Genesis 2026 hackathon. All rights reserved by the team.
