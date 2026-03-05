"""
main.py  —  AI Resume Matcher  —  FastAPI Backend
==================================================
Usage:  uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

# ── stdlib ────────────────────────────────────────────────────
import os, re, time, random, string, smtplib, pathlib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List, Dict, Any

# ── third-party ───────────────────────────────────────────────
import bcrypt
import numpy as np
import pdfplumber
import mysql.connector
from fastapi import (FastAPI, HTTPException, BackgroundTasks,
                     Form, UploadFile, File, Query)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# =============================================================
# ── CONFIG  (reads from environment variables) ───────────────
# =============================================================
DB_HOST      = os.environ.get("DB_HOST", "localhost")
DB_PORT      = int(os.environ.get("DB_PORT", "3306"))
DB_USER      = os.environ.get("DB_USER", "root")
DB_PASSWORD  = os.environ.get("DB_PASSWORD", "12345678")
DB_NAME      = os.environ.get("DB_NAME", "defaultdb")
DB_SSL_CA    = os.environ.get("DB_SSL_CA", "")          # path to ca.pem (Aiven)

SMTP_EMAIL    = os.environ.get("SMTP_EMAIL", "yourapp@gmail.com")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "xxxx xxxx xxxx xxxx")
SMTP_PORT     = 587
# =============================================================

APP_VERSION = "1.0.0"

# ── FastAPI app ───────────────────────────────────────────────
app = FastAPI(title="AI Resume Matcher", version=APP_VERSION)

@app.on_event("startup")
def startup_db_migrations():
    """Run safe DB migrations on startup."""
    try:
        db = get_db(); cur = db.cursor()
        cur.execute("ALTER TABLE users ADD COLUMN resume_filename VARCHAR(255) DEFAULT NULL")
        db.commit()
    except Exception:
        pass  # Column already exists
    finally:
        try: cur.close(); db.close()
        except: pass

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── in-memory OTP store  { email: {otp, expires, purpose} } ──
OTP_STORE: Dict[str, Dict] = {}

# =============================================================
# ── SKILLS & ROLE ARCHETYPES ─────────────────────────────────
# =============================================================

SKILLS_LIST = [
    "python","java","javascript","typescript","c++","golang","kotlin","scala","r","bash",
    "machine learning","deep learning","neural networks","nlp","computer vision",
    "reinforcement learning","transformers","bert","gpt","llm","generative ai",
    "scikit-learn","tensorflow","pytorch","keras","xgboost","lightgbm","huggingface",
    "langchain","openai api","feature engineering","model deployment","time series",
    "recommendation systems","statistics","a/b testing","data analysis","data science",
    "data engineering","etl","data pipelines","pandas","numpy","apache spark","hadoop",
    "kafka","airflow","dbt","sql","mysql","postgresql","mongodb","redis","elasticsearch",
    "tableau","power bi","matplotlib","data visualization","aws","azure","gcp","docker",
    "kubernetes","terraform","ci/cd","jenkins","github actions","mlops","devops","linux",
    "git","rest api","graphql","microservices","serverless","react","vue","angular",
    "node.js","fastapi","django","flask","html","css","tailwind","next.js","spring boot",
    "express.js","jwt","oauth","pytest","selenium","penetration testing","network security",
    "siem","owasp","splunk","agile","scrum","system design","distributed systems",
    "android sdk","jetpack compose","mvvm","retrofit","coroutines","firebase","room",
    "aws sagemaker","redshift","bigquery","hive","helm","prometheus","grafana","vpc","iam",
]

ROLE_ARCHETYPES = [
    "Machine Learning Engineer","Data Scientist","Backend Engineer","Frontend Developer",
    "Data Engineer","DevOps Engineer","Full Stack Developer","Android Developer",
    "Cybersecurity Engineer","Cloud Architect",
]

# =============================================================
# ── MODEL & EMBEDDING WARM-UP ────────────────────────────────
# =============================================================

print("⏳  Loading SentenceTransformer model …")
MODEL = SentenceTransformer("all-MiniLM-L6-v2")
print("✅  Model loaded.")

print("⏳  Pre-computing skill embeddings …")
SKILL_EMBEDDINGS = MODEL.encode(SKILLS_LIST, batch_size=32, show_progress_bar=False)
print(f"✅  {len(SKILLS_LIST)} skill embeddings ready.")

print("⏳  Pre-computing role embeddings …")
ROLE_EMBEDDINGS = MODEL.encode(ROLE_ARCHETYPES, batch_size=16, show_progress_bar=False)
print(f"✅  {len(ROLE_ARCHETYPES)} role embeddings ready.")


# =============================================================
# ── DB HELPER ────────────────────────────────────────────────
# =============================================================

def get_db():
    kwargs = dict(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
    )
    # Add SSL if Aiven CA cert is provided
    if DB_SSL_CA and os.path.exists(DB_SSL_CA):
        kwargs["ssl_ca"] = DB_SSL_CA
        kwargs["ssl_verify_cert"] = True
    return mysql.connector.connect(**kwargs)


# =============================================================
# ── OTP / EMAIL HELPERS ──────────────────────────────────────
# =============================================================

def _gen_otp() -> str:
    return "".join(random.choices(string.digits, k=6))


def _send_otp_email(to_email: str, otp: str, purpose: str):
    subject = "Verify your email" if purpose == "verify" else "Reset your password"
    action  = "verify your email address" if purpose == "verify" else "reset your password"
    html = f"""
    <!DOCTYPE html>
    <html><body style="background:#0f1117;font-family:sans-serif;color:#e2e8f0;padding:40px">
      <div style="max-width:480px;margin:auto;background:#1a1d2e;border-radius:12px;
                  padding:40px;border:1px solid #2d3152">
        <h2 style="color:#6c63ff;margin-bottom:8px">AI Resume Matcher</h2>
        <p style="color:#8892b0;margin-bottom:24px">Use the code below to {action}.</p>
        <div style="background:#0f1117;border-radius:8px;padding:24px;text-align:center;
                    letter-spacing:16px;font-size:36px;font-weight:700;
                    color:#00d4a1;margin-bottom:24px">{otp}</div>
        <p style="color:#8892b0;font-size:13px">This code is valid for <b>10 minutes</b>.</p>
        <p style="color:#8892b0;font-size:12px;margin-top:16px">
          If you did not request this, please ignore this email.</p>
      </div>
    </body></html>"""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = SMTP_EMAIL
    msg["To"]      = to_email
    msg.attach(MIMEText(html, "html"))
    try:
        with smtplib.SMTP("smtp.gmail.com", SMTP_PORT) as s:
            s.starttls()
            s.login(SMTP_EMAIL, SMTP_PASSWORD)
            s.sendmail(SMTP_EMAIL, to_email, msg.as_string())
    except Exception as e:
        print(f"⚠️  SMTP error: {e}")


# =============================================================
# ── NLP / MATCHING ENGINE ────────────────────────────────────
# =============================================================

PII_PATTERNS = [
    r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}",           # email
    r"(\+91[-\s]?)?[6-9]\d{9}",                  # Indian phone
    r"linkedin\.com/in/[\w-]+",                   # LinkedIn
    r"github\.com/[\w-]+",                        # GitHub
]

def _strip_pii(text: str) -> str:
    for pat in PII_PATTERNS:
        text = re.sub(pat, " ", text, flags=re.IGNORECASE)
    return text


def _extract_years(text: str) -> Optional[float]:
    patterns = [
        r"(\d+(?:\.\d+)?)\s*\+?\s*years? of experience",
        r"experience[:\s]+(\d+(?:\.\d+)?)\s*\+?\s*years?",
        r"(\d+(?:\.\d+)?)\s*\+?\s*yrs?",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return float(m.group(1))
    return None


def _extract_jd_years(jd: str) -> Optional[float]:
    m = re.search(r"(\d+)\s*[-–]\s*(\d+)\s*years?", jd, re.IGNORECASE)
    if m:
        return (float(m.group(1)) + float(m.group(2))) / 2
    m = re.search(r"(\d+)\s*\+?\s*years?", jd, re.IGNORECASE)
    if m:
        return float(m.group(1))
    return None


def _extract_skills(text: str, threshold: float = 0.52) -> List[str]:
    text_lower = text.lower()
    found = []
    for skill in SKILLS_LIST:
        if skill in text_lower:
            found.append(skill)
    remaining = [s for s in SKILLS_LIST if s not in found]
    if remaining:
        remaining_idx = [SKILLS_LIST.index(s) for s in remaining]
        remaining_embs = SKILL_EMBEDDINGS[remaining_idx]
        text_emb = MODEL.encode([text], batch_size=1)[0]
        sims = cosine_similarity([text_emb], remaining_embs)[0]
        for i, sim in enumerate(sims):
            if sim >= threshold:
                found.append(remaining[i])
    return list(set(found))


def _classify_role(text: str) -> str:
    emb = MODEL.encode([text[:512]], batch_size=1)[0]
    sims = cosine_similarity([emb], ROLE_EMBEDDINGS)[0]
    return ROLE_ARCHETYPES[int(np.argmax(sims))]


def _skill_evidence(skill: str, sentences: List[str]) -> str:
    if not sentences:
        return ""
    skill_emb = MODEL.encode([skill], batch_size=1)[0]
    top25 = sentences[:25]
    sent_embs = MODEL.encode(top25, batch_size=32)
    sims = cosine_similarity([skill_emb], sent_embs)[0]
    best_idx = int(np.argmax(sims))
    return top25[best_idx]


def _analyse(resume_text: str, jd_text: str) -> Dict[str, Any]:
    t0 = time.perf_counter()

    resume_clean = _strip_pii(resume_text)

    embeddings = MODEL.encode(
        [resume_clean[:1000], jd_text[:1000]],
        batch_size=32,
    )
    resume_emb, jd_emb = embeddings[0], embeddings[1]
    semantic_sim = float(cosine_similarity([resume_emb], [jd_emb])[0][0])

    resume_skills = _extract_skills(resume_clean)
    jd_skills     = _extract_skills(jd_text)

    matched  = [s for s in resume_skills if s in jd_skills]
    missing  = [s for s in jd_skills     if s not in resume_skills]

    skill_overlap = len(matched) / max(len(jd_skills), 1)

    resume_years = _extract_years(resume_clean)
    jd_years     = _extract_jd_years(jd_text)
    if resume_years is not None and jd_years is not None:
        exp_match = min(resume_years / max(jd_years, 1), 1.0)
    else:
        exp_match = 0.5

    resume_role = _classify_role(resume_clean)
    jd_role     = _classify_role(jd_text)
    role_embs   = MODEL.encode([resume_role, jd_role], batch_size=2)
    role_align  = float(cosine_similarity([role_embs[0]], [role_embs[1]])[0][0])

    final_score = (
        0.45 * semantic_sim
        + 0.35 * skill_overlap
        + 0.10 * exp_match
        + 0.10 * role_align
    )
    final_pct = round(final_score * 100, 1)

    sentences = [s.strip() for s in re.split(r"[.\n]", resume_clean) if len(s.strip()) > 20]
    evidence = {}
    for skill in matched[:15]:
        ev = _skill_evidence(skill, sentences)
        if ev:
            evidence[skill] = ev

    def _priority(skill):
        jd_lower = jd_text.lower()
        if jd_lower.count(skill) >= 2:
            return "critical"
        emb = MODEL.encode([skill], batch_size=1)[0]
        sim = float(cosine_similarity([emb], [jd_emb])[0][0])
        if sim > 0.55:
            return "critical"
        if sim > 0.40:
            return "recommended"
        return "optional"

    missing_prioritised = [{"skill": s, "priority": _priority(s)} for s in missing]

    if final_pct >= 80:
        recommendation = "Strong Match — Highly recommend moving forward."
    elif final_pct >= 60:
        recommendation = "Good Match — Worth reviewing with a few skill gaps."
    elif final_pct >= 40:
        recommendation = "Moderate Match — Significant gaps; upskilling suggested."
    else:
        recommendation = "Low Match — Role appears misaligned with current profile."

    processing_time = round(time.perf_counter() - t0, 2)

    return {
        "final_score":           final_pct,
        "semantic_similarity":   round(semantic_sim * 100, 1),
        "skill_overlap":         round(skill_overlap * 100, 1),
        "experience_match":      round(exp_match * 100, 1),
        "role_alignment":        round(role_align * 100, 1),
        "resume_skills":         resume_skills,
        "matched_skills":        matched,
        "missing_skills":        missing_prioritised,
        "skill_evidence":        evidence,
        "resume_role":           resume_role,
        "jd_role":               jd_role,
        "resume_years":          resume_years,
        "jd_years":              jd_years,
        "recommendation":        recommendation,
        "word_count":            len(resume_clean.split()),
        "skills_found":          len(resume_skills),
        "skills_required":       len(jd_skills),
        "processing_time_sec":   processing_time,
    }


# =============================================================
# ── AUTH ENDPOINTS ───────────────────────────────────────────
# =============================================================

@app.post("/auth/signup")
def signup(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    company: str = Form(None),
    industry: str = Form(None),
    job_role: str = Form(None),
    desired_role: str = Form(None),
    background_tasks: BackgroundTasks = None,
):
    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    db = get_db(); cur = db.cursor(dictionary=True)
    try:
        cur.execute(
            """INSERT INTO users (name,email,password,role,company,industry,job_role,desired_role)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
            (name, email, pw_hash, role, company, industry, job_role, desired_role),
        )
        db.commit()
        user_id = cur.lastrowid
    except mysql.connector.IntegrityError:
        raise HTTPException(400, "Email already registered.")
    finally:
        cur.close(); db.close()

    otp = _gen_otp()
    OTP_STORE[email] = {"otp": otp, "expires": datetime.utcnow() + timedelta(minutes=10), "purpose": "verify"}
    if background_tasks:
        background_tasks.add_task(_send_otp_email, email, otp, "verify")

    return {"id": user_id, "name": name, "email": email, "role": role,
            "email_verified": 0, "message": "OTP sent."}


