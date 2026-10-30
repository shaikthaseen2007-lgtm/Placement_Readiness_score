import React, {useEffect, useMemo, useState} from 'react';
import {createRoot} from 'react-dom/client';
import {Activity, ArrowDownRight, ArrowRight, Award, BarChart3, BookOpen, BriefcaseBusiness, Check, ChevronDown, CircleHelp, Clock3, Code2, FileText, Gauge, GraduationCap, History, LayoutDashboard, LogOut, Menu, Rocket, ShieldCheck, Sparkles, Target, TrendingUp, Upload, UserRound, X, Zap} from 'lucide-react';
import {Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis, Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, BarChart, Bar, Legend, LineChart, Line} from 'recharts';
import './style.css';

const API=(import.meta.env.VITE_API_URL||'http://localhost:8000/api').replace(/\/$/,'');
const initialProfile={CGPA:8.2,Tenth_Percentage:85,Twelfth_Percentage:83,DSA_Problems_Solved:120,Projects_Count:2,Internships_Count:0,Hackathons_Participated:1,Certifications_Count:2,Aptitude_Test_Score:72,Soft_Skills_Rating:3.5,Backlogs:0};
const nav=[['Overview',LayoutDashboard],['Readiness assessment',Gauge],['Resume analyzer',FileText],['90-day roadmap',Rocket],['Skill quiz',CircleHelp],['Assessment history',History]];
async function api(path,{token,...opts}={}){const res=await fetch(`${API}${path}`,{...opts,headers:{...(opts.body instanceof FormData?{}:{'Content-Type':'application/json'}),...(token?{Authorization:`Bearer ${token}`}:{}) ,...(opts.headers||{})}});let data;try{data=await res.json()}catch{data={detail:'Unexpected server response'}}if(!res.ok)throw new Error(data.detail||'Request failed');return data}
function App(){
 const [token,setToken]=useState(localStorage.getItem('prs_token')||'');const [user,setUser]=useState(null);const [authMode,setAuthMode]=useState('login');const [page,setPage]=useState('Overview');const [mobileNav,setMobileNav]=useState(false);const [meta,setMeta]=useState({roles:[],role_details:{}});const [profile,setProfile]=useState(initialProfile);const [prediction,setPrediction]=useState(null);const [history,setHistory]=useState([]);const [summary,setSummary]=useState(null);const [busy,setBusy]=useState(false);const [error,setError]=useState('');const [notice,setNotice]=useState('');
 useEffect(()=>{api('/meta').then(setMeta).catch(()=>{});if(token)api('/auth/me',{token}).then(d=>setUser(d.user)).catch(()=>{localStorage.removeItem('prs_token');setToken('')})},[]);
 useEffect(()=>{if(token&&user){Promise.all([api('/history',{token}),api('/summary',{token})]).then(([h,s])=>{setHistory(h.items);setSummary(s)}).catch(e=>setError(e.message))}},[token,user]);
 const authSubmit=async(e)=>{e.preventDefault();setBusy(true);setError('');const fd=new FormData(e.currentTarget);try{const data=await api(`/auth/${authMode}`,{method:'POST',body:JSON.stringify({name:fd.get('name'),email:fd.get('email'),password:fd.get('password')})});localStorage.setItem('prs_token',data.token);setToken(data.token);setUser(data.user);setNotice(authMode==='login'?'Welcome back.':'Your workspace is ready.')}catch(err){setError(err.message)}finally{setBusy(false)}};
 const logout=()=>{localStorage.removeItem('prs_token');setToken('');setUser(null);setPrediction(null);setPage('Overview')};
 const runPrediction=async(e)=>{e.preventDefault();setBusy(true);setError('');try{const d=await api('/predict',{token,method:'POST',body:JSON.stringify(Object.fromEntries(Object.entries(profile).map(([k,v])=>[k,Number(v)])))});setPrediction(d);setNotice('Assessment completed and saved to your history.');setPage('Readiness assessment');const h=await api('/history',{token});setHistory(h.items);setSummary(await api('/summary',{token}))}catch(err){setError(err.message)}finally{setBusy(false)}};
 const go=p=>{setPage(p);setMobileNav(false);setError('');setNotice('')};
 if(!token||!user)return <Auth mode={authMode} setMode={setAuthMode} submit={authSubmit} busy={busy} error={error}/>;
 return <div className="app-shell"><aside className={`sidebar ${mobileNav?'show':''}`}><div className="brand"><div className="brand-mark"><Activity size={22}/></div><div><b>ReadySet</b><span>PLACEMENT INTELLIGENCE</span></div><button className="icon-btn close-nav" onClick={()=>setMobileNav(false)}><X size={18}/></button></div><div className="workspace-label">WORKSPACE</div><nav>{nav.map(([n,Icon])=><button key={n} className={`nav-item ${page===n?'active':''}`} onClick={()=>go(n)}><Icon size={18}/><span>{n}</span>{n==='Readiness assessment'&&<span className="nav-dot"/>}</button>)}</nav><div className="sidebar-bottom"><div className="help-card"><div className="help-icon"><Sparkles size={18}/></div><b>Small steps. Big outcomes.</b><p>Your next opportunity starts with knowing where you stand.</p><button onClick={()=>go('90-day roadmap')}>View your roadmap <ArrowRight size={14}/></button></div><div className="profile-mini"><div className="avatar">{user.name?.slice(0,1).toUpperCase()}</div><div className="profile-copy"><b>{user.name}</b><span>{user.email}</span></div><button className="icon-btn" title="Sign out" onClick={logout}><LogOut size={17}/></button></div></div></aside><div className="main-area"><header className="topbar"><button className="icon-btn mobile-menu" onClick={()=>setMobileNav(true)}><Menu/></button><div className="crumb">Workspace <span>/</span> <b>{page}</b></div><div className="top-right"><span className="status"><i/> Models connected</span><button className="top-avatar" title={user.name}>{user.name?.slice(0,1).toUpperCase()}</button></div></header><main className="content"><div className="page-head"><div><div className="eyebrow"><span className="eyebrow-line"/> YOUR CAREER, WITH CLARITY</div><h1>{page==='Overview'?<>Make your next move <em>count.</em></>:page}</h1><p>{page==='Overview'?'A clearer picture of your placement readiness — and what to do next.':page==='Readiness assessment'?'Use your current profile to estimate placement outcomes and uncover skill gaps.':page==='Resume analyzer'?'See how closely your resume matches the skills expected for your target role.':page==='90-day roadmap'?'A focused, actionable plan built around your weakest readiness area.':page==='Skill quiz'?'Test your technical fundamentals and find topics worth revisiting.':'Review your previous predictions and track your progress.'}</p></div><div className="head-actions"><span className="updated"><span className="live-dot"/> PERSONAL WORKSPACE</span></div></div>{error&&<div className="alert error"><X size={17}/>{error}<button onClick={()=>setError('')}><X size={15}/></button></div>}{notice&&<div className="alert success"><Check size={17}/>{notice}<button onClick={()=>setNotice('')}><X size={15}/></button></div>}
 {page==='Overview'&&<Overview user={user} summary={summary} prediction={prediction||summary?.latest} history={history} go={go}/>}
 {page==='Readiness assessment'&&<Assessment profile={profile} setProfile={setProfile} submit={runPrediction} busy={busy} prediction={prediction||summary?.latest} go={go}/>}
 {page==='Resume analyzer'&&<ResumeAnalyzer token={token} roles={meta.roles} roleDetails={meta.role_details}/>}
 {page==='90-day roadmap'&&<Roadmap token={token} prediction={prediction||summary?.latest} roles={meta.roles}/>}
 {page==='Skill quiz'&&<Quiz token={token}/>}
 {page==='Assessment history'&&<HistoryPage history={history} select={x=>{setPrediction(x);setProfile(x.profile);go('Readiness assessment')}}/>}
 <footer className="footer"><span>READYSET <b>•</b> BUILT FOR YOUR NEXT CHAPTER</span><span>Predictions are estimates, not placement guarantees.</span></footer></main></div></div>
}
function Auth({mode,setMode,submit,busy,error}){return <div className="auth-page"><div className="auth-left"><div className="brand auth-brand"><div className="brand-mark"><Activity size={22}/></div><div><b>ReadySet</b><span>PLACEMENT INTELLIGENCE</span></div></div><div className="auth-copy"><div className="eyebrow"><span className="eyebrow-line"/> YOUR CAREER, WITH CLARITY</div><h1>Know your strengths.<br/><em>Own your future.</em></h1><p>A smarter way to understand your placement readiness, strengthen your profile, and walk into interviews with confidence.</p><div className="auth-stats"><div><b>01</b><span>Measure your readiness</span></div><div><b>02</b><span>Close your skill gaps</span></div><div><b>03</b><span>Build your next 90 days</span></div></div></div><div className="auth-foot">PERSONAL PLACEMENT INTELLIGENCE <span>•</span> MADE FOR YOUR NEXT CHAPTER</div></div><div className="auth-right"><div className="auth-form-wrap"><div className="mobile-auth-brand"><div className="brand-mark"><Activity size={22}/></div><b>ReadySet</b></div><div className="form-kicker">YOUR WORKSPACE AWAITS</div><h2>{mode==='login'?'Welcome back.':'Start with a clear plan.'}</h2><p className="form-sub">{mode==='login'?'Sign in to continue building your placement profile.':'Create your account and make your next step intentional.'}</p>{error&&<div className="alert error">{error}</div>}<form onSubmit={submit} className="auth-form">{mode==='register'&&<label>Full name<input name="name" placeholder="Your name" minLength="2" required/></label>}<label>Email address<input name="email" type="email" placeholder="you@example.com" required/></label><label>Password<input name="password" type="password" minLength="8" placeholder="At least 8 characters" required/></label><button className="primary-btn full" disabled={busy}>{busy?'Please wait…':mode==='login'?'Sign in to workspace':'Create my workspace'} <ArrowRight size={17}/></button></form><div className="auth-switch">{mode==='login'?"New to ReadySet?":"Already have an account?"} <button onClick={()=>setMode(mode==='login'?'register':'login')}>{mode==='login'?'Create an account':'Sign in'}</button></div><div className="secure-note"><ShieldCheck size={15}/> Your profile and assessment history are private to your account.</div></div></div></div>}
function Overview({user,summary,prediction,history,go}){const result=prediction?.result;const readiness=result?.pillar_scores?.Overall_Readiness;const probability=result?.placement_probability;return <><div className="hero-card"><div className="hero-text"><div className="hero-label"><Sparkles size={15}/> YOUR PERSONAL PLACEMENT PLAN</div><h2>Progress isn't a straight line.<br/>It's a series of <em>smart moves.</em></h2><p>Start with an honest assessment. Then turn the insights into a plan you can act on.</p><button className="hero-btn" onClick={()=>go('Readiness assessment')}>{result?'Update my assessment':'Check my readiness'} <ArrowRight size={16}/></button></div><div className="hero-art"><div className="orbit orbit-one"/><div className="orbit orbit-two"/><div className="hero-center"><Target size={38}/></div><div className="float-card float-top"><TrendingUp size={15}/><span><b>{readiness??'—'}{readiness!=null?'%':''}</b><small>Readiness index</small></span></div><div className="float-card float-bottom"><Zap size={15}/><span><b>{probability!=null?`${probability}%`:'Start here'}</b><small>Placement estimate</small></span></div></div><div className="hero-watermark">RS.</div></div><div className="section-title-row"><div><h3>Your snapshot</h3><p>A quick look at where you are today.</p></div><span className="tiny-muted">{result?'LATEST ASSESSMENT':'READY WHEN YOU ARE'}</span></div><div className="metric-grid"><Metric icon={Gauge} label="Readiness index" value={readiness!=null?`${readiness}%`:'—'} hint={readiness!=null?'Across five readiness pillars':'Complete an assessment'} tone="purple"/><Metric icon={BriefcaseBusiness} label="Placement probability" value={probability!=null?`${probability}%`:'—'} hint="Model-based estimate" tone="mint"/><Metric icon={FileText} label="Resume reviews" value={summary?.resume_count??0} hint="ATS-style keyword checks" tone="amber"/><Metric icon={History} label="Assessments" value={summary?.assessment_count??0} hint="Saved to your account" tone="blue"/></div><div className="overview-lower"><div className="panel focus-panel"><div className="panel-head"><div><h3>Your next best step</h3><p>Keep your momentum with one focused action.</p></div><div className="panel-icon"><Target size={18}/></div></div>{result?<><div className="focus-score"><div className="score-ring" style={{'--score':`${readiness||0}%`}}><div><b>{readiness}</b><small>/100</small></div></div><div><span className="pill pill-green">ASSESSMENT READY</span><h4>{readiness>=75?'Turn readiness into interview practice':readiness>=50?'Build consistency in your weakest pillar':'Start with the fundamentals'}</h4><p>Target role predictions are estimates. Use the roadmap to turn your lowest score into a practical weekly routine.</p></div></div><button className="text-btn" onClick={()=>go('90-day roadmap')}>Open my 90-day roadmap <ArrowRight size={15}/></button></>:<div className="empty-state"><div className="empty-icon"><BarChart3 size={25}/></div><h4>Your insights will appear here</h4><p>Share your academic, coding and experience profile to see a readiness breakdown.</p><button className="primary-btn" onClick={()=>go('Readiness assessment')}>Start assessment <ArrowRight size={16}/></button></div>}</div><div className="panel quick-panel"><div className="panel-head"><div><h3>Build your profile</h3><p>Three tools, one stronger application.</p></div><div className="panel-icon pale"><Rocket size={18}/></div></div><div className="quick-list"><Quick icon={Gauge} n="01" title="Readiness assessment" desc="Understand your current baseline" onClick={()=>go('Readiness assessment')}/><Quick icon={FileText} n="02" title="Resume analyzer" desc="Find missing role-specific skills" onClick={()=>go('Resume analyzer')}/><Quick icon={BookOpen} n="03" title="Technical skill quiz" desc="Check your CS fundamentals" onClick={()=>go('Skill quiz')}/></div><div className="quick-footer"><span><ShieldCheck size={14}/> Your progress stays in your workspace</span></div></div></div><div className="charts-grid"><div className="panel chart-panel"><div className="panel-head"><div><h3>Readiness radar</h3><p>Compare your five readiness pillars at a glance.</p></div><div className="panel-icon"><Target size={18}/></div></div>{result?.pillar_scores?<div className="chart-area"><ResponsiveContainer width="100%" height={300}><RadarChart data={Object.entries(result.pillar_scores).filter(([k])=>k!=='Overall_Readiness').map(([name,score])=>({subject:name.replace(' & Problem Solving','').replace(' & Development',''),score:Number(score)}))}><PolarGrid/><PolarAngleAxis dataKey="subject" tick={{fontSize:12,fill:'#667085'}}/><PolarRadiusAxis angle={30} domain={[0,100]} tick={{fontSize:10}}/><Radar name="Readiness" dataKey="score" stroke="#6b5ce7" fill="#8b7cf6" fillOpacity={0.38}/><Tooltip formatter={(v)=>[`${v}%`,'Score']}/></RadarChart></ResponsiveContainer></div>:<div className="chart-empty"><BarChart3 size={26}/><b>Radar chart awaits your assessment</b><span>Complete the readiness assessment to see your pillar scores.</span><button className="text-btn" onClick={()=>go('Readiness assessment')}>Take assessment <ArrowRight size={14}/></button></div>}</div><div className="panel chart-panel"><div className="panel-head"><div><h3>Progress over time</h3><p>Your saved assessment scores.</p></div><div className="panel-icon pale"><TrendingUp size={18}/></div></div>{history?.length?<div className="chart-area"><ResponsiveContainer width="100%" height={300}><LineChart data={[...history].reverse().map((x,i)=>({attempt:i+1,date:String(x.created_at||'').slice(0,10),readiness:Number(x.result?.pillar_scores?.Overall_Readiness||0),placement:Number(x.result?.placement_probability||0)}))}><CartesianGrid strokeDasharray="3 3" stroke="#edf0f6"/><XAxis dataKey="attempt" tick={{fontSize:12}} label={{value:'Assessment',position:'insideBottom',offset:-4,fontSize:12}}/><YAxis domain={[0,100]} tick={{fontSize:11}}/><Tooltip labelFormatter={(v)=>`Assessment ${v}`} formatter={(v,n)=>[`${v}%`,n==='readiness'?'Readiness':'Placement estimate']}/><Legend/><Line type="monotone" dataKey="readiness" name="Readiness" stroke="#6b5ce7" strokeWidth={3} dot={{r:4}}/><Line type="monotone" dataKey="placement" name="Placement estimate" stroke="#17a784" strokeWidth={3} dot={{r:4}}/></LineChart></ResponsiveContainer></div>:<div className="chart-empty"><TrendingUp size={26}/><b>Your progress chart will appear here</b><span>Complete more assessments to track your readiness over time.</span><button className="text-btn" onClick={()=>go('Readiness assessment')}>Start assessment <ArrowRight size={14}/></button></div>}</div></div><div className="bottom-banner"><div className="banner-symbol"><GraduationCap size={22}/></div><div><b>Consistency beats last-minute preparation.</b><p>Choose one skill gap and give it focused time this week.</p></div><button onClick={()=>go('90-day roadmap')}>Plan my next 90 days <ArrowRight size={15}/></button></div></>}
function Metric({icon:Icon,label,value,hint,tone}){return <div className="metric-card"><div className={`metric-icon ${tone}`}><Icon size={18}/></div><div className="metric-label">{label}</div><div className="metric-value">{value}</div><div className="metric-hint">{hint}</div></div>}
function Quick({icon:Icon,n,title,desc,onClick}){return <button className="quick-item" onClick={onClick}><div className="quick-item-icon"><Icon size={18}/></div><div><b>{title}</b><span>{desc}</span></div><span className="quick-num">{n}</span><ArrowRight className="quick-arrow" size={16}/></button>}
const fields=[['CGPA','CGPA',0,10,.1,'Academic'],['Tenth_Percentage','10th percentage',0,100,1,'Academic'],['Twelfth_Percentage','12th percentage',0,100,1,'Academic'],['DSA_Problems_Solved','DSA problems solved',0,1000,1,'Technical'],['Projects_Count','Projects completed',0,50,1,'Experience'],['Internships_Count','Internships completed',0,20,1,'Experience'],['Hackathons_Participated','Hackathons participated',0,50,1,'Experience'],['Certifications_Count','Certifications earned',0,50,1,'Experience'],['Aptitude_Test_Score','Aptitude test score (%)',0,100,1,'Skills'],['Soft_Skills_Rating','Soft skills rating (1–5)',1,5,.1,'Skills'],['Backlogs','Current / historical backlogs',0,20,1,'Academic']];
function Assessment({profile,setProfile,submit,busy,prediction,go}) {
  const [group,setGroup] = useState('Academic');
  const result = prediction?.result;
  const pillars = result?.pillar_scores;

  return (
    <div className="assessment-layout">
      <form className="panel assessment-form" onSubmit={submit}>
        <div className="panel-head">
          <div>
            <h3>Student profile</h3>
            <p>Enter your latest details for a more relevant estimate.</p>
          </div>
          <span className="pill pill-purple">11 INPUTS</span>
        </div>

        <div className="form-tabs">
          {['Academic','Technical','Experience','Skills'].map(g => (
            <button
              type="button"
              className={group===g?'selected':''}
              key={g}
              onClick={() => setGroup(g)}
            >
              {g}
            </button>
          ))}
        </div>

        <div className="field-grid">
          {fields.filter(f => f[5]===group).map(([key,label,min,max,step]) => (
            <label className="field" key={key}>
              <span>{label}</span>
              <div className="number-wrap">
                <input
                  type="number"
                  min={min}
                  max={max}
                  step={step}
                  required
                  value={profile[key]}
                  onChange={e => setProfile({...profile,[key]:e.target.value})}
                />
                {key==='CGPA' ? <small>/ 10</small> :
                 key==='Soft_Skills_Rating' ? <small>/ 5</small> :
                 key.includes('Percentage') || key==='Aptitude_Test_Score' ? <small>%</small> : null}
              </div>
              <div className="field-hint">
                {key==='DSA_Problems_Solved' ? 'Total solved across coding platforms' :
                 key==='Soft_Skills_Rating' ? 'Self-rating: communication, teamwork, confidence' :
                 key==='Backlogs' ? 'Include active and historical backlogs' :
                 'Use your current verified profile'}
              </div>
            </label>
          ))}
        </div>

        <div className="form-note">
          <ShieldCheck size={16}/>
          <span>Your details are saved with your account so you can compare assessments over time.</span>
        </div>

        <button className="primary-btn full" disabled={busy}>
          {busy?'Analyzing your profile…':'Calculate readiness score'}
          <ArrowRight size={17}/>
        </button>
      </form>

      <div className="results-column">
        {result ? (
          <>
            <div className="panel score-panel">
              <div className="result-top">
                <div>
                  <span className="eyebrow-mini">YOUR READINESS INDEX</span>
                  <div className="big-score">
                    {pillars?.Overall_Readiness}
                    <small>/100</small>
                  </div>
                  <span className="pill pill-green">PROFILE ANALYZED</span>
                </div>

                <div
                  className="score-ring large"
                  style={{'--score':`${pillars?.Overall_Readiness||0}%`}}
                >
                  <div><Gauge size={25}/></div>
                </div>
              </div>

              <div className="score-track">
                <i style={{width:`${pillars?.Overall_Readiness||0}%`}}/>
              </div>

              <div className="score-scale">
                <span>Starting point</span>
                <span>Strong readiness</span>
              </div>
            </div>

            <div className="panel">
              <div className="panel-head">
                <div>
                  <h3>Readiness pillars</h3>
                  <p>What is contributing to your overall score.</p>
                </div>
              </div>

              <div className="pillar-list">
                {Object.entries(pillars||{})
                  .filter(([k])=>k!=='Overall_Readiness')
                  .map(([name,score])=>(
                    <div className="pillar" key={name}>
                      <div>
                        <span>{name}</span>
                        <b>{score}%</b>
                      </div>
                      <div className="pillar-track">
                        <i style={{width:`${score}%`}}/>
                      </div>
                    </div>
                  ))}
              </div>
            </div>

            <div className="panel prediction-panel">
              <div className="panel-head">
                <div>
                  <h3>Model predictions</h3>
                  <p>Estimates from your saved ML models.</p>
                </div>
                <TrendingUp size={18}/>
              </div>

              <div className="prediction-stat">
                <span>Predicted company tier</span>
                <b>{result.predicted_tier}</b>
              </div>

              <div className="prediction-stat">
                <span>Estimated CTC</span>
                <b>₹{result.predicted_ctc} LPA</b>
              </div>

              <div className="prediction-stat">
                <span>Estimated range</span>
                <b>{result.ctc_range}</b>
              </div>

              <div className="prediction-stat">
                <span>Placement probability</span>
                <b>{result.placement_probability}%</b>
              </div>

              <p className="disclaimer">
                These are model-generated estimates based on the supplied dataset, not a guarantee of employment or salary.
              </p>

              <button
                className="text-btn"
                onClick={()=>go('90-day roadmap')}
              >
                Build a plan from these results <ArrowRight size={15}/>
              </button>
            </div>
          </>
        ) : (
          <div className="panel result-placeholder">
            <div className="placeholder-illustration">
              <div className="placeholder-ring"><Gauge size={34}/></div>
              <div className="placeholder-chip chip-a"><TrendingUp size={15}/></div>
              <div className="placeholder-chip chip-b"><Target size={15}/></div>
            </div>

            <span className="eyebrow-mini">YOUR RESULTS, VISUALIZED</span>
            <h3>Your readiness story starts here.</h3>
            <p>
              Complete your profile and we'll show your readiness pillars,
              placement estimate, company tier, and salary range.
            </p>

            <div className="placeholder-points">
              <span><Check size={15}/> ML-based predictions</span>
              <span><Check size={15}/> Five readiness pillars</span>
              <span><Check size={15}/> Personalized next steps</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
function ResumeAnalyzer({token,roles,roleDetails}){const [role,setRole]=useState(roles[0]||'Software Development Engineer (SDE)');const [file,setFile]=useState(null);const [text,setText]=useState('');const [result,setResult]=useState(null);const [busy,setBusy]=useState(false);const [err,setErr]=useState('');const [mode,setMode]=useState('file');async function analyze(e){e.preventDefault();setBusy(true);setErr('');setResult(null);try{let d;if(mode==='file'){if(!file)throw new Error('Choose a PDF or TXT resume first.');const fd=new FormData();fd.append('file',file);d=await api(`/resume/analyze?role=${encodeURIComponent(role)}`,{token,method:'POST',body:fd})}else d=await api('/resume/analyze-text',{token,method:'POST',body:JSON.stringify({text,role})});setResult(d.result)}catch(e){setErr(e.message)}finally{setBusy(false)}}return <div className="resume-layout"><form className="panel resume-form" onSubmit={analyze}><div className="panel-head"><div><h3>Resume compatibility check</h3><p>Compare your resume against a target role's keyword taxonomy.</p></div><div className="panel-icon"><FileText size={18}/></div></div><label className="field"><span>Target role</span><select value={role} onChange={e=>setRole(e.target.value)}>{roles.map(r=><option key={r}>{r}</option>)}</select></label><div className="mode-switch"><button type="button" className={mode==='file'?'selected':''} onClick={()=>setMode('file')}><Upload size={15}/> Upload file</button><button type="button" className={mode==='text'?'selected':''} onClick={()=>setMode('text')}><FileText size={15}/> Paste text</button></div>{mode==='file'?<label className="upload-zone"><input type="file" accept=".pdf,.txt,application/pdf,text/plain" onChange={e=>setFile(e.target.files?.[0]||null)}/><div className="upload-icon"><Upload size={22}/></div><b>{file?file.name:'Drop your resume here'}</b><span>{file?`${(file.size/1024).toFixed(0)} KB · Ready to analyze`:'PDF or TXT · Maximum 5 MB'}</span><small>Click to browse files</small></label>:<label className="field"><span>Resume text</span><textarea rows="10" value={text} onChange={e=>setText(e.target.value)} placeholder="Paste your resume summary, skills, projects and experience…"/></label>}{err&&<div className="alert error">{err}</div>}<button className="primary-btn full" disabled={busy}>{busy?'Reviewing resume…':'Analyze resume match'} <ArrowRight size={16}/></button><p className="micro-copy">This is a keyword-based ATS-style estimate, not a guarantee of how a real employer's system will score your resume.</p></form><div className="resume-side"><div className="panel role-panel"><span className="eyebrow-mini">ROLE PROFILE</span><div className="role-symbol"><BriefcaseBusiness size={22}/></div><h3>{role}</h3><p>{roleDetails[role]||'Choose a role to view its focus areas.'}</p><div className="role-tags"><span>Required keywords</span><span>Good-to-have skills</span><span>Impact metrics</span></div></div>{result?<div className="panel resume-result"><div className="panel-head"><div><h3>Resume match</h3><p>Keyword coverage overview.</p></div><div className="resume-score">{result.score}<small>/100</small></div></div><div className="score-track"><i style={{width:`${result.score}%`}}/></div><div className="match-columns"><div><b className="good-text"><Check size={14}/> Matched skills ({result.matched_required.length+result.matched_optional.length})</b><div className="tag-list">{[...result.matched_required,...result.matched_optional].map(x=><span key={x}>{x}</span>)}</div></div><div><b className="missing-text"><ArrowDownRight size={14}/> Missing skills ({result.missing_required.length+result.missing_optional.length})</b><div className="tag-list missing">{[...result.missing_required,...result.missing_optional].map(x=><span key={x}>{x}</span>)}</div></div></div><h4>Recommendations</h4><ul className="recommendations">{result.recommendations.map((x,i)=><li key={i}>{x.replace(/\*\*/g,'')}</li>)}</ul></div>:<div className="panel checklist-panel"><h3>What you'll get</h3>{[['Role keyword coverage','See which core skills are visible.'],['Missing skill signals','Find gaps to address honestly.'],['Actionable recommendations','Improve evidence and impact statements.']].map(([a,b])=><div className="checklist-item" key={a}><div><Check size={15}/></div><span><b>{a}</b><small>{b}</small></span></div>)}</div>}</div></div>}
function Roadmap({token,prediction,roles}){const [role,setRole]=useState(roles[0]||'Software Development Engineer (SDE)');const [data,setData]=useState(null);const [err,setErr]=useState('');const [busy,setBusy]=useState(false);const pillars=prediction?.result?.pillar_scores;useEffect(()=>{if(!pillars)return;setBusy(true);api('/roadmap',{token,method:'POST',body:JSON.stringify({pillar_scores:pillars,target_role:role})}).then(setData).catch(e=>setErr(e.message)).finally(()=>setBusy(false))},[token,role,JSON.stringify(pillars||{})]);return <><div className="roadmap-intro panel"><div className="roadmap-intro-icon"><Rocket size={26}/></div><div className="roadmap-intro-copy"><span className="eyebrow-mini">A PLAN YOU CAN ACT ON</span><h3>90 days. One stronger version of you.</h3><p>Use this roadmap as a guide, then adapt it to your schedule, current skills, and target opportunities.</p></div><label className="role-select"><span>Target role</span><select value={role} onChange={e=>setRole(e.target.value)}>{roles.map(r=><option key={r}>{r}</option>)}</select></label></div>{err&&<div className="alert error">{err}</div>}{!pillars&&<div className="alert info"><CircleHelp size={17}/> Complete a readiness assessment to personalize your roadmap. A general 90-day plan is shown below.</div>}<div className="roadmap-grid">{(data?Object.entries(data[1]):generalPhases(role)).map(([title,phase],i)=><div className="panel phase-card" key={title}><div className="phase-top"><span className={`phase-number phase-${i+1}`}>0{i+1}</span><span className="phase-days">DAYS {i*30+1}–{(i+1)*30}</span></div><h3>{title.replace(/^Phase \d: /,'')}</h3><p className="phase-focus">{phase.focus||`Primary focus for ${role}`}</p><div className="phase-divider"/><h4><Target size={15}/> Milestones</h4><ul>{phase.milestones.map((m,j)=><li key={j}>{m}</li>)}</ul><h4><BookOpen size={15}/> Resources</h4><ul className="resource-list">{phase.resources.map((r,j)=><li key={j}>{r}</li>)}</ul></div>)}</div><div className="bottom-banner"><div className="banner-symbol"><Clock3 size={21}/></div><div><b>Make the plan realistic.</b><p>Even 45–60 focused minutes a day adds up when you stay consistent.</p></div><button onClick={()=>window.print()}>Print roadmap <FileText size={15}/></button></div></>}
function generalPhases(role){return [['Phase 1: Days 1-30 (Foundation & Weak Link Repair)',{focus:'Build a consistent baseline for core technical and communication skills.',milestones:['Set a weekly study schedule and track it honestly.','Review core CS concepts: DBMS, operating systems and networks.','Solve 2 DSA problems a day and revise mistakes.','Take one timed aptitude practice test each week.'],resources:['LeetCode Top Interview 150 / Striver A2Z','GeeksforGeeks Core CS Fundamentals','IndiaBIX aptitude practice']}],['Phase 2: Days 31-60 (Depth, Projects & Mock Tests)',{focus:`Apply your skills to practical work relevant to ${role}.`,milestones:['Polish one project with a clear README and demo.','Practice intermediate DSA patterns and explain your approach aloud.','Complete two peer mock interviews.','Join a coding contest or hackathon.'],resources:['NeetCode pattern-based practice','System Design Primer','Pramp / InterviewBit mock interviews']}],['Phase 3: Days 61-90 (Interview Readiness & Placement Sprints)',{focus:'Practice under realistic interview conditions.',milestones:['Complete timed technical rounds.','Prepare behavioral examples using the STAR method.','Tailor your resume to each relevant job description.','Review weak areas after each mock test.'],resources:['Company interview archives','LeetCode company-tagged problems','Resume bullet-point writing guides']}]]}
function Quiz({token}){const [questions,setQuestions]=useState([]);const [answers,setAnswers]=useState({});const [result,setResult]=useState(null);const [busy,setBusy]=useState(false);const [err,setErr]=useState('');useEffect(()=>{api('/quiz',{token}).then(d=>setQuestions(d.questions)).catch(e=>setErr(e.message))},[token]);async function submit(e){e.preventDefault();setBusy(true);setErr('');try{setResult(await api('/quiz/submit',{token,method:'POST',body:JSON.stringify({answers})}))}catch(e){setErr(e.message)}finally{setBusy(false)}}return <div className="quiz-layout"><form className="panel quiz-form" onSubmit={submit}><div className="panel-head"><div><h3>Technical foundations check</h3><p>Choose the best answer for each question. Review explanations after submitting.</p></div><span className="pill pill-purple">{questions.length} QUESTIONS</span></div>{err&&<div className="alert error">{err}</div>}{questions.map((q,i)=><div className="quiz-question" key={q.id}><div className="question-meta"><span>QUESTION {String(i+1).padStart(2,'0')}</span><span>{q.category}</span></div><h4>{q.question}</h4><div className="quiz-options">{q.options.map((op,j)=><label key={op} className={`quiz-option ${answers[q.id]===op?'chosen':''} ${result&&result.details.find(x=>x.id===q.id)?.answer===op?'correct-option':''}`}><input type="radio" name={`q${q.id}`} checked={answers[q.id]===op} onChange={()=>setAnswers({...answers,[q.id]:op})} disabled={!!result}/><span className="option-letter">{String.fromCharCode(65+j)}</span><span>{op}</span>{result&&result.details.find(x=>x.id===q.id)?.answer===op&&<Check size={15}/>}</label>)}</div>{result&&<div className={`explanation ${result.details.find(x=>x.id===q.id)?.correct?'right':'wrong'}`}><b>{result.details.find(x=>x.id===q.id)?.correct?'Correct':'Review this concept'}</b><p>{result.details.find(x=>x.id===q.id)?.explanation}</p></div>}</div>)}{questions.length>0&&!result&&<button className="primary-btn full" disabled={busy||Object.keys(answers).length!==questions.length}>{busy?'Checking answers…':'Submit quiz'} <ArrowRight size={16}/></button>}{result&&<div className="quiz-result"><div className="quiz-result-ring"><b>{result.percentage}%</b></div><div><span className="eyebrow-mini">YOUR QUIZ RESULT</span><h3>{result.score} of {result.total} correct</h3><p>{result.percentage>=80?'Strong work — keep practicing under timed conditions.':result.percentage>=50?'Good start. Review the explanations and retry the topics you missed.':'Use this as a baseline, then revise the fundamentals and try again.'}</p><button type="button" className="secondary-btn" onClick={()=>{setAnswers({});setResult(null)}}>Try again <ArrowRight size={15}/></button></div></div>}</form><aside className="panel quiz-aside"><div className="quiz-aside-icon"><BookOpen size={24}/></div><span className="eyebrow-mini">PRACTICE WITH PURPOSE</span><h3>It's not just about the score.</h3><p>The most useful part is finding what you don't know yet. Read each explanation and use it to guide your next study session.</p><div className="quiz-progress"><div><span>Answered</span><b>{Object.keys(answers).length}/{questions.length}</b></div><div className="pillar-track"><i style={{width:`${questions.length?Object.keys(answers).length/questions.length*100:0}%`}}/></div></div><div className="quiz-tip"><Sparkles size={16}/><span><b>Tip</b><small>Explain the answer in your own words after selecting it. That helps you retain the concept.</small></span></div></aside></div>}
function HistoryPage({history,select}){return <div className="panel history-panel"><div className="panel-head"><div><h3>Assessment history</h3><p>Your latest 20 saved ML assessments.</p></div><span className="pill pill-purple">{history.length} RECORDS</span></div>{!history.length?<div className="empty-state"><div className="empty-icon"><History size={24}/></div><h4>No assessments yet</h4><p>Your completed assessments will appear here, so you can revisit the results later.</p></div>:<div className="history-table-wrap"><table className="history-table"><thead><tr><th>DATE</th><th>READINESS</th><th>PLACEMENT ESTIMATE</th><th>COMPANY TIER</th><th></th></tr></thead><tbody>{history.map(x=><tr key={x.id}><td><span className="history-date">{x.created_at}</span></td><td><b>{x.result.pillar_scores.Overall_Readiness}/100</b><div className="mini-bar"><i style={{width:`${x.result.pillar_scores.Overall_Readiness}%`}}/></div></td><td>{x.result.placement_probability}%</td><td><span className="tier-pill">{x.result.predicted_tier.split(' (')[0]}</span></td><td><button className="text-btn" onClick={()=>select(x)}>View <ArrowRight size={14}/></button></td></tr>)}</tbody></table></div>}</div>}

createRoot(document.getElementById('root')).render(<App/>);
