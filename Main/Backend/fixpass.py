"""
fix_passwords.py
================
Standalone seed script.
1. Generates a fresh bcrypt hash of "Demo@1234".
2. Upserts all 5 HR company accounts.
3. Inserts 25 seed jobs (5 per company).

Usage:
    python fix_passwords.py

Edit MYSQL_PASSWORD below to match your MySQL root password.
"""

import bcrypt
import mysql.connector
from datetime import datetime, timedelta
import random

# ── CONFIG ────────────────────────────────────────────────────
MYSQL_HOST     = "localhost"
MYSQL_USER     = "root"
MYSQL_PASSWORD = "12345678"          # ← change to your MySQL root password
MYSQL_DB       = "resume_matcher"
DEMO_PASSWORD  = "Demo@1234"
# ─────────────────────────────────────────────────────────────

def get_hash(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt(rounds=12)).decode()

HR_ACCOUNTS = [
    {
        "name": "Priya Sharma",
        "email": "priya.sharma@zoho.com",
        "company": "Zoho Corporation",
        "industry": "Software / SaaS",
        "job_role": "HR Manager",
    },
    {
        "name": "Rahul Menon",
        "email": "rahul.menon@freshworks.com",
        "company": "Freshworks",
        "industry": "Software / SaaS",
        "job_role": "Talent Acquisition Lead",
    },
    {
        "name": "Sneha Iyer",
        "email": "sneha.iyer@razorpay.com",
        "company": "Razorpay",
        "industry": "Fintech",
        "job_role": "Recruiter",
    },
    {
        "name": "Arjun Pillai",
        "email": "arjun.pillai@flipkart.com",
        "company": "Flipkart",
        "industry": "E-Commerce",
        "job_role": "HR Manager",
    },
    {
        "name": "Divya Nair",
        "email": "divya.nair@swiggy.com",
        "company": "Swiggy",
        "industry": "Food Tech",
        "job_role": "Recruiter",
    },
]

