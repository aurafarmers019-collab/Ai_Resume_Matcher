// =============================================================================
//  app.js — AI Bulk Resume Matcher v3.0
// =============================================================================

const API = 'http://localhost:8000';

let dialChartInst  = null;
let radarChartInst = null;
let currentJDText  = '';
let activeJDTab    = '';

// ── Init ──────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  loadJDOptions();
  setupFileUpload();
  setupDragDrop();
  setupFolderCheck();
});

// ── Tab Switching ─────────────────────────────────────────────────────────────
function switchTab(tabName) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelector(`.tab[data-tab="${tabName}"]`).classList.add('active');
  document.getElementById(`page-${tabName}`).classList.add('active');
}

// ── Load JD Options from backend ─────────────────────────────────────────────
async function loadJDOptions() {
  try {
    const res  = await fetch(`${API}/jd-options`);
    const data = await res.json();
    renderJDTabs(data.options, 'single');
    renderJDTabs(data.options, 'bulk');
  } catch (e) {
    console.warn('Could not load JD options from backend:', e.message);
  }
}

function renderJDTabs(options, mode) {
  const container = document.getElementById(`jdTabs-${mode}`);
  if (!container) return;
  container.innerHTML = '';

  options.forEach(opt => {
    const btn = document.createElement('button');
    btn.className   = 'jd-tab';
    btn.textContent = opt;
    btn.onclick     = () => selectJD(opt, mode);
    container.appendChild(btn);
  });

  // Manual option
  const manual = document.createElement('button');
  manual.className   = 'jd-tab manual-tab';
  manual.textContent = '✏️ Manual Input';
  manual.onclick     = () => selectJD('manual', mode);
  container.appendChild(manual);

  // Auto-select first
  selectJD(options[0], mode);
}

async function selectJD(name, mode) {
  // Update tab highlight
  const container = document.getElementById(`jdTabs-${mode}`);
  container.querySelectorAll('.jd-tab').forEach(t => t.classList.remove('active'));
  const clicked = [...container.querySelectorAll('.jd-tab')].find(t => t.textContent.replace('✏️ ','') === name || (name === 'manual' && t.textContent.includes('Manual')));
  if (clicked) clicked.classList.add('active');

  const textarea = document.getElementById(`jobDesc-${mode}`);

  if (name === 'manual') {
    textarea.readOnly    = false;
    textarea.placeholder = 'Type or paste your custom job description here...';
    textarea.value       = '';
    textarea.focus();
    currentJDText = '';
  } else {
    textarea.readOnly = true;
    try {
      const res  = await fetch(`${API}/jd-text/${encodeURIComponent(name)}`);
      const data = await res.json();
      textarea.value = data.text;
      currentJDText  = data.text;
    } catch (e) {
      textarea.value = '';
    }
  }
  activeJDTab = name;
}

function getJDText(mode) {
  return document.getElementById(`jobDesc-${mode}`).value.trim();
}

// ── Single Resume Upload ───────────────────────────────────────────────────────
function setupFileUpload() {
  document.getElementById('resumeFile').addEventListener('change', (e) => {
    const f = e.target.files[0];
    if (f) document.getElementById('fileLabel').innerHTML =
      `<span class="upload-filename">✅ ${f.name}</span>`;
  });
}

function setupDragDrop() {
  const zone = document.getElementById('dropZone');
  if (!zone) return;
  zone.addEventListener('dragover',  e => { e.preventDefault(); zone.classList.add('drag'); });
  zone.addEventListener('dragleave', ()  => zone.classList.remove('drag'));
  zone.addEventListener('drop', e => {
    e.preventDefault(); zone.classList.remove('drag');
    const f = e.dataTransfer.files[0];
    if (f && f.name.toLowerCase().endsWith('.pdf')) {
      const dt = new DataTransfer(); dt.items.add(f);
      document.getElementById('resumeFile').files = dt.files;
      document.getElementById('fileLabel').innerHTML =
        `<span class="upload-filename">✅ ${f.name}</span>`;
    } else {
      showError('Please drop a valid PDF file.', 'single');
    }
  });
}

// ── Folder Check ──────────────────────────────────────────────────────────────
function setupFolderCheck() {
  const input = document.getElementById('folderPath');
  if (input) {
    input.addEventListener('keydown', e => { if (e.key === 'Enter') checkFolder(); });
  }
}

