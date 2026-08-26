const ROLES = [
  { id: "sde",        title: "Software Engineer",        desc: "DSA, system design, coding rounds", icon: "code" },
  { id: "frontend",   title: "Frontend Developer",       desc: "JS, React, UI/UX fundamentals",     icon: "layout" },
  { id: "data",       title: "Data Scientist",           desc: "Statistics, ML, case studies",      icon: "chart" },
  { id: "mlai",       title: "ML / AI Engineer",         desc: "Model design, MLOps, deep learning",icon: "brain" },
  { id: "devops",     title: "DevOps Engineer",          desc: "CI/CD, cloud, infra automation",    icon: "server" },
  { id: "product",    title: "Product Manager",          desc: "Strategy, metrics, stakeholder mgmt",icon: "target" },
  { id: "business",   title: "Business Analyst",         desc: "Requirements, SQL, dashboards",     icon: "briefcase" },
  { id: "security",   title: "Cybersecurity Analyst",    desc: "Threats, network security, audits", icon: "shield" },
  { id: "qa",         title: "QA / SDET",                desc: "Test design, automation, bugs",     icon: "check" }
];

const COMPANIES = [
  "TCS", "Infosys", "Wipro", "Accenture", "Cognizant",
  "Google", "Microsoft", "Amazon", "Deloitte", "Capgemini"
];

const ICONS = {
  code: '<path d="m8 6-6 6 6 6M16 6l6 6-6 6"/>',
  layout: '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/>',
  chart: '<path d="M3 3v18h18"/><path d="M7 15l3.5-4 3 2.5L18 8"/>',
  brain: '<path d="M12 2a4 4 0 0 0-4 4v1a3 3 0 0 0-2 5 3 3 0 0 0 1 5.6A4 4 0 0 0 11 21a1 1 0 0 0 1-1V6a4 4 0 0 0 0-4Z"/><path d="M12 2a4 4 0 0 1 4 4v1a3 3 0 0 1 2 5 3 3 0 0 1-1 5.6 4 4 0 0 1-4 3.4 1 1 0 0 1-1-1V6a4 4 0 0 1 0-4Z"/>',
  server: '<rect x="2" y="3" width="20" height="7" rx="1.5"/><rect x="2" y="14" width="20" height="7" rx="1.5"/><path d="M6 7h.01M6 18h.01"/>',
  target: '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
  briefcase: '<rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>',
  shield: '<path d="M12 2 4 5v6c0 5 3.5 8.5 8 11 4.5-2.5 8-6 8-11V5l-8-3Z"/>',
  check: '<path d="M20 6 9 17l-5-5"/>',
  upload: '<path d="M12 3v12"/><path d="m7 8 5-5 5 5"/><path d="M5 21h14"/>',
  file: '<path d="M14 3v5h5"/><path d="M6 3h8l5 5v13H6z"/>',
  x: '<path d="M18 6 6 18M6 6l12 12"/>',
  search: '<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/>',
  arrowRight: '<path d="M5 12h14M13 6l6 6-6 6"/>',
  arrowLeft: '<path d="M19 12H5M11 18l-6-6 6-6"/>',
  spark: '<path d="M12 2v4M12 18v4M4.9 4.9l2.8 2.8M16.3 16.3l2.8 2.8M2 12h4M18 12h4M4.9 19.1l2.8-2.8M16.3 7.7l2.8-2.8"/>',
  trend: '<path d="M3 3v18h18"/><path d="M7 15l3.5-4 3 2.5L18 8"/>',
  download: '<path d="M12 3v12"/><path d="m7 10 5 5 5-5"/><path d="M5 21h14"/>'
};
function icon(name, cls){
  return `<svg class="${cls||''}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${ICONS[name]||''}</svg>`;
}