JOBS_TEMPLATE = {
    "Zoho Corporation": [
        {
            "title": "Senior Python Backend Engineer",
            "location": "Chennai, Tamil Nadu",
            "job_type": "Full-time",
            "salary": "18–28 LPA",
            "experience": "4–7 years",
            "department": "Engineering",
            "skills": "python,fastapi,django,postgresql,redis,docker,kubernetes,rest api,git,linux",
            "description": (
                "We are looking for a Senior Python Backend Engineer to design and build "
                "scalable APIs and microservices powering Zoho's suite of products. "
                "You will collaborate with cross-functional teams to deliver high-quality software. "
                "4+ years of Python experience, strong knowledge of FastAPI/Django, SQL/NoSQL databases. "
                "Experience with containerisation and cloud deployments preferred."
            ),
        },
        {
            "title": "Machine Learning Engineer",
            "location": "Chennai, Tamil Nadu",
            "job_type": "Full-time",
            "salary": "22–35 LPA",
            "experience": "3–6 years",
            "department": "AI/ML",
            "skills": "python,machine learning,deep learning,pytorch,tensorflow,scikit-learn,nlp,mlops,docker,aws",
            "description": (
                "Join Zoho AI team to build ML models that power intelligent features across Zoho products. "
                "Responsibilities: model development, feature engineering, deployment, and monitoring. "
                "Strong ML fundamentals, Python, and experience shipping models to production required."
            ),
        },
        {
            "title": "Data Engineer",
            "location": "Chennai, Tamil Nadu",
            "job_type": "Full-time",
            "salary": "16–24 LPA",
            "experience": "3–5 years",
            "department": "Data",
            "skills": "python,apache spark,kafka,airflow,sql,postgresql,etl,data pipelines,aws,dbt",
            "description": (
                "Build robust data pipelines and infrastructure at scale. "
                "Design ETL workflows, manage data warehouses, and ensure data quality. "
                "3+ years with Spark, Kafka, and orchestration tools. SQL expertise required."
            ),
        },
        {
            "title": "Frontend Developer",
            "location": "Chennai, Tamil Nadu",
            "job_type": "Full-time",
            "salary": "14–22 LPA",
            "experience": "2–5 years",
            "department": "Engineering",
            "skills": "javascript,typescript,react,vue,html,css,tailwind,rest api,git,jest",
            "description": (
                "Develop pixel-perfect, performant UIs for Zoho applications used by millions. "
                "React/Vue expertise, strong HTML/CSS fundamentals, and accessibility awareness required. "
                "You will work closely with designers and backend engineers."
            ),
        },
        {
            "title": "DevOps Engineer",
            "location": "Chennai, Tamil Nadu",
            "job_type": "Full-time",
            "salary": "18–28 LPA",
            "experience": "3–6 years",
            "department": "Infrastructure",
            "skills": "docker,kubernetes,terraform,jenkins,github actions,linux,aws,ci/cd,prometheus,grafana",
            "description": (
                "Own CI/CD pipelines, infrastructure-as-code, and reliability for Zoho's cloud platforms. "
                "Strong Kubernetes and Terraform skills required. Experience with monitoring stacks (Prometheus/Grafana) a plus."
            ),
        },
    ],
    "Freshworks": [
        {
            "title": "Full Stack Developer",
            "location": "Bangalore, Karnataka",
            "job_type": "Full-time",
            "salary": "16–26 LPA",
            "experience": "3–6 years",
            "department": "Engineering",
            "skills": "javascript,typescript,react,node.js,python,django,postgresql,mongodb,docker,rest api",
            "description": (
                "Build and maintain full-stack features for Freshworks CRM platform. "
                "Own features end-to-end from database to UI. Strong React and Node.js skills required."
            ),
        },
        {
            "title": "Data Scientist",
            "location": "Bangalore, Karnataka",
            "job_type": "Full-time",
            "salary": "20–32 LPA",
            "experience": "3–6 years",
            "department": "AI/ML",
            "skills": "python,machine learning,statistics,a/b testing,nlp,scikit-learn,pandas,numpy,sql,tableau",
            "description": (
                "Drive data-driven product decisions using ML and statistical analysis. "
                "Build predictive models, run A/B tests, and communicate insights to stakeholders. "
                "Strong Python and ML fundamentals required."
            ),
        },
        {
            "title": "Backend Engineer – Go",
            "location": "Bangalore, Karnataka",
            "job_type": "Full-time",
            "salary": "18–30 LPA",
            "experience": "3–6 years",
            "department": "Engineering",
            "skills": "golang,microservices,rest api,grpc,postgresql,redis,kafka,docker,kubernetes,git",
            "description": (
                "Design high-throughput backend services in Go for Freshworks platform. "
                "Experience with distributed systems, gRPC, and message queues required."
            ),
        },
        {
            "title": "Android Developer",
            "location": "Bangalore, Karnataka",
            "job_type": "Full-time",
            "salary": "16–26 LPA",
            "experience": "3–5 years",
            "department": "Mobile",
            "skills": "kotlin,android sdk,jetpack compose,mvvm,retrofit,coroutines,firebase,room,git,rest api",
            "description": (
                "Build the Freshworks mobile app on Android. Strong Kotlin and Jetpack Compose skills. "
                "Experience with MVVM architecture, Retrofit, and Room database required."
            ),
        },
        {
            "title": "Cloud Architect",
            "location": "Bangalore, Karnataka",
            "job_type": "Full-time",
            "salary": "30–50 LPA",
            "experience": "7–12 years",
            "department": "Infrastructure",
            "skills": "aws,azure,gcp,terraform,kubernetes,docker,microservices,vpc,iam,serverless,ci/cd",
            "description": (
                "Lead cloud architecture strategy for Freshworks SaaS platform. "
                "Design scalable, secure multi-cloud infrastructure. 7+ years cloud experience, AWS Solutions Architect preferred."
            ),
        },
    ],
    "Razorpay": [
        {
            "title": "Backend Engineer – Payments",
            "location": "Bangalore, Karnataka",
            "job_type": "Full-time",
            "salary": "20–35 LPA",
            "experience": "3–6 years",
            "department": "Payments Engineering",
            "skills": "java,spring boot,microservices,postgresql,redis,kafka,rest api,docker,kubernetes,git",
            "description": (
                "Build the core payments infrastructure processing billions in transactions. "
                "Java/Spring Boot expertise, distributed systems knowledge, and fintech experience preferred."
            ),
        },
        {
            "title": "Cybersecurity Engineer",
            "location": "Bangalore, Karnataka",
            "job_type": "Full-time",
            "salary": "22–38 LPA",
            "experience": "4–8 years",
            "department": "Security",
            "skills": "penetration testing,owasp,network security,siem,splunk,python,linux,iam,aws,git",
            "description": (
                "Protect Razorpay's payment infrastructure and customer data. "
                "Conduct pen tests, threat modelling, and security reviews. "
                "OSCP/CEH certification preferred. Strong knowledge of OWASP and compliance standards."
            ),
        },
        {
            "title": "Machine Learning Engineer – Fraud",
            "location": "Bangalore, Karnataka",
            "job_type": "Full-time",
            "salary": "24–40 LPA",
            "experience": "4–7 years",
            "department": "Risk & AI",
            "skills": "python,machine learning,xgboost,lightgbm,feature engineering,mlops,kafka,aws sagemaker,sql,a/b testing",
            "description": (
                "Build real-time fraud detection models processing millions of daily transactions. "
                "Experience with gradient boosting, feature engineering, and low-latency model serving required."
            ),
        },
        {
            "title": "Data Engineer – Analytics",
            "location": "Bangalore, Karnataka",
            "job_type": "Full-time",
            "salary": "18–28 LPA",
            "experience": "3–5 years",
            "department": "Data Platform",
            "skills": "python,apache spark,airflow,kafka,sql,redshift,bigquery,dbt,etl,data pipelines",
            "description": (
                "Build and maintain Razorpay's analytics data platform. "
                "Design scalable ETL pipelines, manage data warehouse, and partner with analytics teams."
            ),
        },
        {
            "title": "Frontend Engineer – Dashboard",
            "location": "Bangalore, Karnataka",
            "job_type": "Full-time",
            "salary": "16–26 LPA",
            "experience": "2–5 years",
            "department": "Engineering",
            "skills": "react,typescript,javascript,next.js,tailwind,rest api,html,css,jest,git",
            "description": (
                "Own the merchant-facing Razorpay Dashboard UI. Build complex data-rich React components. "
                "TypeScript expertise and strong attention to UX performance required."
            ),
        },
    ],
    "Flipkart": [
        {
            "title": "Senior Data Scientist – Recommendations",
            "location": "Bangalore, Karnataka",
            "job_type": "Full-time",
            "salary": "24–40 LPA",
            "experience": "4–8 years",
            "department": "AI/ML",
            "skills": "python,recommendation systems,machine learning,deep learning,tensorflow,pytorch,feature engineering,sql,spark,a/b testing",
            "description": (
                "Build personalisation and recommendation systems serving 400M+ users. "
                "Strong ML experience, recommendation algorithms (collaborative filtering, neural), and A/B testing required."
            ),
        },
        {
            "title": "Backend Engineer – Supply Chain",
            "location": "Bangalore, Karnataka",
            "job_type": "Full-time",
            "salary": "18–30 LPA",
            "experience": "3–6 years",
            "department": "Supply Chain Engineering",
            "skills": "java,spring boot,microservices,mysql,redis,kafka,docker,kubernetes,rest api,system design",
            "description": (
                "Design and build scalable supply chain microservices at Flipkart. "
                "Strong Java, distributed systems, and high-scale system design experience required."
            ),
        },
        {
            "title": "Data Engineer – Big Data",
            "location": "Bangalore, Karnataka",
            "job_type": "Full-time",
            "salary": "16–26 LPA",
            "experience": "3–5 years",
            "department": "Data Platform",
            "skills": "python,apache spark,hadoop,hive,kafka,airflow,sql,etl,data pipelines,bigquery",
            "description": (
                "Build and scale Flipkart's big data platform handling petabytes of commerce data. "
                "Hadoop/Spark ecosystem expertise and experience with large-scale ETL required."
            ),
        },
        {
            "title": "Android Developer – Commerce App",
            "location": "Bangalore, Karnataka",
            "job_type": "Full-time",
            "salary": "18–30 LPA",
            "experience": "3–6 years",
            "department": "Mobile",
            "skills": "kotlin,android sdk,jetpack compose,mvvm,coroutines,retrofit,room,firebase,performance,git",
            "description": (
                "Build features for India's largest e-commerce Android app. "
                "Strong Kotlin, Jetpack Compose, and app performance optimisation skills required."
            ),
        },
        {
            "title": "DevOps Engineer – Platform",
            "location": "Bangalore, Karnataka",
            "job_type": "Full-time",
            "salary": "20–32 LPA",
            "experience": "4–7 years",
            "department": "Platform Engineering",
            "skills": "kubernetes,docker,terraform,helm,prometheus,grafana,ci/cd,jenkins,aws,linux",
            "description": (
                "Own reliability and deployment infrastructure for Flipkart's commerce platform. "
                "Kubernetes expertise at scale, Helm, and observability tooling (Prometheus/Grafana) required."
            ),
        },
    ],
    "Swiggy": [
        {
            "title": "Machine Learning Engineer – ETA & Logistics",
            "location": "Bangalore, Karnataka",
            "job_type": "Full-time",
            "salary": "22–36 LPA",
            "experience": "3–6 years",
            "department": "AI/ML",
            "skills": "python,machine learning,time series,deep learning,pytorch,feature engineering,mlops,sql,kafka,aws",
            "description": (
                "Build ML models for food delivery time estimation and route optimisation. "
                "Experience with time series, geospatial ML, and real-time model serving required."
            ),
        },
        {
            "title": "Full Stack Engineer – Consumer",
            "location": "Bangalore, Karnataka",
            "job_type": "Full-time",
            "salary": "16–28 LPA",
            "experience": "2–5 years",
            "department": "Consumer Engineering",
            "skills": "javascript,typescript,react,node.js,next.js,postgresql,redis,rest api,docker,git",
            "description": (
                "Build features for Swiggy's consumer-facing web and mobile applications. "
                "Strong React/Next.js and Node.js skills required. Experience with high-traffic applications preferred."
            ),
        },
        {
            "title": "Backend Engineer – Ordering Platform",
            "location": "Bangalore, Karnataka",
            "job_type": "Full-time",
            "salary": "18–30 LPA",
            "experience": "3–6 years",
            "department": "Engineering",
            "skills": "python,golang,microservices,postgresql,redis,kafka,docker,kubernetes,rest api,system design",
            "description": (
                "Scale Swiggy's core ordering platform processing millions of daily food orders. "
                "Strong distributed systems experience, Python or Go expertise, and message queues required."
            ),
        },
        {
            "title": "Data Scientist – Growth",
            "location": "Bangalore, Karnataka",
            "job_type": "Full-time",
            "salary": "18–30 LPA",
            "experience": "3–5 years",
            "department": "Growth & Analytics",
            "skills": "python,statistics,a/b testing,machine learning,scikit-learn,sql,pandas,data analysis,tableau,power bi",
            "description": (
                "Drive growth through data: experimentation, user behaviour analysis, and ML-powered insights. "
                "Strong statistics, A/B testing design, and SQL skills required."
            ),
        },
        {
            "title": "Cloud & Infrastructure Engineer",
            "location": "Bangalore, Karnataka",
            "job_type": "Full-time",
            "salary": "20–34 LPA",
            "experience": "4–7 years",
            "department": "Infrastructure",
            "skills": "aws,gcp,kubernetes,terraform,docker,vpc,iam,ci/cd,prometheus,grafana,linux,serverless",
            "description": (
                "Design and operate Swiggy's cloud infrastructure serving 50M+ monthly users. "
                "AWS/GCP multi-cloud experience, strong Kubernetes and Terraform skills required."
            ),
        },
    ],
}