async function checkFolder() {
  const folder  = document.getElementById('folderPath').value.trim();
  const infoBox = document.getElementById('folderInfo');
  if (!folder) return;

  try {
    const res  = await fetch(`${API}/list-resumes?folder=${encodeURIComponent(folder)}`);
    const data = await res.json();
    infoBox.textContent = `✅ Found ${data.count} PDF resume(s) in folder`;
    infoBox.classList.add('show');
  } catch (e) {
    infoBox.textContent = `❌ Could not read folder. Check the path.`;
    infoBox.style.background = 'rgba(255,101,132,.08)';
    infoBox.style.borderColor = 'rgba(255,101,132,.3)';
    infoBox.style.color = 'var(--red)';
    infoBox.classList.add('show');
  }
}

// ── Error Helpers ─────────────────────────────────────────────────────────────
function showError(msg, mode) {
  const id = mode === 'bulk' ? 'errorBox-bulk' : 'errorBox-single';
  const b  = document.getElementById(id);
  if (b) { b.textContent = msg; b.classList.add('show'); }
}
function clearError(mode) {
  const id = mode === 'bulk' ? 'errorBox-bulk' : 'errorBox-single';
  const b  = document.getElementById(id);
  if (b) b.classList.remove('show');
}

// ── Score Helpers ─────────────────────────────────────────────────────────────
function scoreColor(s) {
  return s >= 0.72 ? '#00d4a1' : s >= 0.50 ? '#ffd166' : '#ff6584';
}
function scoreLabel(s) {
  if (s >= 0.80) return '🎯 Excellent Match';
  if (s >= 0.65) return '✅ Good Match';
  if (s >= 0.50) return '⚠️ Moderate Match';
  if (s >= 0.35) return '🔶 Weak Match';
  return '❌ Poor Match';
}

// =============================================================================
//  SINGLE RESUME MATCH
// =============================================================================
async function runMatch() {
  const fileInput = document.getElementById('resumeFile');
  const jd        = getJDText('single');
  clearError('single');

  if (!fileInput.files[0]) return showError('Please upload a resume PDF first.', 'single');
  if (jd.length < 50)      return showError('Job description is too short.', 'single');

  document.getElementById('matchBtn').disabled = true;
  document.getElementById('loading-single').classList.add('show');
  document.getElementById('results').classList.remove('show');

  const fd = new FormData();
  fd.append('resume', fileInput.files[0]);
  fd.append('job_description', jd);

  try {
    const res = await fetch(`${API}/match`, { method:'POST', body:fd });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail:'Server error' }));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    const data = await res.json();
    renderSingleResults(data);
  } catch (e) {
    const msg = e.message.includes('fetch')
      ? 'Cannot connect to backend. Is the server running on port 8000?'
      : e.message;
    showError(msg, 'single');
  } finally {
    document.getElementById('loading-single').classList.remove('show');
    document.getElementById('matchBtn').disabled = false;
  }
}

function renderSingleResults(data) {
  document.getElementById('results').classList.add('show');
  renderScoreHero(data.final_score, data.recommendation);
  renderBreakdown(data.score_breakdown);
  renderRadar(data.score_breakdown);
  renderRoles(data.role_analysis);
  renderSkills(data.skills);
  renderAttributions(data.skills.attributions);
  if (data.stats) {
    document.getElementById('statsRow').innerHTML = `
      <div class="stat-pill">Resume Words <span>${data.stats.resume_word_count}</span></div>
      <div class="stat-pill">JD Words <span>${data.stats.jd_word_count || '—'}</span></div>
      <div class="stat-pill">Skills in Resume <span>${data.stats.resume_skills_found}</span></div>
      <div class="stat-pill">Skills Required <span>${data.stats.jd_skills_required}</span></div>`;
  }
}

// ── Score Hero ────────────────────────────────────────────────────────────────
function renderScoreHero(score, rec) {
  const pct   = Math.round(score * 100);
  const color = scoreColor(score);
  document.getElementById('scoreNum').textContent  = `${pct}%`;
  document.getElementById('scoreNum').style.color  = color;
  document.getElementById('scoreTitle').textContent = scoreLabel(score);
  document.getElementById('recommendation').textContent = rec;

  if (dialChartInst) dialChartInst.destroy();
  dialChartInst = new Chart(document.getElementById('dialChart'), {
    type: 'doughnut',
    data: { datasets: [{ data:[pct,100-pct], backgroundColor:[color,'#2a2f4a'], borderWidth:0, circumference:270, rotation:225 }] },
    options: { responsive:false, plugins:{ legend:{display:false}, tooltip:{enabled:false} }, cutout:'76%', animation:{ duration:1300 } }
  });
}