@app.post("/auth/login")
def login(email: str = Form(...), password: str = Form(...)):
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cur.fetchone()
    cur.close(); db.close()
    if not user or not bcrypt.checkpw(password.encode(), user["password"].encode()):
        raise HTTPException(400, "Invalid email or password.")
    user.pop("password")
    return user


@app.post("/auth/send-otp")
def send_otp(email: str = Form(...), purpose: str = Form(...), background_tasks: BackgroundTasks = BackgroundTasks()):
    if purpose == "reset":
        db = get_db(); cur = db.cursor(dictionary=True)
        cur.execute("SELECT id FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        cur.close(); db.close()
        if not user:
            raise HTTPException(404, "No account found with this email address.")

    otp = _gen_otp()
    OTP_STORE[email] = {"otp": otp, "expires": datetime.utcnow() + timedelta(minutes=10), "purpose": purpose}

    try:
        _send_otp_email(email, otp, purpose)
    except Exception as e:
        print(f"⚠️  OTP email failed: {e}")
        print(f"🔑  OTP for {email}: {otp}")

    return {"message": "OTP sent.", "dev_otp": otp if SMTP_PASSWORD == "xxxx xxxx xxxx xxxx" else None}


@app.post("/auth/verify-otp")
def verify_otp(email: str = Form(...), otp: str = Form(...), purpose: str = Form(...)):
    entry = OTP_STORE.get(email)
    if not entry or entry["otp"] != otp or entry["purpose"] != purpose:
        raise HTTPException(400, "Invalid OTP.")
    if datetime.utcnow() > entry["expires"]:
        OTP_STORE.pop(email, None)
        raise HTTPException(400, "OTP expired.")
    if purpose == "verify":
        db = get_db(); cur = db.cursor()
        cur.execute("UPDATE users SET email_verified=1 WHERE email=%s", (email,))
        db.commit(); cur.close(); db.close()
    OTP_STORE.pop(email, None)
    return {"message": "OTP verified."}


@app.post("/auth/reset-password")
def reset_password(email: str = Form(...), otp: str = Form(...), new_password: str = Form(...)):
    entry = OTP_STORE.get(email)
    if not entry or entry["otp"] != otp or entry["purpose"] != "reset":
        raise HTTPException(400, "Invalid OTP.")
    if datetime.utcnow() > entry["expires"]:
        OTP_STORE.pop(email, None)
        raise HTTPException(400, "OTP expired.")
    pw_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    db = get_db(); cur = db.cursor()
    cur.execute("UPDATE users SET password=%s WHERE email=%s", (pw_hash, email))
    db.commit(); cur.close(); db.close()
    OTP_STORE.pop(email, None)
    return {"message": "Password reset successful."}


@app.post("/auth/sync-password")
def sync_password(email: str = Form(...), new_password: str = Form(...)):
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cur.fetchone()
    if not user:
        cur.close(); db.close()
        raise HTTPException(404, "User not found.")
    pw_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    cur.execute("UPDATE users SET password=%s WHERE email=%s", (pw_hash, email))
    db.commit()
    user["password"] = None
    cur.close(); db.close()
    return {"message": "Password synced.", "data": user}


@app.post("/auth/change-password")
def change_password(
    user_id: int = Form(...),
    current_password: str = Form(...),
    new_password: str = Form(...),
):
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT password FROM users WHERE id=%s", (user_id,))
    row = cur.fetchone()
    if not row or not bcrypt.checkpw(current_password.encode(), row["password"].encode()):
        cur.close(); db.close()
        raise HTTPException(400, "Current password is incorrect.")
    pw_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    cur.execute("UPDATE users SET password=%s WHERE id=%s", (pw_hash, user_id))
    db.commit(); cur.close(); db.close()
    return {"message": "Password updated."}


@app.get("/auth/profile/{user_id}")
def get_profile(user_id: int):
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT id,name,email,role,company,industry,job_role,desired_role,"
                "resume_score,resume_filename,email_verified,created_at FROM users WHERE id=%s", (user_id,))
    user = cur.fetchone()
    cur.close(); db.close()
    if not user:
        raise HTTPException(404, "User not found.")
    return user