function formatBytes(bytes){
  if(bytes < 1024) return bytes + " B";
  if(bytes < 1024*1024) return (bytes/1024).toFixed(1) + " KB";
  return (bytes/(1024*1024)).toFixed(1) + " MB";
}
function escapeHtml(str){
  return String(str).replace(/[&<>"']/g, m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[m]));
}

// ============================================================
// Page router — runs the right init function based on URL
// ============================================================
document.addEventListener("DOMContentLoaded", ()=>{
  const path = window.location.pathname;
  if(path.includes("role.html")) initRoleScreen();
  else if(path.includes("target.html")) initTargetScreen();
  else if(path.includes("interview.html")) initInterviewScreen();
  else if(path.includes("report.html")) initReportScreen();
  else initResumeScreen();
});

// ============================================================
// PAGE 1: index.html — Resume Upload
// ============================================================
function initResumeScreen(){
  sessionStorage.clear();
  const dz = document.getElementById("dropzone");
  const input = document.getElementById("resumeInput");
  const fileCardWrap = document.getElementById("fileCardWrap");
  const continueBtn = document.getElementById("resumeContinueBtn");
  let selectedFile = null;

  dz.addEventListener("click", ()=> input.click());
  dz.addEventListener("dragover", e=>{ e.preventDefault(); dz.classList.add("drag"); });
  dz.addEventListener("dragleave", ()=> dz.classList.remove("drag"));
  dz.addEventListener("drop", e=>{
    e.preventDefault(); dz.classList.remove("drag");
    if(e.dataTransfer.files.length) handleResumeFile(e.dataTransfer.files[0]);
  });
  input.addEventListener("change", e=>{
    if(e.target.files.length) handleResumeFile(e.target.files[0]);
  });

  function handleResumeFile(file){
    selectedFile = file;
    sessionStorage.setItem("resume_name", file.name);
    sessionStorage.setItem("resume_size", file.size);

    fileCardWrap.innerHTML = `
      <div class="file-card">
        <div class="fico">${icon("file")}</div>
        <div class="file-info">
          <div class="fname">${escapeHtml(file.name)}</div>
          <div class="fmeta">${formatBytes(file.size)} • Ready</div>
        </div>
        <button class="file-remove" id="removeFile">${icon("x")}</button>
      </div>`;

    document.getElementById("removeFile").addEventListener("click", ()=>{
      selectedFile = null;
      sessionStorage.removeItem("resume_name");
      sessionStorage.removeItem("resume_size");
      sessionStorage.removeItem("resume_path");
      fileCardWrap.innerHTML = "";
      continueBtn.disabled = true;
    });
    continueBtn.disabled = false;
  }

  continueBtn.addEventListener("click", async ()=>{
    if(!selectedFile) return;

    // Upload the file to the backend immediately
    continueBtn.disabled = true;
    continueBtn.innerHTML = 'Uploading...' + icon("upload");

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      const res = await fetch("/api/upload-resume", {
        method: "POST",
        body: formData
      });
      const data = await res.json();

      if(data.success){
        sessionStorage.setItem("resume_path", data.filepath);
        sessionStorage.setItem("resume_name", data.filename);
        window.location.href = "role.html";
      } else {
        alert("Upload failed. Please try again.");
        continueBtn.disabled = false;
        continueBtn.innerHTML = 'Continue' + icon("arrowRight");
      }
    } catch(err){
      console.error("Upload error:", err);
      alert("Upload failed. Is the server running?");
      continueBtn.disabled = false;
      continueBtn.innerHTML = 'Continue' + icon("arrowRight");
    }
  });
}

// ============================================================
// PAGE 2: role.html — Role Selection
// ============================================================
function initRoleScreen(){
  const grid = document.getElementById("roleGrid");
  const search = document.getElementById("roleSearch");
  const continueBtn = document.getElementById("roleContinueBtn");
  let selectedRole = sessionStorage.getItem("role") || null;

  function render(filter=""){
    grid.innerHTML = "";
    ROLES.filter(r => r.title.toLowerCase().includes(filter.toLowerCase()))
      .forEach(r=>{
        const card = document.createElement("div");
        card.className = "role-card" + (selectedRole===r.id ? " selected" : "");
        card.innerHTML = `
          <div class="ricon">${icon(r.icon)}</div>
          <div class="rtitle">${r.title}</div>
          <div class="rdesc">${r.desc}</div>`;
        card.addEventListener("click", ()=>{
          selectedRole = r.id;
          sessionStorage.setItem("role", selectedRole);
          continueBtn.disabled = false;
          render(search.value);
        });
        grid.appendChild(card);
      });
  }
  search.addEventListener("input", ()=> render(search.value));
  render();
  if(selectedRole) continueBtn.disabled = false;

  continueBtn.addEventListener("click", ()=>{
    window.location.href = "target.html";
  });
}

// ============================================================
// PAGE 3: target.html — Target Companies & Package
// ============================================================
function initTargetScreen(){
  const chipGroup = document.getElementById("companyChips");
  const addInput = document.getElementById("customCompanyInput");
  const addBtn = document.getElementById("customCompanyBtn");
  const pkgInput = document.getElementById("packageInput");
  const unitButtons = document.querySelectorAll(".pill-select button");
  const continueBtn = document.getElementById("targetContinueBtn");

  let companies = JSON.parse(sessionStorage.getItem("companies") || "[]");
  let pkg = sessionStorage.getItem("package") || "";
  let pkgUnit = sessionStorage.getItem("packageUnit") || "LPA";

  pkgInput.value = pkg;

  function renderChips(){
    chipGroup.innerHTML = "";
    COMPANIES.concat(companies.filter(c=>!COMPANIES.includes(c))).forEach(name=>{
      const chip = document.createElement("div");
      chip.className = "chip" + (companies.includes(name) ? " selected" : "");
      chip.textContent = name;
      chip.addEventListener("click", ()=>{
        if(companies.includes(name)) companies = companies.filter(c=>c!==name);
        else companies.push(name);
        sessionStorage.setItem("companies", JSON.stringify(companies));
        renderChips();
        validate();
      });
      chipGroup.appendChild(chip);
    });
  }
  renderChips();

  addBtn.addEventListener("click", ()=>{
    const val = addInput.value.trim();
    if(val && !companies.includes(val)){
      companies.push(val);
      sessionStorage.setItem("companies", JSON.stringify(companies));
      addInput.value = "";
      renderChips();
      validate();
    }
  });
  addInput.addEventListener("keydown", e=>{ if(e.key==="Enter"){ e.preventDefault(); addBtn.click(); } });

  unitButtons.forEach(b=>{
    if(b.dataset.unit === pkgUnit) b.classList.add("selected");
    else b.classList.remove("selected");
    b.addEventListener("click", ()=>{
      unitButtons.forEach(x=>x.classList.remove("selected"));
      b.classList.add("selected");
      pkgUnit = b.dataset.unit;
      sessionStorage.setItem("packageUnit", pkgUnit);
    });
  });

  pkgInput.addEventListener("input", ()=>{
    pkg = pkgInput.value;
    sessionStorage.setItem("package", pkg);
    validate();
  });

  function validate(){
    continueBtn.disabled = !(companies.length>0 && pkg && Number(pkg)>0);
  }
  validate();

  continueBtn.addEventListener("click", async ()=>{
    continueBtn.disabled = true;
    continueBtn.innerHTML = `${icon("spark")} AI is generating your questions...`;

    try {
      // 1. Create candidate profile
      const candidateData = {
        name: (sessionStorage.getItem("resume_name") || "Candidate").split('.')[0],
        role_id: sessionStorage.getItem("role"),
        target_companies: companies.join(", "),
        expected_package: parseFloat(pkg),
        package_unit: pkgUnit
      };

      const res = await fetch("/api/candidate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(candidateData)
      });
      const cand = await res.json();
      sessionStorage.setItem("candidate_id", cand.id);

      // 2. Generate personalized questions using AI + resume
      const qRes = await fetch("/api/generate-questions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          candidate_id: sessionStorage.getItem("candidate_id"),
          role_id: sessionStorage.getItem("role"),
          resume_path: sessionStorage.getItem("resume_path") || ""
        })
      });
      const qBank = await qRes.json();
      sessionStorage.setItem("QUESTION_BANK", JSON.stringify(qBank));

      window.location.href = "interview.html";
    } catch(err){
      console.error("Error:", err);
      alert("Something went wrong. Please try again.");
      continueBtn.disabled = false;
      continueBtn.innerHTML = 'Start mock interview' + icon("arrowRight");
    }
  });
}

