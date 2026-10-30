import re

ROLE_TAXONOMY = {
    "Software Development Engineer (SDE)": {
        "required_keywords": [
            "data structures", "algorithms", "dsa", "c++", "java", "python",
            "oop", "object oriented programming", "dbms", "sql", "operating systems",
            "computer networks", "git", "github", "problem solving"
        ],
        "good_to_have": [
            "system design", "rest api", "docker", "microservices", "redis",
            "linux", "unit testing", "ci/cd", "concurrency", "multithreading"
        ],
        "description": "Focuses on high-performance code, scalable architecture, strong DSA, and core CS fundamentals."
    },
    "Full Stack Web Developer": {
        "required_keywords": [
            "javascript", "typescript", "react", "html", "css", "node.js",
            "express", "sql", "mongodb", "rest api", "git", "github",
            "responsive design", "frontend", "backend"
        ],
        "good_to_have": [
            "next.js", "tailwind", "redux", "graphql", "docker", "aws",
            "authentication", "jwt", "postgresql", "postman", "jest"
        ],
        "description": "Focuses on modern web apps, full-stack architecture, clean APIs, and responsive UIs."
    },
    "Data Scientist / ML Engineer": {
        "required_keywords": [
            "python", "machine learning", "pandas", "numpy", "scikit-learn",
            "sql", "data analysis", "eda", "deep learning", "statistics",
            "data visualization", "matplotlib", "seaborn", "git"
        ],
        "good_to_have": [
            "tensorflow", "pytorch", "xgboost", "nlp", "computer vision",
            "tableau", "power bi", "mlops", "docker", "cloud", "aws"
        ],
        "description": "Focuses on statistical modeling, ML pipelines, feature engineering, and predictive algorithms."
    },
    "Cloud & DevOps Engineer": {
        "required_keywords": [
            "linux", "bash", "docker", "kubernetes", "ci/cd", "jenkins",
            "git", "aws", "cloud", "networking", "python", "terraform"
        ],
        "good_to_have": [
            "ansible", "prometheus", "grafana", "azure", "gcp",
            "infrastructure as code", "microservices", "helm", "security"
        ],
        "description": "Focuses on automated pipelines, container orchestration, infrastructure as code, and site reliability."
    },
    "Business / Data Analyst": {
        "required_keywords": [
            "sql", "excel", "python", "tableau", "power bi", "data analysis",
            "business intelligence", "statistics", "communication", "dashboards"
        ],
        "good_to_have": [
            "pandas", "storytelling", "r", "problem solving", "a/b testing",
            "kpi tracking", "market research", "presentation"
        ],
        "description": "Focuses on data storytelling, actionable business metrics, SQL querying, and executive reporting."
    }
}

def analyze_resume_text(resume_text: str, role_name: str):
    if not resume_text or len(resume_text.strip()) < 20:
        return {
            "score": 0,
            "matched_required": [],
            "missing_required": [],
            "matched_optional": [],
            "missing_optional": [],
            "recommendations": ["Paste or write your resume summary, project descriptions, and technical skills above to analyze ATS compatibility."]
        }
        
    role_info = ROLE_TAXONOMY.get(role_name, ROLE_TAXONOMY["Software Development Engineer (SDE)"])
    clean_text = resume_text.lower()
    
    matched_req = []
    missing_req = []
    for kw in role_info["required_keywords"]:
        # Match whole words or phrases
        pattern = r'\b' + re.escape(kw) + r'\b'
        if re.search(pattern, clean_text):
            matched_req.append(kw.title())
        else:
            missing_req.append(kw.title())
            
    matched_opt = []
    missing_opt = []
    for kw in role_info["good_to_have"]:
        pattern = r'\b' + re.escape(kw) + r'\b'
        if re.search(pattern, clean_text):
            matched_opt.append(kw.title())
        else:
            missing_opt.append(kw.title())
            
    # Calculate score
    total_req = len(role_info["required_keywords"])
    total_opt = len(role_info["good_to_have"])
    
    req_ratio = len(matched_req) / max(1, total_req)
    opt_ratio = len(matched_opt) / max(1, total_opt)
    
    score = int(round((req_ratio * 0.75 + opt_ratio * 0.25) * 100))
    score = max(5, min(100, score))
    
    recommendations = []
    if missing_req:
        top_missing = ", ".join(missing_req[:4])
        recommendations.append(f"Add critical missing core skills to your resume: **{top_missing}**.")
    if len(matched_opt) < 2:
        top_opt = ", ".join(missing_opt[:3])
        recommendations.append(f"Stand out by including modern high-demand tools like **{top_opt}**.")
    
    # Check for quantifiable achievements (numbers, %, metrics)
    metrics_matches = re.findall(r'\b\d+%\b|\b\d+x\b|\b\$\d+|\b\d+\+?\s*(users|requests|ms|seconds|stars|downloads|latency)\b', clean_text)
    if len(metrics_matches) < 2:
        recommendations.append("Incorporate **quantifiable impact metrics** (e.g., 'Optimized API response time by 35%', 'Served 2,000+ active users').")
    
    # Check project links
    if "github" not in clean_text and "gitlab" not in clean_text:
        recommendations.append("Include clickable links to your **GitHub repository** or live demo deployments.")
        
    if not recommendations:
        recommendations.append("Outstanding resume profile! Ensure your bullet points use strong action verbs (Architected, Spearheaded, Engineered).")
        
    return {
        "score": score,
        "matched_required": matched_req,
        "missing_required": missing_req,
        "matched_optional": matched_opt,
        "missing_optional": missing_opt,
        "recommendations": recommendations
    }

