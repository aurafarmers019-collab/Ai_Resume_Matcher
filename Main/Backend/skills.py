# =============================================================================
#  skills.py  —  Skills database & Role Personas
# =============================================================================

SKILLS_DB = [
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "golang",
    "rust", "kotlin", "swift", "scala", "r", "matlab", "ruby", "php",
    "bash", "shell scripting",

    # ML / AI
    "machine learning", "deep learning", "neural networks", "nlp",
    "natural language processing", "computer vision", "reinforcement learning",
    "transfer learning", "transformers", "bert", "gpt", "llm",
    "large language models", "generative ai", "diffusion models",
    "scikit-learn", "tensorflow", "pytorch", "keras", "xgboost", "lightgbm",
    "huggingface", "langchain", "openai api", "feature engineering",
    "model deployment", "model evaluation", "hyperparameter tuning",
    "time series", "anomaly detection", "recommendation systems",

    # Data
    "data analysis", "data science", "data engineering", "etl",
    "data pipelines", "pandas", "numpy", "spark", "hadoop", "kafka",
    "airflow", "dbt", "sql", "mysql", "postgresql", "mongodb", "redis",
    "elasticsearch", "tableau", "power bi", "matplotlib", "seaborn",
    "plotly", "data visualization", "data wrangling", "data cleaning",

    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ci/cd",
    "jenkins", "github actions", "mlops", "devops", "linux", "git",
    "rest api", "graphql", "microservices", "serverless", "cloud computing",

    # Web
    "react", "vue", "angular", "node.js", "fastapi", "django", "flask",
    "html", "css", "tailwind", "next.js", "express.js", "spring boot",

    # Security & QA
    "unit testing", "integration testing", "pytest", "selenium",
    "cybersecurity", "oauth", "jwt", "penetration testing", "network security",

    # Soft / Process
    "agile", "scrum", "product management", "system design",
    "distributed systems", "a/b testing", "statistics", "probability",
    "optimization", "communication", "leadership",
]

ROLE_PERSONAS = {
    "Machine Learning Engineer": (
        "machine learning engineer building deploying ml models pipelines "
        "production systems pytorch tensorflow scikit-learn mlops"
    ),
    "Data Scientist": (
        "data scientist statistical analysis insights experiments hypothesis "
        "testing research visualization storytelling pandas numpy"
    ),
    "Backend Engineer": (
        "backend software engineer apis databases microservices server "
        "infrastructure scalability performance rest graphql"
    ),
    "Frontend Developer": (
        "frontend developer ui ux web interface react javascript css "
        "design components accessibility responsive"
    ),
    "Data Engineer": (
        "data engineer pipelines etl spark hadoop data infrastructure "
        "warehousing streaming kafka airflow dbt"
    ),
    "DevOps / MLOps Engineer": (
        "devops mlops engineer deployment kubernetes docker cloud "
        "infrastructure ci cd automation monitoring terraform"
    ),
    "Full Stack Developer": (
        "full stack developer frontend backend web application end to end "
        "systems rest api database ui node react"
    ),
    "AI Research Engineer": (
        "ai research engineer deep learning papers publications novel "
        "algorithms innovation experiments benchmarks transformers"
    ),
}

# =============================================================================
#  Predefined Job Descriptions
# =============================================================================