// ============================================================
// PAGE 4: interview.html — Mock Interview
// ============================================================
let interviewState = {
  round: "oa",
  qIndex: { oa:0, technical:0, hr:0 },
  answers: { oa:{}, technical:{}, hr:{} },
  roundComplete: { oa:false, technical:false, hr:false },
  timeLeft: 0,
  timerId: null
};

const ROUND_META = {
  oa:        { title:"Online Assessment", sub:"8 questions • MCQ", icon:"layout", time:60 },
  technical: { title:"Technical Round",   sub:"5 questions • Written", icon:"code", time:180 },
  hr:        { title:"HR Round",          sub:"5 questions • Written", icon:"briefcase", time:120 }
};
const ROUND_ORDER = ["oa","technical","hr"];

function initInterviewScreen(){
  let saved = sessionStorage.getItem("interviewState");
  if(saved) interviewState = JSON.parse(saved);
  renderInterview();
}

function saveInterviewState(){
  sessionStorage.setItem("interviewState", JSON.stringify(interviewState));
}

function renderInterview(){
  renderRoundTabs();
  renderQuestion();
}

function renderRoundTabs(){
  const wrap = document.getElementById("roundTabs");
  wrap.innerHTML = "";
  ROUND_ORDER.forEach((r, idx)=>{
    const unlocked = idx===0 || interviewState.roundComplete[ROUND_ORDER[idx-1]];
    const complete = interviewState.roundComplete[r];
    const meta = ROUND_META[r];
    const div = document.createElement("div");
    div.className = "round-tab" + (unlocked?" unlocked":"") + (r===interviewState.round?" current":"") + (complete?" complete":"");
    div.innerHTML = `
      <div class="rt-ico">${complete?icon("check"):icon(meta.icon)}</div>
      <div class="rt-text">
        <div class="rt-title">${meta.title}</div>
        <div class="rt-sub">${meta.sub}</div>
      </div>`;
    if(unlocked){
      div.addEventListener("click", ()=>{
        interviewState.round = r;
        clearTimer();
        saveInterviewState();
        renderInterview();
      });
    }
    wrap.appendChild(div);
  });
}