// ── Breakdown Bars ────────────────────────────────────────────────────────────
function renderBreakdown(bd) {
  const metrics = [
    { key:'semantic_similarity', label:'Semantic Similarity', weight:'45%' },
    { key:'skill_overlap',       label:'Skill Overlap',       weight:'35%' },
    { key:'experience_match',    label:'Experience Match',    weight:'10%' },
    { key:'role_alignment',      label:'Role Alignment',      weight:'10%' },
  ];
  const grid = document.getElementById('breakdownGrid');
  grid.innerHTML = '';
  metrics.forEach(m => {
    const val = bd[m.key], pct = Math.round(val*100), color = scoreColor(val);
    const div = document.createElement('div');
    div.className = 'breakdown-item';
    div.innerHTML = `
      <div class="bd-header"><span class="bd-label">${m.label}</span><span class="bd-value" style="color:${color}">${pct}%</span></div>
      <div class="bd-weight">Weight: ${m.weight}</div>
      <div class="bar-track"><div class="bar-fill" id="bar-${m.key}" style="background:${color}"></div></div>`;
    grid.appendChild(div);
    requestAnimationFrame(() => setTimeout(() => {
      const el = document.getElementById(`bar-${m.key}`);
      if (el) el.style.width = `${pct}%`;
    }, 60));
  });
}

// ── Radar ─────────────────────────────────────────────────────────────────────
function renderRadar(bd) {
  if (radarChartInst) radarChartInst.destroy();
  radarChartInst = new Chart(document.getElementById('radarChart'), {
    type: 'radar',
    data: {
      labels: ['Semantic\nSimilarity','Skill\nCoverage','Experience\nFit','Role\nAlignment'],
      datasets: [{
        label:'Your Match',
        data:[Math.round(bd.semantic_similarity*100),Math.round(bd.skill_overlap*100),Math.round(bd.experience_match*100),Math.round(bd.role_alignment*100)],
        backgroundColor:'rgba(108,99,255,.15)', borderColor:'#6c63ff', borderWidth:2,
        pointBackgroundColor:'#6c63ff', pointRadius:4,
      }]
    },
    options: {
      responsive:true,
      scales:{ r:{ min:0, max:100, grid:{color:'#2a2f4a'}, angleLines:{color:'#2a2f4a'},
        ticks:{color:'#8892b0',backdropColor:'transparent',font:{size:10},stepSize:25},
        pointLabels:{color:'#e2e8f0',font:{size:10,weight:'600'}}
      }},
      plugins:{ legend:{display:false}, tooltip:{callbacks:{label:c=>` ${c.raw}%`}} },
      animation:{duration:1000}
    }
  });
}

// ── Roles ─────────────────────────────────────────────────────────────────────
function renderRoles(ra) {
  const container = document.getElementById('roleRow');
  container.innerHTML = '';
  [
    { tag:'👤 Your Resume Profile',   roles:ra.resume_roles, top:ra.resume_top_role },
    { tag:'💼 Job Description Needs', roles:ra.jd_roles,     top:ra.jd_top_role    },
  ].forEach(side => {
    const maxScore = Math.max(...side.roles.map(r=>r.score));
    const bars = side.roles.map(r => {
      const isTop = r.role === side.top.role;
      const w = Math.round((r.score/maxScore)*100);
      return `<div class="role-bar-item">
        <div class="role-bar-meta"><span style="color:${isTop?'var(--text)':'var(--muted)'}">${r.role}</span><span>${Math.round(r.score*100)}%</span></div>
        <div class="bar-track"><div class="bar-fill" style="width:${w}%;background:${isTop?'var(--accent)':'var(--border)'}"></div></div>
      </div>`;
    }).join('');
    container.innerHTML += `<div class="role-card">
      <div class="role-tag">${side.tag}</div>
      <div class="role-name">${side.top.role}</div>
      <div class="role-bar-row">${bars}</div>
    </div>`;
  });
}