PREDEFINED_JDS = {
    "Machine Learning Engineer": """We are looking for a Machine Learning Engineer to join our AI team.

Responsibilities:
- Design, build, and deploy machine learning models to production
- Build and maintain data pipelines using Python and SQL
- Work with large datasets using Pandas, NumPy, and Spark
- Develop deep learning models using PyTorch and TensorFlow
- Implement NLP solutions using Huggingface Transformers and BERT
- Deploy models using Docker, Kubernetes, and AWS
- Build REST APIs using FastAPI to serve ML models
- Set up CI/CD pipelines and MLOps workflows

Requirements:
- 3+ years of experience in machine learning or data science
- Strong programming skills in Python
- Experience with scikit-learn, PyTorch, or TensorFlow
- Knowledge of SQL and NoSQL databases (PostgreSQL, MongoDB)
- Hands-on experience with Docker and Kubernetes
- Familiarity with cloud platforms: AWS, GCP, or Azure
- Experience with Git, GitHub Actions, and CI/CD
- Strong understanding of statistics, probability, and optimization
- Experience with model evaluation, feature engineering, and hyperparameter tuning
- Bonus: Experience with LLMs, LangChain, or OpenAI API""",

    "Full Stack Developer": """We are looking for a Full Stack Developer to join our product team.

Responsibilities:
- Build and maintain web applications using React and Node.js
- Develop RESTful APIs and GraphQL endpoints using Express.js
- Design and manage databases using PostgreSQL and MongoDB
- Write clean, reusable frontend components using React, TypeScript, and Tailwind CSS
- Implement authentication and authorization using JWT and OAuth
- Deploy applications using Docker and Kubernetes on AWS
- Set up and maintain CI/CD pipelines using GitHub Actions
- Write unit tests and integration tests

Requirements:
- 2+ years of experience in full stack web development
- Strong proficiency in JavaScript and TypeScript
- Experience with React, Next.js, and modern frontend frameworks
- Backend development experience with Node.js and Express.js or Django
- Database experience with PostgreSQL, MongoDB, and Redis
- Familiarity with Docker, Kubernetes, and cloud platforms (AWS or GCP)
- Experience with Git and CI/CD workflows
- Knowledge of HTML, CSS, and responsive design""",

    "Data Scientist": """We are hiring a Data Scientist to extract insights from complex datasets.

Responsibilities:
- Analyze large datasets to identify trends and actionable insights
- Build predictive models using Python and scikit-learn
- Design and run A/B testing experiments
- Create dashboards and visualizations using Tableau and Power BI
- Collaborate with engineering teams to deploy models
- Apply statistical methods for hypothesis testing

Requirements:
- 2+ years of experience in data science or analytics
- Proficiency in Python, R, and SQL
- Experience with pandas, numpy, scikit-learn
- Knowledge of statistics, probability, and hypothesis testing
- Experience with data visualization tools: Tableau, Power BI, Matplotlib
- Familiarity with machine learning algorithms
- Experience with PostgreSQL or MySQL
- Bonus: Experience with Apache Spark or big data tools""",

    "Data Engineer": """We are looking for a Data Engineer to build and maintain our data infrastructure.

Responsibilities:
- Design and build scalable data pipelines using Apache Spark and Kafka
- Develop ETL workflows using Apache Airflow and dbt
- Maintain data warehouse on AWS Redshift or GCP BigQuery
- Ensure data quality, reliability, and availability
- Collaborate with data scientists and analysts

Requirements:
- 3+ years of experience in data engineering
- Strong proficiency in Python and SQL
- Experience with Apache Spark, Kafka, and Airflow
- Knowledge of cloud platforms: AWS, GCP, or Azure
- Experience with data warehousing: Redshift, BigQuery, or Snowflake
- Familiarity with Docker and Kubernetes
- Experience with dbt for data transformation
- Knowledge of streaming vs batch processing""",

    "DevOps Engineer": """We are hiring a DevOps Engineer to manage our cloud infrastructure.

Responsibilities:
- Design and maintain CI/CD pipelines using Jenkins and GitHub Actions
- Manage Kubernetes clusters and Docker containerization
- Provision infrastructure using Terraform and Ansible
- Set up monitoring and alerting using Prometheus and Grafana
- Ensure high availability and disaster recovery
- Manage cloud infrastructure on AWS and GCP

Requirements:
- 3+ years of experience in DevOps or infrastructure
- Strong knowledge of Docker and Kubernetes
- Experience with CI/CD tools: Jenkins, GitHub Actions, GitLab CI
- Proficiency in Terraform and infrastructure as code
- Knowledge of Linux, Bash, and Python scripting
- Experience with cloud platforms: AWS, GCP, or Azure
- Familiarity with monitoring tools: Prometheus, Grafana
- Experience with Helm and ArgoCD""",

    "Backend Engineer": """We are looking for a Backend Software Engineer to build scalable APIs.

Responsibilities:
- Design and build RESTful and GraphQL APIs
- Develop microservices using Python (FastAPI/Django) or Java (Spring Boot)
- Manage databases: PostgreSQL, MongoDB, Redis
- Implement authentication using JWT and OAuth
- Deploy services using Docker and Kubernetes
- Write unit and integration tests

Requirements:
- 3+ years of backend development experience
- Strong proficiency in Python or Java
- Experience with FastAPI, Django, Spring Boot, or Node.js
- Database expertise: PostgreSQL, MySQL, MongoDB
- Knowledge of REST API and GraphQL design
- Experience with Docker, Kubernetes, and CI/CD
- Understanding of microservices and distributed systems
- Familiarity with message queues: Kafka or RabbitMQ""",

    "Frontend Developer": """We are hiring a Frontend Developer to build beautiful web interfaces.

Responsibilities:
- Build responsive web applications using React and TypeScript
- Develop reusable component libraries
- Integrate REST APIs and GraphQL endpoints
- Implement state management using Redux or Zustand
- Ensure cross-browser compatibility and accessibility
- Write unit tests using Jest

Requirements:
- 2+ years of frontend development experience
- Strong proficiency in JavaScript and TypeScript
- Experience with React, Next.js, or Vue.js
- Knowledge of HTML, CSS, and Tailwind CSS
- Experience with state management: Redux, Zustand
- Familiarity with GraphQL and REST APIs
- Experience with testing: Jest, Selenium
- Knowledge of Git and CI/CD workflows""",

    "Android Developer": """We are looking for an Android Developer to build our mobile application.

Responsibilities:
- Develop Android applications using Kotlin and Jetpack Compose
- Implement MVVM architecture with Room and Retrofit
- Integrate REST APIs and Firebase services
- Write unit tests and UI tests using Espresso
- Publish and maintain apps on Google Play Store

Requirements:
- 2+ years of Android development experience
- Strong proficiency in Kotlin and Java
- Experience with Jetpack Compose and Android SDK
- Knowledge of MVVM architecture, Room, Retrofit
- Experience with Coroutines and Flow
- Familiarity with Firebase and REST APIs
- Experience with Git and CI/CD
- Understanding of Material Design guidelines""",

    "Cybersecurity Engineer": """We are hiring a Cybersecurity Engineer to protect our systems.

Responsibilities:
- Conduct penetration testing and vulnerability assessments
- Monitor security events using SIEM and Splunk
- Implement zero-trust network architecture
- Respond to security incidents and perform forensic analysis
- Perform security audits for compliance

Requirements:
- 3+ years of cybersecurity experience
- Experience with penetration testing tools: Metasploit, Burp Suite, Nmap
- Knowledge of network security and firewall configuration
- Familiarity with OWASP top 10 vulnerabilities
- Experience with SIEM tools and threat intelligence
- Certifications: CEH, CompTIA Security+, or OSCP preferred
- Knowledge of Python and Bash scripting
- Understanding of OAuth, JWT, and encryption""",

    "Cloud Architect": """We are looking for a Cloud Architect to design our cloud infrastructure.

Responsibilities:
- Design multi-region cloud architectures on AWS, GCP, and Azure
- Define cloud governance, security, and cost optimization strategies
- Architect high-availability and disaster recovery solutions
- Lead cloud migration projects
- Implement infrastructure as code using Terraform

Requirements:
- 5+ years of cloud architecture experience
- Deep expertise in AWS, GCP, or Azure
- Experience with Terraform and infrastructure as code
- Knowledge of Kubernetes and containerization
- Understanding of networking, VPC, load balancing, and auto scaling
- Experience with serverless architectures
- Certifications: AWS Solutions Architect, Google Cloud Architect preferred
- Knowledge of security, IAM, and compliance""",
}