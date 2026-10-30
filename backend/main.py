from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import os, sys, sqlite3, hashlib, hmac, secrets, json, time, re
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))
from ml_model import predict_student_readiness, calculate_pillar_scores, FEATURE_COLS, get_models
from utils import analyze_resume_text, generate_custom_roadmap, ROLE_TAXONOMY, DIAGNOSTIC_QUIZ

DB_PATH = Path(os.getenv('DATABASE_PATH', str(BASE / 'placement_readiness.db')))
SECRET = os.getenv('APP_SECRET_KEY', 'change-this-secret-before-public-deployment')
if SECRET == 'change-this-secret-before-public-deployment' and os.getenv('RENDER'):
    raise RuntimeError('Set APP_SECRET_KEY in the deployment environment before going public.')
app = FastAPI(title='Placement Readiness API', version='1.0.0', description='Placement prediction and student readiness API')
origins = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',')
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

class RegisterInput(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
class LoginInput(BaseModel):
    email: EmailStr
    password: str
class Profile(BaseModel):
    CGPA: float = Field(ge=0, le=10)
    Tenth_Percentage: float = Field(ge=0, le=100)
    Twelfth_Percentage: float = Field(ge=0, le=100)
    DSA_Problems_Solved: int = Field(ge=0, le=10000)
    Projects_Count: int = Field(ge=0, le=100)
    Internships_Count: int = Field(ge=0, le=50)
    Hackathons_Participated: int = Field(ge=0, le=100)
    Certifications_Count: int = Field(ge=0, le=100)
    Aptitude_Test_Score: float = Field(ge=0, le=100)
    Soft_Skills_Rating: float = Field(ge=1, le=5)
    Backlogs: int = Field(ge=0, le=50)
class ResumeInput(BaseModel):
    text: str = Field(min_length=20, max_length=50000)
    role: str
class RoadmapInput(BaseModel):
    pillar_scores: dict
    target_role: str


def conn():
    c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; return c
def init_db():
    with conn() as c:
        c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP)')
        c.execute('CREATE TABLE IF NOT EXISTS assessments (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, profile TEXT NOT NULL, result TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(user_id) REFERENCES users(id))')
        c.execute('CREATE TABLE IF NOT EXISTS resumes (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, role TEXT NOT NULL, score INTEGER NOT NULL, result TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP)')
init_db()

def hash_password(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest=hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), 240000).hex()
    return f'{salt}${digest}'
def verify_password(password, saved):
    try:
        salt,digest=saved.split('$',1); return hmac.compare_digest(hash_password(password,salt).split('$',1)[1],digest)
    except Exception: return False
def make_token(user_id):
    payload=f'{user_id}:{int(time.time())+60*60*24*7}'
    sig=hmac.new(SECRET.encode(),payload.encode(),hashlib.sha256).hexdigest()
    return f'{payload}:{sig}'
def current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith('Bearer '): raise HTTPException(401,'Please sign in to continue.')
    try:
        raw=authorization[7:]; uid,expiry,sig=raw.split(':',2); payload=f'{uid}:{expiry}'
        expected=hmac.new(SECRET.encode(),payload.encode(),hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig,expected) or int(expiry)<time.time(): raise ValueError()
        with conn() as c: row=c.execute('SELECT id,name,email FROM users WHERE id=?',(int(uid),)).fetchone()
        if not row: raise ValueError()
        return dict(row)
    except Exception: raise HTTPException(401,'Your session expired. Please sign in again.')

@app.get('/api/health')
def health():
    try:
        get_models(); model_status='loaded'
    except Exception as e: model_status=f'error: {str(e)}'
    return {'status':'ok','service':'Placement Readiness API','models':model_status}
@app.post('/api/auth/register')
def register(data:RegisterInput):
    try:
        with conn() as c: cur=c.execute('INSERT INTO users(name,email,password_hash) VALUES(?,?,?)',(data.name.strip(),data.email.lower(),hash_password(data.password))); uid=cur.lastrowid
    except sqlite3.IntegrityError: raise HTTPException(409,'An account with this email already exists.')
    return {'token':make_token(uid),'user':{'id':uid,'name':data.name.strip(),'email':data.email.lower()}}
@app.post('/api/auth/login')
def login(data:LoginInput):
    with conn() as c: row=c.execute('SELECT * FROM users WHERE email=?',(data.email.lower(),)).fetchone()
    if not row or not verify_password(data.password,row['password_hash']): raise HTTPException(401,'Incorrect email or password.')
    return {'token':make_token(row['id']),'user':{'id':row['id'],'name':row['name'],'email':row['email']}}
