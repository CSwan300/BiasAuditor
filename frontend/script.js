const API_BASE = 'http://localhost:8000';

const dropZone    = document.getElementById('drop-zone');
const fileInput   = document.getElementById('file-input');
const browseLink  = document.getElementById('browse-link');
const fileBar     = document.getElementById('file-bar');
const fileNameLbl = document.getElementById('file-name-label');
const fileSizeLbl = document.getElementById('file-size-label');
const auditBtn    = document.getElementById('audit-btn');
const loading     = document.getElementById('loading');
const results     = document.getElementById('results');
const errorBox    = document.getElementById('error-box');
const resetBtn    = document.getElementById('reset-btn');

let selectedFile = null;

// ── Drag & Drop Logic
dropZone.addEventListener('dragover', e => {
  e.preventDefault();
  dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));

dropZone.addEventListener('drop', e => {
  e.preventDefault();
  dropZone.classList.remove('drag-over');
  const f = e.dataTransfer.files[0];
  if (f) handleFile(f);
});

dropZone.addEventListener('click', () => fileInput.click());
browseLink.addEventListener('click', e => {
  e.stopPropagation();
  fileInput.click();
});

fileInput.addEventListener('change', () => {
  if (fileInput.files[0]) handleFile(fileInput.files[0]);
});

function handleFile(file) {
  const allowed = ['.csv', '.xlsx', '.xls'];
  const ext = '.' + file.name.split('.').pop().toLowerCase();

  if (!allowed.includes(ext)) {
    showError('Unsupported file type. Please upload a CSV or Excel file.');
    return;
  }

  selectedFile = file;
  fileNameLbl.textContent = file.name;
  fileSizeLbl.textContent = formatBytes(file.size);
  fileBar.classList.add('visible');
  auditBtn.classList.add('visible');
  hideError();
}

// ── Audit Execution
auditBtn.addEventListener('click', runAudit);

async function runAudit() {
  if (!selectedFile) return;

  auditBtn.disabled = true;
  loading.classList.add('visible');
  results.classList.remove('visible');
  hideError();

  const form = new FormData();
  form.append('file', selectedFile);

  try {
    const res = await fetch(`${API_BASE}/audit`, { method: 'POST', body: form });
    const data = await res.json();

    if (!res.ok) {
      showError(data.detail || 'Audit failed. Please check your file format.');
      return;
    }

    renderResults(data);
  } catch (err) {
    showError('Could not reach the API server. Make sure the backend is running on localhost:8000.');
  } finally {
    loading.classList.remove('visible');
    auditBtn.disabled = false;
  }
}