def seed():
    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
    )
    cur = conn.cursor(dictionary=True)

    print("🔐 Generating bcrypt hash for 'Demo@1234' …")
    pw_hash = get_hash(DEMO_PASSWORD)
    print(f"   Hash: {pw_hash[:30]}…\n")

    company_ids = {}

    for hr in HR_ACCOUNTS:
        cur.execute("SELECT id FROM users WHERE email = %s", (hr["email"],))
        row = cur.fetchone()
        if row:
            cur.execute(
                "UPDATE users SET password=%s, email_verified=1 WHERE email=%s",
                (pw_hash, hr["email"]),
            )
            company_ids[hr["company"]] = row["id"]
            print(f"✅  Updated : {hr['email']}")
        else:
            cur.execute(
                """INSERT INTO users
                   (name, email, password, role, company, industry, job_role, email_verified)
                   VALUES (%s, %s, %s, 'company', %s, %s, %s, 1)""",
                (hr["name"], hr["email"], pw_hash, hr["company"], hr["industry"], hr["job_role"]),
            )
            conn.commit()
            company_ids[hr["company"]] = cur.lastrowid
            print(f"✅  Inserted: {hr['email']}")

    conn.commit()

    print("\n📋 Seeding jobs …")
    base_date = datetime.now() - timedelta(days=30)
    job_count = 0

    for company_name, jobs in JOBS_TEMPLATE.items():
        cid = company_ids.get(company_name)
        if not cid:
            print(f"   ⚠️  Could not find company_id for {company_name}, skipping.")
            continue
        for i, job in enumerate(jobs):
            posted = base_date + timedelta(days=random.randint(0, 25))
            applicants = random.randint(0, 45)
            cur.execute("SELECT id FROM jobs WHERE title=%s AND company_id=%s", (job["title"], cid))
            if cur.fetchone():
                print(f"   ⏭️  Already exists: {job['title']} @ {company_name}")
                continue
            cur.execute(
                """INSERT INTO jobs
                   (company_id, title, company_name, location, job_type, salary,
                    experience, department, skills, description, status, applicants, posted_at)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'Active',%s,%s)""",
                (
                    cid,
                    job["title"],
                    company_name,
                    job["location"],
                    job["job_type"],
                    job["salary"],
                    job["experience"],
                    job["department"],
                    job["skills"],
                    job["description"],
                    applicants,
                    posted,
                ),
            )
            job_count += 1
            print(f"   ➕ {job['title']} @ {company_name}")

    conn.commit()
    cur.close()
    conn.close()

    print(f"\n✨ Done! Seeded {job_count} new job(s).\n")
    print("=" * 56)
    print("DEMO HR CREDENTIALS (all use: Demo@1234)")
    print("=" * 56)
    for hr in HR_ACCOUNTS:
        print(f"  {hr['email']:40s}  {hr['company']}")
    print("=" * 56)


if __name__ == "__main__":
    seed()