@app.post("/auth/profile/{user_id}/resume")
async def upload_profile_resume(user_id: int, resume: UploadFile = File(...)):
    if not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are accepted.")
    contents = await resume.read()
    os.makedirs("uploads", exist_ok=True)
    filename = f"resume_{user_id}.pdf"
    filepath = os.path.join("uploads", filename)
    with open(filepath, "wb") as f:
        f.write(contents)
    db = get_db(); cur = db.cursor()
    cur.execute("UPDATE users SET resume_filename=%s WHERE id=%s", (resume.filename, user_id))
    db.commit(); cur.close(); db.close()
    return {"message": "Resume saved.", "filename": resume.filename}


@app.get("/auth/profile/{user_id}/resume")
def download_profile_resume(user_id: int):
    from fastapi.responses import FileResponse
    filepath = os.path.join("uploads", f"resume_{user_id}.pdf")
    if not os.path.exists(filepath):
        raise HTTPException(404, "No resume saved.")
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT resume_filename FROM users WHERE id=%s", (user_id,))
    row = cur.fetchone(); cur.close(); db.close()
    filename = row["resume_filename"] if row else f"resume_{user_id}.pdf"
    return FileResponse(filepath, media_type="application/pdf", filename=filename)


@app.put("/auth/profile/{user_id}")
def update_profile(
    user_id: int,
    name: str = Form(None),
    desired_role: str = Form(None),
    job_role: str = Form(None),
):
    db = get_db(); cur = db.cursor()
    cur.execute(
        "UPDATE users SET name=COALESCE(%s,name), desired_role=COALESCE(%s,desired_role),"
        " job_role=COALESCE(%s,job_role) WHERE id=%s",
        (name, desired_role, job_role, user_id),
    )
    db.commit(); cur.close(); db.close()
    return {"message": "Profile updated."}