function renderQuestion(){
  clearTimer();
  const qBank = JSON.parse(sessionStorage.getItem("QUESTION_BANK") || "{}");
  const questions = qBank[interviewState.round] || [];
  const idx = interviewState.qIndex[interviewState.round];

  if(questions.length === 0){
    document.getElementById("questionBody").innerHTML = "<p style='color:var(--text-tertiary)'>No questions loaded. Please go back and try again.</p>";
    return;
  }

  const q = questions[idx];
  const body = document.getElementById("questionBody");
  const meta = ROUND_META[interviewState.round];

  document.getElementById("qProgressText").textContent = `Question ${idx+1} of ${questions.length}`;
  document.getElementById("qProgressBar").style.width = `${(idx/questions.length)*100}%`;

  let inner = `<div class="q-tagrow"><span class="q-tag">${escapeHtml(q.tag)}</span><span class="q-tag">${meta.title}</span></div>
    <div class="q-text">${escapeHtml(q.text)}</div>`;

  if(q.type==="mcq"){
    inner += `<div class="mcq-list">` + q.options.map((opt,i)=>{
      const selected = interviewState.answers[interviewState.round][q.id]===i;
      return `<div class="mcq-opt${selected?" selected":""}" data-i="${i}">
        <div class="mcq-letter">${String.fromCharCode(65+i)}</div>
        <div>${escapeHtml(opt)}</div>
      </div>`;
    }).join("") + `</div>`;
  } else {
    const val = interviewState.answers[interviewState.round][q.id] || "";
    inner += `<textarea class="answer-box" id="answerBox" placeholder="Type your answer as if you were speaking it out loud to the interviewer...">${escapeHtml(val)}</textarea>
      <div class="answer-meta"><span id="wordCount">0 words</span><span>Tip: use the STAR method for behavioral answers</span></div>`;
  }
  body.innerHTML = inner;

  if(q.type==="mcq"){
    body.querySelectorAll(".mcq-opt").forEach(el=>{
      el.addEventListener("click", ()=>{
        interviewState.answers[interviewState.round][q.id] = Number(el.dataset.i);
        saveInterviewState();
        renderQuestion();
      });
    });
  } else {
    const box = document.getElementById("answerBox");
    const wc = document.getElementById("wordCount");
    function updateWc(){
      const words = box.value.trim().split(/\s+/).filter(Boolean).length;
      wc.textContent = words + " words";
    }
    updateWc();
    box.addEventListener("input", ()=>{
      interviewState.answers[interviewState.round][q.id] = box.value;
      saveInterviewState();
      updateWc();
    });
  }

  const nextBtn = document.getElementById("nextQBtn");
  nextBtn.textContent = idx===questions.length-1 ? "Finish round" : "Submit & Next";
  const prevBtn = document.getElementById("prevQBtn");
  prevBtn.disabled = idx===0;

  nextBtn.onclick = ()=> advanceQuestion();
  prevBtn.onclick = ()=>{
    if(idx>0){
      interviewState.qIndex[interviewState.round]--;
      saveInterviewState();
      renderQuestion();
    }
  };

  startTimer(meta.time);
}