def generate_custom_roadmap(pillar_scores: dict, target_role: str):
    lowest_pillar = min(
        [k for k in pillar_scores.keys() if k != "Overall_Readiness"],
        key=lambda k: pillar_scores[k]
    )
    lowest_score = pillar_scores[lowest_pillar]
    
    phases = {
        "Phase 1: Days 1-30 (Foundation & Weak Link Repair)": {
            "focus": f"Primary Focus: {lowest_pillar} (Current score: {lowest_score}/100)",
            "milestones": [
                "Dedicate 2 hours daily specifically targeting your identified gap.",
                "Review standard college syllabi for Core CS (DBMS, OS, Computer Networks) and make 1-page cheat sheets.",
                "Solve 2 DSA problems daily (Focus on Arrays, Strings, Hashing, Two Pointers).",
                "Complete 1 structured aptitude practice test weekly (Quantitative & Logical reasoning)."
            ],
            "resources": [
                "LeetCode Top Interview 150 / Striver's A2Z DSA Sheet",
                "GeeksforGeeks Core CS Fundamentals (DBMS, OS, CN)",
                "IndiaBIX / PrepInsta for Aptitude Practice"
            ]
        },
        "Phase 2: Days 31-60 (Depth, Projects & Mock Tests)": {
            "focus": f"Primary Focus: Applied Projects & Advanced Problem Solving for {target_role}",
            "milestones": [
                "Build or polish 1 production-quality capstone project with clean GitHub README and live demo.",
                "Progress to Medium-level DSA: Trees, Graphs, Dynamic Programming, and Recursion.",
                "Conduct 2 peer mock interviews focusing on technical explanation and code walkthrough.",
                "Participate in at least 1 online hackathon or contest (LeetCode Biweekly / CodeChef)."
            ],
            "resources": [
                "System Design Primer (GitHub) for architectural basics",
                "NeetCode YouTube channel for pattern-based DSA",
                "Pramp / InterviewBit for peer mock technical interviews"
            ]
        },
        "Phase 3: Days 61-90 (Interview Readiness & Placement Sprints)": {
            "focus": "Primary Focus: Speed, Company-Specific Rounds & HR Communication",
            "milestones": [
                "Timed coding rounds: Solve 3 problems under 60-minute time constraints.",
                "Master behavioral questions using the STAR technique (Situation, Task, Action, Result).",
                "Tailor your resume for specific company job descriptions and verify ATS score > 80%.",
                "Complete 5 full-length mock placement drive tests (Aptitude + Technical MCQs + Coding)."
            ],
            "resources": [
                "AmbitionBox & Glassdoor for company-specific interview archives",
                "LeetCode Company Tags (Amazon, TCS Digital, Infosys, Goldman Sachs)",
                "Harvard Resume Bullet Points Guide"
            ]
        }
    }
    return lowest_pillar, phases

DIAGNOSTIC_QUIZ = [
    {
        "id": 1,
        "category": "DSA & Algorithms",
        "question": "What is the worst-case time complexity of searching an element in a Balanced Binary Search Tree (AVL Tree)?",
        "options": ["O(1)", "O(log N)", "O(N)", "O(N log N)"],
        "answer": "O(log N)",
        "explanation": "Because an AVL tree is self-balancing, the height is guaranteed to remain O(log N), ensuring search takes O(log N) worst-case."
    },
    {
        "id": 2,
        "category": "Operating Systems",
        "question": "Which of the following conditions is NOT required for a deadlock to occur?",
        "options": ["Mutual Exclusion", "Hold and Wait", "Preemption allowed", "Circular Wait"],
        "answer": "Preemption allowed",
        "explanation": "Deadlock requires NO PREEMPTION (resources cannot be forcibly taken). Preemption prevents deadlock."
    },
    {
        "id": 3,
        "category": "Database Management (DBMS)",
        "question": "Which normal form deals with removing Transitive Functional Dependencies?",
        "options": ["1NF", "2NF", "3NF", "BCNF"],
        "answer": "3NF",
        "explanation": "Third Normal Form (3NF) requires a relation to be in 2NF and have no non-prime attribute transitively dependent on the primary key."
    },
    {
        "id": 4,
        "category": "Computer Networks",
        "question": "At which layer of the OSI model does the Transport Control Protocol (TCP) operate?",
        "options": ["Network Layer", "Transport Layer", "Data Link Layer", "Session Layer"],
        "answer": "Transport Layer",
        "explanation": "TCP and UDP operate at Layer 4: Transport Layer, providing host-to-host communication and reliability services."
    },
    {
        "id": 5,
        "category": "Quantitative Aptitude",
        "question": "A train running at 72 km/hr crosses a pole in 9 seconds. What is the length of the train?",
        "options": ["150 meters", "180 meters", "200 meters", "220 meters"],
        "answer": "180 meters",
        "explanation": "Speed = 72 * (5/18) = 20 m/s. Distance = Speed * Time = 20 * 9 = 180 meters."
    }
]