@app.get('/api/auth/me')
def me(user=Depends(current_user)): return {'user':user}
@app.get('/api/meta')
def meta(): return {'features':FEATURE_COLS,'roles':list(ROLE_TAXONOMY.keys()),'role_details':{k:v['description'] for k,v in ROLE_TAXONOMY.items()}}
@app.post('/api/predict')
def predict(profile:Profile,user=Depends(current_user)):
    values=profile.model_dump()
    try:
        result=predict_student_readiness(values)
        # Save every successful assessment to the signed-in user's history.
        with conn() as c: c.execute('INSERT INTO assessments(user_id,profile,result) VALUES(?,?,?)',(user['id'],json.dumps(values),json.dumps(result)))
        return {'profile':values,'result':result,'created_at':time.strftime('%Y-%m-%d %H:%M:%S')}
    except Exception as e: raise HTTPException(500,'Prediction failed. Check backend model compatibility. Details: '+str(e))
@app.get('/api/history')
def history(user=Depends(current_user)):
    with conn() as c: rows=c.execute('SELECT id,profile,result,created_at FROM assessments WHERE user_id=? ORDER BY id DESC LIMIT 20',(user['id'],)).fetchall()
    return {'items':[{'id':r['id'],'profile':json.loads(r['profile']),'result':json.loads(r['result']),'created_at':r['created_at']} for r in rows]}
@app.post('/api/resume/analyze')
async def resume_analyze(role: str, file: UploadFile=File(...), user=Depends(current_user)):
    if file.size and file.size>5*1024*1024: raise HTTPException(413,'Please upload a file under 5 MB.')
    name=(file.filename or '').lower(); content=await file.read()
    if len(content)>5*1024*1024: raise HTTPException(413,'Please upload a file under 5 MB.')
    if name.endswith('.txt'):
        text=content.decode('utf-8',errors='ignore')
    elif name.endswith('.pdf'):
        try:
            from pypdf import PdfReader
            import io
            reader=PdfReader(io.BytesIO(content)); text='\n'.join(page.extract_text() or '' for page in reader.pages)
        except ImportError: raise HTTPException(500,'PDF support is missing. Install requirements.txt again.')
        except Exception: raise HTTPException(400,'Could not read this PDF. Try a text-based PDF or upload a .txt file.')
    else: raise HTTPException(400,'Upload a PDF or TXT resume.')
    result=analyze_resume_text(text,role)
    with conn() as c: c.execute('INSERT INTO resumes(user_id,role,score,result) VALUES(?,?,?,?)',(user['id'],role,result['score'],json.dumps(result)))
    return {'filename':file.filename,'role':role,'result':result}
@app.post('/api/resume/analyze-text')
def resume_text(data:ResumeInput,user=Depends(current_user)):
    if data.role not in ROLE_TAXONOMY: raise HTTPException(400,'Choose a valid target role.')
    result=analyze_resume_text(data.text,data.role)
    with conn() as c: c.execute('INSERT INTO resumes(user_id,role,score,result) VALUES(?,?,?,?)',(user['id'],data.role,result['score'],json.dumps(result)))
    return {'role':data.role,'result':result}
@app.post('/api/roadmap')
def roadmap(data:RoadmapInput,user=Depends(current_user)):
    if data.target_role not in ROLE_TAXONOMY: raise HTTPException(400,'Choose a valid target role.')
    return generate_custom_roadmap(data.pillar_scores,data.target_role)
@app.get('/api/quiz')
def quiz(user=Depends(current_user)):
    return {'questions':[{'id':q['id'],'category':q['category'],'question':q['question'],'options':q['options']} for q in DIAGNOSTIC_QUIZ]}
class QuizAnswer(BaseModel): answers: dict
@app.post('/api/quiz/submit')
def quiz_submit(data:QuizAnswer,user=Depends(current_user)):
    qs={str(q['id']):q for q in DIAGNOSTIC_QUIZ}; correct=0; details=[]
    for qid,q in qs.items():
        chosen=data.answers.get(qid); ok=chosen==q['answer']; correct+=int(ok)
        details.append({'id':q['id'],'question':q['question'],'chosen':chosen,'answer':q['answer'],'correct':ok,'explanation':q.get('explanation',''),'category':q['category']})
    return {'score':correct,'total':len(qs),'percentage':round(correct/max(1,len(qs))*100),'details':details}
@app.get('/api/summary')
def summary(user=Depends(current_user)):
    with conn() as c:
        count=c.execute('SELECT COUNT(*) n FROM assessments WHERE user_id=?',(user['id'],)).fetchone()['n']
        latest=c.execute('SELECT result,created_at FROM assessments WHERE user_id=? ORDER BY id DESC LIMIT 1',(user['id'],)).fetchone()
        resumes=c.execute('SELECT COUNT(*) n FROM resumes WHERE user_id=?',(user['id'],)).fetchone()['n']
    return {'assessment_count':count,'resume_count':resumes,'latest':({'result':json.loads(latest['result']),'created_at':latest['created_at']} if latest else None)}
