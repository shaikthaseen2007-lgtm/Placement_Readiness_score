import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, roc_auc_score

MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(MODEL_DIR, "placement_data.csv")
PLACEMENT_MODEL_FILE = os.path.join(MODEL_DIR, "placement_model.joblib")
TIER_MODEL_FILE = os.path.join(MODEL_DIR, "tier_model.joblib")
CTC_MODEL_FILE = os.path.join(MODEL_DIR, "ctc_model.joblib")

FEATURE_COLS = [
    "CGPA",
    "Tenth_Percentage",
    "Twelfth_Percentage",
    "DSA_Problems_Solved",
    "Projects_Count",
    "Internships_Count",
    "Hackathons_Participated",
    "Certifications_Count",
    "Aptitude_Test_Score",
    "Soft_Skills_Rating",
    "Backlogs"
]

def load_data():
    if not os.path.exists(DATA_FILE):
        from data_generator import generate_placement_dataset
        df = generate_placement_dataset()
        df.to_csv(DATA_FILE, index=False)
    else:
        df = pd.read_csv(DATA_FILE)
    return df

def train_models():
    df = load_data()
    
    # 1. Placement Binary Classifier (Gradient Boosting)
    X = df[FEATURE_COLS]
    y_placed = df["Placed"]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_placed, test_size=0.2, random_state=42, stratify=y_placed
    )
    
    clf_placement = GradientBoostingClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.08,
        random_state=42
    )
    clf_placement.fit(X_train, y_train)
    
    acc = accuracy_score(y_test, clf_placement.predict(X_test))
    auc = roc_auc_score(y_test, clf_placement.predict_proba(X_test)[:, 1])
    print(f"Placement Classifier - Accuracy: {acc:.3f}, AUC: {auc:.3f}")
    
    # 2. Company Tier Classifier (trained on placed students)
    placed_df = df[df["Placed"] == 1].copy()
    tier_mapping = {
        "Tier 3 (Service/Mass Recruiter)": 0,
        "Tier 2 (Tech Startup/Mid-Corp)": 1,
        "Tier 1 (Product/MNC)": 2
    }
    tier_labels = ["Tier 3 (Service/Mass Recruiter)", "Tier 2 (Tech Startup/Mid-Corp)", "Tier 1 (Product/MNC)"]
    
    y_tier = placed_df["Company_Tier"].map(tier_mapping)
    X_tier = placed_df[FEATURE_COLS]
    
    clf_tier = RandomForestClassifier(n_estimators=80, max_depth=5, random_state=42)
    clf_tier.fit(X_tier, y_tier)
    
    # 3. CTC Regressor (trained on placed students)
    y_ctc = placed_df["CTC_Offered_LPA"]
    reg_ctc = RandomForestRegressor(n_estimators=80, max_depth=5, random_state=42)
    reg_ctc.fit(X_tier, y_ctc)
    
    # Save artifacts
    joblib.dump(clf_placement, PLACEMENT_MODEL_FILE)
    joblib.dump({"model": clf_tier, "labels": tier_labels}, TIER_MODEL_FILE)
    joblib.dump(reg_ctc, CTC_MODEL_FILE)
    
    return clf_placement, clf_tier, reg_ctc

def get_models():
    if not (os.path.exists(PLACEMENT_MODEL_FILE) and os.path.exists(TIER_MODEL_FILE) and os.path.exists(CTC_MODEL_FILE)):
        return train_models()
    
    try:
        clf_placement = joblib.load(PLACEMENT_MODEL_FILE)
        tier_data = joblib.load(TIER_MODEL_FILE)
        clf_tier = tier_data["model"] if isinstance(tier_data, dict) else tier_data
        reg_ctc = joblib.load(CTC_MODEL_FILE)
        return clf_placement, clf_tier, reg_ctc
    except Exception:
        return train_models()