// ── UI Rendering Functions
function renderResults(data) {
  renderRiskBanner(data.overall_risk, data.metadata);
  renderWarnings(data.warnings);
  renderMetadata(data.metadata);
  renderCharCards(data.audits);
  results.classList.add('visible');
  results.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function renderRiskBanner(risk, meta) {
  const banner = document.getElementById('risk-banner');
  const ring   = document.getElementById('risk-ring');
  const title  = document.getElementById('risk-title');
  const desc   = document.getElementById('risk-desc');
  const metaEl = document.getElementById('risk-meta');

  const level = (risk.level || 'Unknown').toLowerCase();
  const levelMap = {
    low:      { label: 'Low Risk',      desc: 'No protected characteristics show significant disparity.' },
    moderate: { label: 'Moderate Risk', desc: 'One or more characteristics show minor disparity worth monitoring.' },
    high:     { label: 'High Risk',     desc: 'Multiple characteristics show potential adverse impact. Review required.' },
    critical: { label: 'Critical Risk', desc: 'Severe disparity detected across characteristics. Immediate action needed.' },
    unknown:  { label: 'Incomplete Data', desc: 'Could not evaluate bias — check warnings below.' },
  };
  const info = levelMap[level] || levelMap.unknown;

  banner.className = `risk-banner ${level}`;
  ring.className = `risk-score-ring ${level}`;
  ring.textContent = risk.score != null ? risk.score + '%' : '?';
  title.textContent = info.label;
  desc.textContent  = info.desc;

  if (risk.flagged_characteristics && risk.flagged_characteristics.length > 0) {
    desc.textContent += ` Flagged: ${risk.flagged_characteristics.join(', ')}.`;
  }

  metaEl.innerHTML = `
    <div class="meta-item">Total Rows <span class="meta-value">${meta.total_rows.toLocaleString()}</span></div>
    <div class="meta-item">Columns <span class="meta-value">${meta.total_columns}</span></div>
    <div class="meta-item">Characteristics <span class="meta-value">${meta.protected_characteristics_found.length}</span></div>
    <div class="meta-item">Prediction Col <span class="meta-value">${meta.prediction_column || 'None'}</span></div>
  `;
}

function renderWarnings(warnings) {
  const container = document.getElementById('warnings-container');
  container.innerHTML = '';
  (warnings || []).forEach(w => {
    const box = document.createElement('div');
    box.className = 'warning-box';
    box.innerHTML = `<p>${w}</p>`;
    container.appendChild(box);
  });
}

function renderMetadata(meta) {
  const table = document.getElementById('meta-table');
  const rows = [
    ['Total Rows',             meta.total_rows.toLocaleString()],
    ['Total Columns',          meta.total_columns],
    ['Prediction Column',      meta.prediction_column || '—'],
    ['Protected Cols Found',   meta.protected_characteristics_found.join(', ') || '—'],
    ['All Columns',            meta.columns_detected.join(', ')],
  ];
  table.innerHTML = rows.map(([k, v]) =>
    `<tr><td>${k}</td><td>${v}</td></tr>`
  ).join('');
}

function renderCharCards(audits) {
  const grid = document.getElementById('char-grid');
  grid.innerHTML = '';

  if (!audits || audits.length === 0) {
    grid.innerHTML = '<p style="color:var(--text-muted);font-size:13px;padding:20px 0;">No characteristics to display.</p>';
    return;
  }

  const maxRate = Math.max(...audits.flatMap(a => a.groups.map(g => g.rate)), 0.001);

  audits.forEach((audit, idx) => {
    const dir = audit.disparity.disparate_impact_ratio;
    const flagged = audit.disparity.flag;
    const dirClass = dir >= 0.8 ? 'good' : dir >= 0.6 ? 'warn' : 'bad';
    const dispClass = audit.disparity.max_disparity < 0.1 ? 'good' :
                      audit.disparity.max_disparity < 0.2 ? 'warn' : 'bad';

    const groupBars = audit.groups.map(g => {
      const pct = maxRate > 0 ? (g.rate / maxRate) * 100 : 0;
      const barClass = flagged && g.rate === Math.min(...audit.groups.map(x => x.rate)) ? 'flagged-bar' : '';
      return `
        <div class="group-row">
          <div class="group-meta">
            <span class="group-label">${escHtml(g.group)}</span>
            <span class="group-rate">${(g.rate * 100).toFixed(1)}%</span>
          </div>
          <div class="bar-track">
            <div class="bar-fill ${barClass}" style="width:0%" data-target="${pct.toFixed(1)}%"></div>
          </div>
          <div class="group-count">${g.count.toLocaleString()} rows (${g.percentage}%)</div>
        </div>
      `;
    }).join('');

    const card = document.createElement('div');
    card.className = 'char-card';
    card.style.animationDelay = `${idx * 0.08}s`;
    card.innerHTML = `
      <div class="card-header">
        <span class="char-name">${escHtml(audit.characteristic)}</span>
        <span class="flag-badge ${flagged ? 'flagged' : 'ok'}">${flagged ? '⚑ Flagged' : '✓ OK'}</span>
      </div>
      <div class="card-body">
        ${groupBars}
        <div class="disparity-stats">
          <div class="stat-block">
            <div class="stat-label">Disparate Impact Ratio</div>
            <div class="stat-value ${dirClass}">${dir.toFixed(3)}</div>
          </div>
          <div class="stat-block">
            <div class="stat-label">Max Disparity Gap</div>
            <div class="stat-value ${dispClass}">${(audit.disparity.max_disparity * 100).toFixed(1)}%</div>
          </div>
          ${audit.disparity.highest_group ? `
          <div class="stat-block">
            <div class="stat-label">Highest Group</div>
            <div class="stat-value" style="font-size:12px;color:var(--green)">${escHtml(audit.disparity.highest_group)}</div>
          </div>
          <div class="stat-block">
            <div class="stat-label">Lowest Group</div>
            <div class="stat-value" style="font-size:12px;color:${flagged ? 'var(--red)' : 'var(--text-muted)'}">${escHtml(audit.disparity.lowest_group)}</div>
          </div>` : ''}
        </div>
      </div>
    `;
    grid.appendChild(card);
  });

  // Trigger animation for bars
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      document.querySelectorAll('.bar-fill[data-target]').forEach(el => {
        el.style.width = el.dataset.target;
      });
    });
  });
}

// ── Reset Functionality
resetBtn.addEventListener('click', () => {
  selectedFile = null;
  fileInput.value = '';
  fileBar.classList.remove('visible');
  auditBtn.classList.remove('visible');
  results.classList.remove('visible');
  hideError();
  window.scrollTo({ top: 0, behavior: 'smooth' });
});

// ── Helper Utilities
function showError(msg) {
  errorBox.textContent = '⚠ ' + msg;
  errorBox.classList.add('visible');
}

function hideError() {
  errorBox.classList.remove('visible');
}

function formatBytes(b) {
  if (b < 1024) return b + ' B';
  if (b < 1024 * 1024) return (b / 1024).toFixed(1) + ' KB';
  return (b / 1024 / 1024).toFixed(1) + ' MB';
}

function escHtml(str) {
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}