function advanceQuestion(){
  const qBank = JSON.parse(sessionStorage.getItem("QUESTION_BANK") || "{}");
  const questions = qBank[interviewState.round] || [];
  const idx = interviewState.qIndex[interviewState.round];

  if(idx < questions.length-1){
    interviewState.qIndex[interviewState.round]++;
    saveInterviewState();
    renderQuestion();
  } else {
    interviewState.roundComplete[interviewState.round] = true;
    const nextIdx = ROUND_ORDER.indexOf(interviewState.round)+1;
    if(nextIdx < ROUND_ORDER.length){
      interviewState.round = ROUND_ORDER[nextIdx];
      saveInterviewState();
      renderInterview();
    } else {
      clearTimer();
      saveInterviewState();
      window.location.href = "report.html";
    }
  }
}

function startTimer(seconds){
  interviewState.timeLeft = seconds;
  updateTimerUI();
  interviewState.timerId = setInterval(()=>{
    interviewState.timeLeft--;
    updateTimerUI();
    if(interviewState.timeLeft<=0){ clearTimer(); advanceQuestion(); }
  }, 1000);
}
function clearTimer(){ if(interviewState.timerId){ clearInterval(interviewState.timerId); interviewState.timerId=null; } }
function updateTimerUI(){
  const el = document.getElementById("timerDisplay");
  if(!el) return;
  const m = Math.floor(interviewState.timeLeft/60), s = interviewState.timeLeft%60;
  el.parentElement.classList.toggle("low", interviewState.timeLeft<=10);
  el.textContent = `${m}:${s.toString().padStart(2,"0")}`;
}

// ============================================================
// PAGE 5: report.html — Analysis & Report
// ============================================================
const ANALYZE_STEPS = [
  "Reviewing OA answers",
  "Evaluating technical responses",
  "Assessing communication & tone",
  "Compiling your report"
];

function initReportScreen(){
  runAnalysis();
}