def calculate_pillar_scores(profile: dict):
    """
    Computes 5 pillar scores (0 to 100) and overall weighted Readiness Index.
    """
    cgpa = float(profile.get("CGPA", 7.0))
    tenth = float(profile.get("Tenth_Percentage", 75.0))
    twelfth = float(profile.get("Twelfth_Percentage", 75.0))
    dsa = float(profile.get("DSA_Problems_Solved", 0))
    projects = float(profile.get("Projects_Count", 0))
    internships = float(profile.get("Internships_Count", 0))
    hackathons = float(profile.get("Hackathons_Participated", 0))
    certs = float(profile.get("Certifications_Count", 0))
    aptitude = float(profile.get("Aptitude_Test_Score", 60.0))
    soft_skills = float(profile.get("Soft_Skills_Rating", 3.0))
    backlogs = int(profile.get("Backlogs", 0))
    
    # 1. Academics (0-100)
    acad_score = (
        0.60 * ((np.clip(cgpa, 4.0, 10.0) - 4.0) / 6.0 * 100) +
        0.20 * ((np.clip(tenth, 50.0, 100.0) - 50.0) / 50.0 * 100) +
        0.20 * ((np.clip(twelfth, 50.0, 100.0) - 50.0) / 50.0 * 100)
    )
    if backlogs > 0:
        acad_score = max(0.0, acad_score - backlogs * 15)
        
    # 2. DSA & Problem Solving (0-100)
    dsa_score = min(100.0, (dsa / 350.0) * 100.0)
    
    # 3. Practical Projects & Development (0-100)
    project_score = min(100.0, (projects * 25.0) + (hackathons * 15.0))
    
    # 4. Industry Exposure & Certifications (0-100)
    industry_score = min(100.0, (internships * 40.0) + (certs * 15.0))
    
    # 5. Aptitude & Soft Skills (0-100)
    soft_score = (
        0.55 * np.clip(aptitude, 0, 100) +
        0.45 * (np.clip(soft_skills, 1.0, 5.0) / 5.0 * 100)
    )
    
    # Overall Weighted Readiness
    overall_readiness = (
        0.22 * acad_score +
        0.28 * dsa_score +
        0.20 * project_score +
        0.15 * industry_score +
        0.15 * soft_score
    )
    
    return {
        "Academics": round(float(acad_score), 1),
        "DSA & Problem Solving": round(float(dsa_score), 1),
        "Projects & Development": round(float(project_score), 1),
        "Industry Exposure": round(float(industry_score), 1),
        "Aptitude & Soft Skills": round(float(soft_score), 1),
        "Overall_Readiness": round(float(overall_readiness), 1)
    }

def predict_student_readiness(profile: dict):
    clf_placement, clf_tier, reg_ctc = get_models()
    
    input_row = pd.DataFrame([[profile.get(col, 0) for col in FEATURE_COLS]], columns=FEATURE_COLS)
    
    # Placement probability
    prob = clf_placement.predict_proba(input_row)[0][1] * 100
    
    # Tier prediction
    tier_probs = clf_tier.predict_proba(input_row)[0]
    tier_idx = int(np.argmax(tier_probs))
    tier_labels = ["Tier 3 (Service/Mass Recruiter)", "Tier 2 (Tech Startup/Mid-Corp)", "Tier 1 (Product/MNC)"]
    predicted_tier = tier_labels[tier_idx]
    
    # CTC prediction
    pred_ctc = float(reg_ctc.predict(input_row)[0])
    
    # CTC range
    ctc_min = max(3.0, round(pred_ctc * 0.85, 1))
    ctc_max = round(pred_ctc * 1.15, 1)
    
    # Pillar scores
    pillar_scores = calculate_pillar_scores(profile)
    
    # Feature contributions / impact
    feature_importances = clf_placement.feature_importances_
    factors = []
    for col, imp in sorted(zip(FEATURE_COLS, feature_importances), key=lambda x: x[1], reverse=True):
        factors.append({"Feature": col.replace("_", " "), "Importance": round(float(imp) * 100, 1)})
        
    return {
        "placement_probability": round(float(prob), 1),
        "predicted_tier": predicted_tier,
        "tier_probabilities": {
            "Tier 1 (Product/MNC)": round(float(tier_probs[2]) * 100, 1),
            "Tier 2 (Tech Startup)": round(float(tier_probs[1]) * 100, 1),
            "Tier 3 (Service/Mass)": round(float(tier_probs[0]) * 100, 1),
        },
        "predicted_ctc": round(pred_ctc, 1),
        "ctc_range": f"{ctc_min} - {ctc_max} LPA",
        "pillar_scores": pillar_scores,
        "factors": factors
    }

if __name__ == "__main__":
    train_models()
    sample_profile = {
        "CGPA": 8.4,
        "Tenth_Percentage": 88.0,
        "Twelfth_Percentage": 85.0,
        "DSA_Problems_Solved": 220,
        "Projects_Count": 3,
        "Internships_Count": 1,
        "Hackathons_Participated": 2,
        "Certifications_Count": 2,
        "Aptitude_Test_Score": 78.0,
        "Soft_Skills_Rating": 4.2,
        "Backlogs": 0
    }
    result = predict_student_readiness(sample_profile)
    print("Sample Prediction Output:")
    for k, v in result.items():
        print(f"  {k}: {v}")