# =============================================================
# ── JOBS ENDPOINTS ───────────────────────────────────────────
# =============================================================

@app.get("/jobs")
def list_jobs():
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM jobs WHERE status='Active' ORDER BY posted_at DESC")
    jobs = cur.fetchall()
    cur.close(); db.close()
    return jobs


@app.get("/jobs/company/{company_id}")
def company_jobs(company_id: int):
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM jobs WHERE company_id=%s ORDER BY posted_at DESC", (company_id,))
    jobs = cur.fetchall()
    cur.close(); db.close()
    return jobs


@app.post("/jobs")
def create_job(
    company_id: int = Query(...),
    title: str = Form(...),
    location: str = Form(None),
    job_type: str = Form(None),
    salary: str = Form(None),
    experience: str = Form(None),
    department: str = Form(None),
    skills: str = Form(None),
    description: str = Form(None),
):
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT name FROM users WHERE id=%s", (company_id,))
    u = cur.fetchone()
    company_name = u["name"] if u else "Unknown"
    cur.execute(
        """INSERT INTO jobs (company_id,title,company_name,location,job_type,salary,
           experience,department,skills,description)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (company_id, title, company_name, location, job_type, salary,
         experience, department, skills, description),
    )
    db.commit()
    job_id = cur.lastrowid
    cur.close(); db.close()
    return {"id": job_id, "message": "Job posted."}


@app.put("/jobs/{job_id}/status")
def update_job_status(job_id: int, status: str = Query(...)):
    db = get_db(); cur = db.cursor()
    cur.execute("UPDATE jobs SET status=%s WHERE id=%s", (status, job_id))
    db.commit(); cur.close(); db.close()
    return {"message": f"Job status set to {status}."}


@app.delete("/jobs/{job_id}")
def delete_job(job_id: int):
    db = get_db(); cur = db.cursor()
    cur.execute("DELETE FROM jobs WHERE id=%s", (job_id,))
    db.commit(); cur.close(); db.close()
    return {"message": "Job deleted."}


# =============================================================
# ── APPLICATIONS ─────────────────────────────────────────────
# =============================================================

@app.post("/apply")
def apply(job_id: int = Query(...), candidate_id: int = Query(...)):
    db = get_db(); cur = db.cursor()
    try:
        cur.execute(
            "INSERT INTO applications (job_id,candidate_id) VALUES (%s,%s)",
            (job_id, candidate_id),
        )
        cur.execute("UPDATE jobs SET applicants=applicants+1 WHERE id=%s", (job_id,))
        db.commit()
    except mysql.connector.IntegrityError:
        raise HTTPException(400, "Already applied to this job.")
    finally:
        cur.close(); db.close()
    return {"message": "Application submitted."}


@app.get("/applications/job/{job_id}")
def job_applications(job_id: int):
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute(
        """SELECT u.id, u.name, u.email, u.desired_role, u.resume_score,
                  a.applied_at
           FROM applications a
           JOIN users u ON a.candidate_id = u.id
           WHERE a.job_id=%s
           ORDER BY a.applied_at DESC""",
        (job_id,),
    )
    rows = cur.fetchall()
    cur.close(); db.close()
    return rows


@app.get("/applications/candidate/{candidate_id}")
def candidate_applications(candidate_id: int):
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute(
        """SELECT a.id, a.applied_at, j.title, j.company_name,
                  j.location, j.status, j.salary, j.job_type
           FROM applications a
           JOIN jobs j ON a.job_id = j.id
           WHERE a.candidate_id=%s
           ORDER BY a.applied_at DESC""",
        (candidate_id,),
    )
    rows = cur.fetchall()
    cur.close(); db.close()
    return rows


# =============================================================
# ── MATCH ENDPOINTS ──────────────────────────────────────────
# =============================================================

@app.post("/match")
async def match_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    candidate_id: int = Form(None),
):
    pdf_bytes = await resume.read()
    import io
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        resume_text = "\n".join(p.extract_text() or "" for p in pdf.pages)

    if not resume_text.strip():
        raise HTTPException(400, "Could not extract text from PDF.")

    result = _analyse(resume_text, job_description)

    if candidate_id:
        try:
            db = get_db(); cur = db.cursor()
            cur.execute("UPDATE users SET resume_score=%s WHERE id=%s",
                        (result["final_score"], candidate_id))
            db.commit(); cur.close(); db.close()
        except Exception:
            pass

    return result


@app.post("/bulk-match")
def bulk_match(folder_path: str = Form(...), jd_text: str = Form(...)):
    folder = pathlib.Path(folder_path)
    if not folder.exists():
        raise HTTPException(400, "Folder not found.")

    pdf_files = list(folder.rglob("*.pdf"))
    if not pdf_files:
        raise HTTPException(400, "No PDF files found in folder.")

    results = []
    for pdf_path in pdf_files:
        try:
            with pdfplumber.open(str(pdf_path)) as pdf:
                text = "\n".join(p.extract_text() or "" for p in pdf.pages)
            if not text.strip():
                continue
            r = _analyse(text, jd_text)
            r["filename"] = pdf_path.name
            results.append(r)
        except Exception as e:
            results.append({"filename": pdf_path.name, "error": str(e)})

    results.sort(key=lambda x: x.get("final_score", 0), reverse=True)
    return {"total": len(results), "results": results}


@app.get("/list-resumes")
def list_resumes(folder: str = Query(...)):
    p = pathlib.Path(folder)
    if not p.exists():
        raise HTTPException(400, "Folder not found.")
    files = [str(f) for f in p.rglob("*.pdf")]
    return {"folder": folder, "files": files, "count": len(files)}


# =============================================================
# ── HEALTH ───────────────────────────────────────────────────
# =============================================================

@app.get("/health")
def health():
    return {"status": "ok", "version": APP_VERSION}