function runAnalysis(){
  const stepsWrap = document.getElementById("analyzingSteps");
  const analyzingBlock = document.getElementById("analyzingBlock");
  const reportBlock = document.getElementById("reportBlock");

  stepsWrap.innerHTML = ANALYZE_STEPS.map((s,i)=>
    `<div class="astep" id="astep-${i}">${icon("clock")}<span>${s}</span></div>`
  ).join("");

  // Start the analyzing animation, then call the API
  submitAndComputeScores().then(report => {
    // Complete all animation steps
    ANALYZE_STEPS.forEach((s, idx) => {
      const el = document.getElementById("astep-"+idx);
      el.classList.add("done");
      el.innerHTML = icon("check") + `<span>${s}</span>`;
    });
    setTimeout(()=>{
      analyzingBlock.classList.add("hidden");
      reportBlock.classList.remove("hidden");
      renderReport(report);
    }, 400);
  }).catch(err => {
    console.error("Analysis error:", err);
    // Show error state
    stepsWrap.innerHTML = `<div class="astep" style="color:var(--coral)">${icon("x")}<span>Analysis failed. Please try again.</span></div>`;
  });

  // Animate steps in parallel
  let i = 0;
  function animateStep(){
    if(i < ANALYZE_STEPS.length){
      const el = document.getElementById("astep-"+i);
      if(el && !el.classList.contains("done")){
        el.style.color = "var(--amber)";
      }
      i++;
      setTimeout(animateStep, 800);
    }
  }
  animateStep();
}

async function submitAndComputeScores(){
  const saved = JSON.parse(sessionStorage.getItem("interviewState") || "{}");
  const payload = {
    candidate_id: parseInt(sessionStorage.getItem("candidate_id") || "0"),
    round: "all",
    answers: saved.answers || {}
  };

  const res = await fetch("/api/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  return await res.json();
}

function renderReport(r){
  const candidateName = (sessionStorage.getItem("resume_name") || "Candidate").replace(/\.(pdf|docx?|txt)$/i,"");
  const roleId = sessionStorage.getItem("role");
  const roleTitle = (ROLES.find(x=>x.id===roleId)||{}).title || "—";
  const pkg = sessionStorage.getItem("package");
  const pkgUnit = sessionStorage.getItem("packageUnit");
  const companies = JSON.parse(sessionStorage.getItem("companies") || "[]");

  document.getElementById("reportCandidate").textContent = candidateName;
  document.getElementById("reportRole").textContent = `Target role: ${roleTitle} • Package goal: ${pkg||"—"} ${pkgUnit}`;

  const tagWrap = document.getElementById("reportTags");
  tagWrap.innerHTML = companies.map(c=>`<span class="chip selected">${escapeHtml(c)}</span>`).join("");

  const circumference = 2*Math.PI*68;
  const offset = circumference - (r.overall/100)*circumference;
  document.getElementById("rgFill").style.strokeDasharray = circumference;
  document.getElementById("rgFill").style.strokeDashoffset = circumference;
  requestAnimationFrame(()=>{
    document.getElementById("rgFill").style.strokeDashoffset = offset;
  });
  document.getElementById("rgNum").textContent = r.overall;

  document.getElementById("roundScores").innerHTML = `
    ${roundScoreCard("Online Assessment", r.oa+"%", r.oa, "var(--amber)")}
    ${roundScoreCard("Technical Round", r.technical+"/10", r.technical*10, "var(--mint)")}
    ${roundScoreCard("HR Round", r.hr+"/10", r.hr*10, "var(--lavender)")}
  `;

  document.getElementById("strengthsList").innerHTML = r.strengths.map(s=>
    `<div class="insight-item good">${icon("check")}<span>${escapeHtml(s)}</span></div>`).join("");
  document.getElementById("improvementsList").innerHTML = r.improvements.map(s=>
    `<div class="insight-item improve">${icon("spark")}<span>${escapeHtml(s)}</span></div>`).join("");
}

function roundScoreCard(title, display, pct, color){
  return `<div class="rscore-card">
    <div class="rtitle">${title}</div>
    <div class="rval">${display}</div>
    <div class="rscore-bar"><i style="width:${pct}%;background:${color};"></i></div>
  </div>`;
}
