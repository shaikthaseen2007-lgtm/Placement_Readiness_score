import numpy as np
import pandas as pd
import os

def generate_placement_dataset(num_samples=1500, random_state=42):
    np.random.seed(random_state)
    
    student_ids = [f"STU{1000 + i}" for i in range(num_samples)]
    
    branches = np.random.choice(
        ["Computer Science", "Information Technology", "Electronics & Comm", "Electrical & Electronics", "Mechanical", "Civil"],
        size=num_samples,
        p=[0.35, 0.25, 0.18, 0.10, 0.07, 0.05]
    )
    
    cgpa = np.clip(np.random.normal(7.8, 0.9, num_samples), 5.2, 9.9)
    tenth_pct = np.clip(np.random.normal(82, 9, num_samples), 55, 99)
    twelfth_pct = np.clip(np.random.normal(80, 10, num_samples), 50, 99)
    
    # Branch tech bias for DSA & Coding
    branch_boost = np.array([
        1.2 if b in ["Computer Science", "Information Technology"] else (1.0 if b == "Electronics & Comm" else 0.75)
        for b in branches
    ])
    
    # DSA / Coding problems solved (0 to 600)
    base_dsa = np.random.exponential(scale=110, size=num_samples) * branch_boost
    dsa_solved = np.clip(base_dsa.astype(int), 0, 650)
    
    # Projects Count (0 to 6)
    projects_count = np.random.poisson(lam=2.5, size=num_samples)
    projects_count = np.clip(projects_count, 0, 7)
    
    # Internships Count (0 to 3)
    internships_prob = np.clip((cgpa - 6.0) / 4.0 * 0.7, 0.05, 0.8)
    internships_count = np.random.binomial(n=3, p=internships_prob)
    
    # Hackathons & Certifications
    hackathons = np.random.poisson(lam=1.2, size=num_samples)
    hackathons = np.clip(hackathons, 0, 6)
    
    certifications = np.random.poisson(lam=2.0, size=num_samples)
    certifications = np.clip(certifications, 0, 6)
    
    # Aptitude Score (30 to 100)
    aptitude_score = np.clip(np.random.normal(68, 14, num_samples) + (cgpa - 7.5) * 3, 30, 100)
    
    # Soft Skills / Communication Rating (1.0 to 5.0)
    soft_skills = np.clip(np.normal(3.5, 0.7, num_samples) if hasattr(np, "normal") else np.random.normal(3.5, 0.7, num_samples), 1.0, 5.0)
    
    # Active Backlogs (0 to 4)
    backlog_weights = [0.72, 0.16, 0.07, 0.03, 0.02]
    backlogs = np.random.choice([0, 1, 2, 3, 4], size=num_samples, p=backlog_weights)
    
    # Calculate Latent Placement Readiness Score
    # Weights reflecting tech campus placement criteria
    academic_score = ((cgpa - 5.0) / 5.0) * 100
    coding_score = (dsa_solved / 400.0) * 100
    experience_score = (internships_count * 25 + projects_count * 12 + hackathons * 10)
    aptitude_weighted = aptitude_score
    soft_skills_score = (soft_skills / 5.0) * 100
    
    latent_score = (
        0.25 * academic_score +
        0.30 * np.clip(coding_score, 0, 100) +
        0.18 * np.clip(experience_score, 0, 100) +
        0.15 * aptitude_weighted +
        0.12 * soft_skills_score
    )
    
    # Backlog penalty
    penalty = backlogs * 18
    adjusted_score = latent_score - penalty + np.random.normal(0, 4, num_samples)
    
    # Determine placement (Threshold ~ 52)
    placement_prob = 1 / (1 + np.exp(-(adjusted_score - 53) / 8.0))
    # Strict filter: students with > 2 backlogs rarely get cleared by company eligibility
    for i in range(num_samples):
        if backlogs[i] > 2:
            placement_prob[i] *= 0.25
        if cgpa[i] < 6.0:
            placement_prob[i] *= 0.35
            
    placed = (np.random.rand(num_samples) < placement_prob).astype(int)
    
    # Tier classification & CTC estimation
    company_tiers = []
    ctc_offered = []
    
    for i in range(num_samples):
        if placed[i] == 0:
            company_tiers.append("Not Placed")
            ctc_offered.append(0.0)
        else:
            # Score indicates tier
            sc = adjusted_score[i]
            dsa = dsa_solved[i]
            intern = internships_count[i]
            
            if (sc >= 75 and dsa >= 250 and cgpa[i] >= 8.0) or (dsa >= 350 and intern >= 1):
                # Product Tier 1
                company_tiers.append("Tier 1 (Product/MNC)")
                ctc = np.random.uniform(16.0, 42.0) + (cgpa[i] - 8.0) * 2 + (dsa / 100)
            elif sc >= 60 and dsa >= 120:
                # Tech Startup / Mid-tier
                company_tiers.append("Tier 2 (Tech Startup/Mid-Corp)")
                ctc = np.random.uniform(7.5, 15.5) + (cgpa[i] - 7.0) * 1.2
            else:
                # Service / Mass Recruiter
                company_tiers.append("Tier 3 (Service/Mass Recruiter)")
                ctc = np.random.uniform(3.6, 6.8) + (cgpa[i] - 6.0) * 0.4
                
            ctc_offered.append(round(ctc, 2))
            
    df = pd.DataFrame({
        "Student_ID": student_ids,
        "Branch": branches,
        "CGPA": np.round(cgpa, 2),
        "Tenth_Percentage": np.round(tenth_pct, 1),
        "Twelfth_Percentage": np.round(twelfth_pct, 1),
        "DSA_Problems_Solved": dsa_solved,
        "Projects_Count": projects_count,
        "Internships_Count": internships_count,
        "Hackathons_Participated": hackathons,
        "Certifications_Count": certifications,
        "Aptitude_Test_Score": np.round(aptitude_score, 1),
        "Soft_Skills_Rating": np.round(soft_skills, 1),
        "Backlogs": backlogs,
        "Readiness_Index": np.round(np.clip(adjusted_score, 0, 100), 1),
        "Placed": placed,
        "Company_Tier": company_tiers,
        "CTC_Offered_LPA": ctc_offered
    })
    
    return df

if __name__ == "__main__":
    out_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(out_dir, "placement_data.csv")
    df = generate_placement_dataset()
    df.to_csv(data_path, index=False)
    print(f"Generated {len(df)} student placement records saved to {data_path}")
    print(f"Overall Placement Rate: {df['Placed'].mean()*100:.1f}%")
    print(df['Company_Tier'].value_counts())