// ── Skills ────────────────────────────────────────────────────────────────────
function renderSkills(skills) {
  document.getElementById('matchedCount').textContent = skills.matched.length;
  const mc = document.getElementById('matchedChips');
  mc.innerHTML = skills.matched.length === 0
    ? '<span class="empty-note">No matching skills found</span>'
    : skills.matched.map(s => {
        const tip = skills.attributions[s] ? `title="${skills.attributions[s]}"` : '';
        return `<span class="chip green" ${tip}>✓ ${s}</span>`;
      }).join('');

  document.getElementById('missingCount').textContent = skills.missing_ranked.length;
  const msc = document.getElementById('missingChips');
  msc.innerHTML = skills.missing_ranked.length === 0
    ? '<span class="empty-note" style="color:var(--green)">🎉 No missing skills!</span>'
    : skills.missing_ranked.map(s => {
        const cls  = s.priority==='critical'?'red':s.priority==='recommended'?'yellow':'gray';
        const icon = s.priority==='critical'?'⚠':s.priority==='recommended'?'!':'○';
        return `<span class="chip ${cls}" title="Relevance:${Math.round(s.relevance*100)}% | ${s.priority}">${icon} ${s.skill}</span>`;
      }).join('');
}

// ── Attributions ──────────────────────────────────────────────────────────────
function renderAttributions(attrs) {
  const list = document.getElementById('attributionList');
  const entries = Object.entries(attrs);
  list.innerHTML = !entries.length
    ? '<p class="empty-note">No sentence-level evidence available.</p>'
    : entries.map(([skill,sentence]) => `
        <div class="attribution-item">
          <div class="attr-skill">🔍 ${skill}</div>
          <div class="attr-evidence">"${sentence}"</div>
        </div>`).join('');
}

// =============================================================================
//  BULK RESUME MATCH
// =============================================================================
async function runBulkMatch() {
  const folder = document.getElementById('folderPath').value.trim();
  const jd     = getJDText('bulk');
  clearError('bulk');

  if (!folder)          return showError('Please enter a folder path.', 'bulk');
  if (jd.length < 50)  return showError('Job description is too short.', 'bulk');

  document.getElementById('bulkMatchBtn').disabled = true;
  document.getElementById('loading-bulk').classList.add('show');
  document.getElementById('bulk-results').classList.remove('show');

  // Animate progress bar
  let progress = 0;
  const progressEl = document.getElementById('bulkProgress');
  const progressTimer = setInterval(() => {
    progress = Math.min(progress + Math.random() * 8, 90);
    if (progressEl) progressEl.style.width = `${progress}%`;
  }, 400);

  try {
    const res = await fetch(`${API}/bulk-match`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ folder, jd_text: jd, top_n: 50 })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail:'Server error' }));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    const data = await res.json();
    if (progressEl) progressEl.style.width = '100%';
    setTimeout(() => renderBulkResults(data), 300);
  } catch (e) {
    const msg = e.message.includes('fetch')
      ? 'Cannot connect to backend. Is the server running on port 8000?'
      : e.message;
    showError(msg, 'bulk');
  } finally {
    clearInterval(progressTimer);
    document.getElementById('loading-bulk').classList.remove('show');
    document.getElementById('bulkMatchBtn').disabled = false;
  }
}

function renderBulkResults(data) {
  document.getElementById('bulk-results').classList.add('show');

  // Summary cards
  const excellent = data.results.filter(r => r.final_score >= 0.7).length;
  const moderate  = data.results.filter(r => r.final_score >= 0.4 && r.final_score < 0.7).length;
  const weak      = data.results.filter(r => r.final_score < 0.4).length;
  const topScore  = data.results[0]?.final_score || 0;

  document.getElementById('bulkSummary').innerHTML = `
    <div class="summary-card">
      <div class="s-num" style="color:var(--text)">${data.total_scanned}</div>
      <div class="s-label">Resumes Scanned</div>
    </div>
    <div class="summary-card">
      <div class="s-num" style="color:var(--green)">${excellent}</div>
      <div class="s-label">Strong Matches (70%+)</div>
    </div>
    <div class="summary-card">
      <div class="s-num" style="color:var(--yellow)">${moderate}</div>
      <div class="s-label">Moderate Matches</div>
    </div>
    <div class="summary-card">
      <div class="s-num" style="color:var(--accent)">${Math.round(topScore*100)}%</div>
      <div class="s-label">Top Score</div>
    </div>`;

  // Leaderboard
  const board = document.getElementById('leaderboard');
  board.innerHTML = '';

  data.results.forEach((r, i) => {
    const rank     = i + 1;
    const pct      = Math.round(r.final_score * 100);
    const color    = scoreColor(r.final_score);
    const rankCls  = rank===1?'rank-1':rank===2?'rank-2':rank===3?'rank-3':'rank-n';
    const matched  = r.skills.matched.slice(0, 5).join(', ') || 'None';
    const critical = r.skills.missing_ranked.filter(s=>s.priority==='critical').slice(0,3).map(s=>s.skill).join(', ') || 'None';

    // Card
    const card = document.createElement('div');
    card.className = 'resume-card';
    card.id        = `card-${i}`;
    card.innerHTML = `
      <div class="rank-badge ${rankCls}">${rank <= 3 ? ['🥇','🥈','🥉'][rank-1] : rank}</div>
      <div class="resume-info">
        <div class="r-name">${r.filename}</div>
        <div class="r-role">${r.role_analysis.resume_top_role.role}</div>
        <div class="r-skills">✅ ${r.skills.matched.length} matched &nbsp;|&nbsp; ❌ ${r.skills.missing_ranked.length} missing</div>
      </div>
      <div class="score-pill">
        <div class="sp-num" style="color:${color}">${pct}%</div>
        <div class="sp-label">Match</div>
      </div>`;
    card.onclick = () => toggleDetail(i);

    // Detail panel
    const detail = document.createElement('div');
    detail.className = 'resume-detail';
    detail.id        = `detail-${i}`;
    detail.innerHTML = `
      <div class="detail-grid">
        <div>
          <div class="section-title" style="margin-bottom:10px">📊 Score Breakdown</div>
          <div class="mini-breakdown">
            ${[
              ['Semantic Similarity', r.score_breakdown.semantic_similarity],
              ['Skill Overlap',       r.score_breakdown.skill_overlap],
              ['Experience Match',    r.score_breakdown.experience_match],
              ['Role Alignment',      r.score_breakdown.role_alignment],
            ].map(([lbl,val]) => `
              <div class="mini-bd-item">
                <div class="mini-bd-label">${lbl} <span>${Math.round(val*100)}%</span></div>
                <div class="bar-track"><div class="bar-fill" style="width:${Math.round(val*100)}%;background:${scoreColor(val)}"></div></div>
              </div>`).join('')}
          </div>
        </div>
        <div>
          <div class="section-title" style="margin-bottom:8px">✅ Matched Skills</div>
          <div class="mini-chips">
            ${r.skills.matched.slice(0,10).map(s=>`<span class="mini-chip green">✓ ${s}</span>`).join('')}
            ${r.skills.matched.length === 0 ? '<span style="font-size:.78rem;color:var(--muted)">None detected</span>' : ''}
          </div>
          <div class="section-title" style="margin-bottom:8px;margin-top:12px">❌ Missing Skills</div>
          <div class="mini-chips">
            ${r.skills.missing_ranked.slice(0,8).map(s=>{
              const cls = s.priority==='critical'?'red':s.priority==='recommended'?'yellow':'';
              return cls ? `<span class="mini-chip ${cls}">${s.skill}</span>` : '';
            }).join('')}
            ${r.skills.missing_ranked.length === 0 ? '<span style="font-size:.78rem;color:var(--green)">None missing!</span>' : ''}
          </div>
        </div>
      </div>
      <div class="detail-rec">💡 ${r.recommendation}</div>`;

    board.appendChild(card);
    board.appendChild(detail);
  });

  if (data.results.length === 0) {
    board.innerHTML = '<p style="color:var(--muted);padding:20px;text-align:center">No results to show.</p>';
  }
}

function toggleDetail(i) {
  const card   = document.getElementById(`card-${i}`);
  const detail = document.getElementById(`detail-${i}`);
  const isOpen = detail.classList.contains('open');

  // Close all
  document.querySelectorAll('.resume-detail').forEach(d => d.classList.remove('open'));
  document.querySelectorAll('.resume-card').forEach(c => c.classList.remove('expanded'));

  if (!isOpen) {
    detail.classList.add('open');
    card.classList.add('expanded');
    card.scrollIntoView({ behavior:'smooth', block:'nearest' });
  }
}