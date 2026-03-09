"""
inventoryMgmt_preview_v3.html → inventoryMgmt.html 변환 스크립트
Firebase 연동 3가지 변경 + sidebar.js 연결
"""
import re, os

SRC = os.path.join(os.path.dirname(__file__), '..', 'inventoryMgmt.html')

with open(SRC, 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')

# ============================================================
# 1) CSS: .main에 margin-left:250px 추가 (sidebar.js 호환)
# ============================================================
for i, line in enumerate(lines):
    if '.main{flex:1;display:flex;flex-direction:column;overflow:hidden}' in line:
        lines[i] = line.replace(
            '.main{flex:1;display:flex;flex-direction:column;overflow:hidden}',
            '.main{flex:1;display:flex;flex-direction:column;overflow:hidden;margin-left:250px}'
        )
        break

# ============================================================
# 2) sidebar HTML → sidebar.js placeholder
# ============================================================
sidebar_start = None
sidebar_end = None
for i, line in enumerate(lines):
    if '<div class="sidebar">' in line and sidebar_start is None:
        sidebar_start = i
    if sidebar_start is not None and i > sidebar_start and '</div>' in line.strip():
        # Count div nesting
        pass

# Find sidebar block (lines 173-185 based on analysis)
# Replace from <div class="sidebar"> to its closing </div>
for i in range(len(lines)):
    if '<div class="sidebar">' in lines[i]:
        sidebar_start = i
        break

# Find the end of the sidebar div (track nesting)
depth = 0
for i in range(sidebar_start, len(lines)):
    depth += lines[i].count('<div')
    depth -= lines[i].count('</div>')
    if depth <= 0:
        sidebar_end = i
        break

if sidebar_start is not None and sidebar_end is not None:
    # Replace sidebar block with sidebar.js placeholder
    new_sidebar = ['<!-- ===== SIDEBAR (js/sidebar.js) ===== -->', '<aside class="sidebar" id="sidebar"></aside>']
    lines[sidebar_start:sidebar_end+1] = new_sidebar
    # Recalculate line numbers since we removed lines
    print(f'Sidebar replaced: lines {sidebar_start+1}-{sidebar_end+1} → 2 lines')

# ============================================================
# 3) Script section modifications
# ============================================================
# Re-find key positions after sidebar replacement
content = '\n'.join(lines)
lines = content.split('\n')

script_start = None
spec_data_line = None
process_out_line = None
process_in_line = None
save_batch_line = None
render_spec_line = None
save_spec_edit_line = None
init_kpi_line = None
dom_content_loaded_line = None
close_script_line = None
close_body_line = None

for i, line in enumerate(lines):
    s = line.strip()
    if s == '<script>' and script_start is None:
        script_start = i
    if 'const SPEC_DATA' in s:
        spec_data_line = i
    if 'function processOut(' in s:
        process_out_line = i
    if 'function processIn(' in s:
        process_in_line = i
    if 'function saveBatch(' in s:
        save_batch_line = i
    if 'function renderSpecTable(' in s:
        render_spec_line = i
    if 'function saveSpecEdit(' in s:
        save_spec_edit_line = i
    if 'function initKPI(' in s:
        init_kpi_line = i
    if "document.addEventListener('DOMContentLoaded'" in s:
        dom_content_loaded_line = i
    if s == '</script>':
        close_script_line = i
    if '</body>' in s:
        close_body_line = i

print(f'script_start={script_start}, spec_data={spec_data_line}')
print(f'processOut={process_out_line}, processIn={process_in_line}')
print(f'saveSpecEdit={save_spec_edit_line}, initKPI={init_kpi_line}')
print(f'DOMContentLoaded={dom_content_loaded_line}, </script>={close_script_line}')

# 3a) After <script>, add db and allReagents declarations
lines[script_start] = '''<script>
let db;
let allReagents = [];
let _todayLogs = [];'''

# 3b) Remove SPEC_DATA line (huge array) → replace with comment
if spec_data_line is not None:
    lines[spec_data_line] = '// SPEC_DATA 제거됨 — Firestore reagents 컬렉션에서 로드'

# 3c) Replace processOut stub
lines[process_out_line] = '''async function processOut(auto=false) {
  clearT(); hideModal('outConfirmModal');
  // Get scanned reagent info from the scan display
  const scanNameEl = document.getElementById('scanName');
  const scanCodeEl = document.getElementById('scanCode');
  if (!scanNameEl || !scanCodeEl) { showToast('스캔된 제품 정보가 없습니다','warning'); return; }

  const barcodeVal = scanCodeEl.textContent || '';
  const reagent = allReagents.find(r => r.barcodeVal === barcodeVal || 'BFL-'+r.code === barcodeVal);
  if (!reagent) { showToast('제품을 찾을 수 없습니다','warning'); return; }

  const qty = 1;
  const userId = '현재사용자';
  const purpose = '일반출고';

  try {
    const batch = db.batch();
    const ref = db.collection('reagents').doc(reagent.id);
    batch.update(ref, {
      stockQty: firebase.firestore.FieldValue.increment(-qty),
      updatedAt: firebase.firestore.FieldValue.serverTimestamp()
    });
    const logRef = db.collection('reagentLogs').doc();
    batch.set(logRef, {
      reagentId: reagent.id, reagentCode: reagent.code, reagentName: reagent.name,
      type: '출고', qty, userId, purpose,
      unitPrice: reagent.unitPrice || reagent.price || 0,
      inputMethod: '바코드스캔',
      year: new Date().getFullYear(), month: new Date().getMonth() + 1,
      createdAt: firebase.firestore.FieldValue.serverTimestamp()
    });
    await batch.commit();
    // 캐시 업데이트
    reagent.stockQty = (reagent.stockQty || 0) - qty;
    updateKPI();
    renderStockTable();
    loadTodayLogs();
    showToast('📤 출고 완료 처리되었습니다','success',4000);
  } catch(err) {
    console.error('출고 처리 실패:', err);
    showToast('출고 처리 중 오류가 발생했습니다','warning');
  }
}'''

# 3d) Replace processIn stub
lines[process_in_line] = '''async function processIn() {
  hideModal('inModal');
  const scanCodeEl = document.getElementById('scanCode');
  const barcodeVal = scanCodeEl ? scanCodeEl.textContent : '';
  const reagent = allReagents.find(r => r.barcodeVal === barcodeVal || 'BFL-'+r.code === barcodeVal);
  if (!reagent) { showToast('제품을 찾을 수 없습니다','warning'); return; }

  // 입고 모달에서 값 가져오기 (실제 DOM ID에 맞춰 조정)
  const qty = parseInt(document.getElementById('inQty')?.value) || 1;
  const price = parseInt(document.getElementById('inPrice')?.value) || reagent.unitPrice || reagent.price || 0;
  const supplier = document.getElementById('inSupplier')?.value || reagent.supplier || '';
  const mfr = document.getElementById('inMfr')?.value || reagent.mfr || '';
  const userId = '현재사용자';

  try {
    const batch = db.batch();
    const ref = db.collection('reagents').doc(reagent.id);
    batch.update(ref, {
      stockQty: firebase.firestore.FieldValue.increment(qty),
      unitPrice: price, supplier, mfr,
      updatedAt: firebase.firestore.FieldValue.serverTimestamp()
    });
    const logRef = db.collection('reagentLogs').doc();
    batch.set(logRef, {
      reagentId: reagent.id, reagentCode: reagent.code, reagentName: reagent.name,
      type: '입고', qty, userId, unitPrice: price, prevPrice: reagent.unitPrice || reagent.price || 0,
      inputMethod: '바코드스캔',
      year: new Date().getFullYear(), month: new Date().getMonth() + 1,
      createdAt: firebase.firestore.FieldValue.serverTimestamp()
    });
    // 단가/구매처/제조사 변경 감지 → reagentChangeLogs
    const changes = [];
    const prevPrice = reagent.unitPrice || reagent.price || 0;
    if (price !== prevPrice) changes.push({ changeType: '단가', before: String(prevPrice), after: String(price) });
    if (supplier !== reagent.supplier) changes.push({ changeType: '구매처', before: reagent.supplier || '', after: supplier });
    if (mfr !== reagent.mfr) changes.push({ changeType: '제조사', before: reagent.mfr || '', after: mfr });
    for (const c of changes) {
      const cRef = db.collection('reagentChangeLogs').doc();
      batch.set(cRef, { reagentId: reagent.id, reagentCode: reagent.code, ...c, changedBy: userId, changedAt: firebase.firestore.FieldValue.serverTimestamp() });
    }
    await batch.commit();
    // 캐시 업데이트
    reagent.stockQty = (reagent.stockQty || 0) + qty;
    reagent.unitPrice = price; reagent.price = price;
    reagent.supplier = supplier; reagent.mfr = mfr;
    updateKPI();
    renderStockTable();
    loadTodayLogs();
    showToast('📥 입고 완료 — 라벨 출력 중...','success',4000);
  } catch(err) {
    console.error('입고 처리 실패:', err);
    showToast('입고 처리 중 오류가 발생했습니다','warning');
  }
}'''

# 3e) Replace all SPEC_DATA references with allReagents
content = '\n'.join(lines)
content = content.replace('SPEC_DATA.filter', 'allReagents.filter')
content = content.replace('SPEC_DATA.indexOf', 'allReagents.indexOf')
content = content.replace('SPEC_DATA[', 'allReagents[')
content = content.replace('SPEC_DATA.length', 'allReagents.length')
content = content.replace('SPEC_DATA.forEach', 'allReagents.forEach')
lines = content.split('\n')

# Re-find positions after replacements
for i, line in enumerate(lines):
    s = line.strip()
    if 'function saveSpecEdit(' in s:
        save_spec_edit_line = i
    if 'function initKPI(' in s:
        init_kpi_line = i
    if "document.addEventListener('DOMContentLoaded'" in s:
        dom_content_loaded_line = i
    if s == '</script>':
        close_script_line = i
    if '</body>' in s:
        close_body_line = i

# 3f) Find and modify saveSpecEdit to add Firestore save
# Find the line with "// allReagents 업데이트 (프리뷰 - 실제 운영시 Firestore 저장)"
for i, line in enumerate(lines):
    if '프리뷰 - 실제 운영시 Firestore 저장' in line or 'SPEC_DATA 업데이트 (프리뷰' in line or 'allReagents 업데이트 (프리뷰' in line:
        # Replace this comment with actual Firestore save
        lines[i] = '  // Firestore에 저장'
        break

# Find the "성공 토스트" line and add Firestore save before it
for i, line in enumerate(lines):
    if "showToast('✅ 수정 사항이 저장되었습니다'" in line:
        # Insert Firestore save code before this line
        firestore_save = '''
  // Firestore 저장
  if (db && d.id) {
    try {
      await db.collection('reagents').doc(d.id).update({
        name: d.name, dept: d.dept, cat: d.cat,
        catNo: d.catNo, casNo: d.casNo, spec: d.spec,
        mfr: d.mfr, supplier: d.supplier,
        unitPrice: d.price, minQty: d.minQty,
        updatedAt: firebase.firestore.FieldValue.serverTimestamp()
      });
      // 변경 이력 → reagentChangeLogs
      const userId = '현재사용자';
      if (prev.mfr !== newMfr && prev.mfr && newMfr) {
        await db.collection('reagentChangeLogs').add({
          reagentId: d.id, changeType: '제조사', before: prev.mfr, after: newMfr,
          changedBy: userId, changedAt: firebase.firestore.FieldValue.serverTimestamp()
        });
      }
      if (prev.supplier !== newSupplier && prev.supplier && newSupplier) {
        await db.collection('reagentChangeLogs').add({
          reagentId: d.id, changeType: '구매처', before: prev.supplier, after: newSupplier,
          changedBy: userId, changedAt: firebase.firestore.FieldValue.serverTimestamp()
        });
      }
      if (prev.price !== newPrice && newPrice) {
        await db.collection('reagentChangeLogs').add({
          reagentId: d.id, changeType: '단가', before: String(prev.price), after: String(newPrice),
          changedBy: userId, changedAt: firebase.firestore.FieldValue.serverTimestamp()
        });
      }
    } catch(err) { console.error('Firestore 저장 실패:', err); }
  }
'''
        lines[i] = firestore_save + '\n' + line
        break

# Make saveSpecEdit async
for i, line in enumerate(lines):
    if 'function saveSpecEdit()' in line:
        lines[i] = line.replace('function saveSpecEdit()', 'async function saveSpecEdit()')
        break

# 3g) Replace initKPI with Firebase-aware version
# Find initKPI function and replace entirely
init_kpi_start = None
init_kpi_end = None
for i, line in enumerate(lines):
    if 'function initKPI()' in line:
        init_kpi_start = i
        break

if init_kpi_start is not None:
    # Find the end of initKPI (next function or closing brace at same level)
    brace_depth = 0
    for i in range(init_kpi_start, len(lines)):
        brace_depth += lines[i].count('{') - lines[i].count('}')
        if brace_depth == 0 and i > init_kpi_start:
            init_kpi_end = i
            break

    if init_kpi_end is not None:
        new_init_kpi = '''function initKPI() {
  updateKPI();
}

function updateKPI() {
  const total = allReagents.length;
  const deptCnt = {};
  allReagents.forEach(d => { deptCnt[d.dept] = (deptCnt[d.dept]||0)+1; });
  const deptStr = Object.entries(deptCnt).map(([k,v])=>k+' '+v.toLocaleString()).join(' · ');

  const el = (id) => document.getElementById(id);
  if(el('kpiTotal')) el('kpiTotal').textContent = total.toLocaleString();
  if(el('kpiDeptSub')) el('kpiDeptSub').textContent = deptStr || '-';

  // 재고 있는 품목 / 없는 품목
  const hasStock = allReagents.filter(r => (r.stockQty || 0) > 0).length;
  const noStock = allReagents.filter(r => (r.stockQty || 0) <= 0).length;
  if(el('kpiHasStock')) el('kpiHasStock').textContent = hasStock.toLocaleString();
  if(el('kpiNoStock')) el('kpiNoStock').textContent = noStock.toLocaleString();

  // 안전재고 미달 품목
  const lowStock = allReagents.filter(r => (r.stockQty || 0) > 0 && (r.stockQty || 0) <= (r.minQty || 1)).length;
  if(el('kpiExpiry')) el('kpiExpiry').textContent = lowStock.toLocaleString();

  // 재고 총 자산
  const totalCost = allReagents.reduce((sum, r) => sum + ((r.stockQty || 0) * (r.unitPrice || r.price || 0)), 0);
  if(el('kpiStockCost')) el('kpiStockCost').textContent = totalCost > 0 ? totalCost.toLocaleString() + '원' : '-';
}'''
        lines[init_kpi_start:init_kpi_end+1] = new_init_kpi.split('\n')

# Rebuild and re-find positions
content = '\n'.join(lines)
lines = content.split('\n')

for i, line in enumerate(lines):
    s = line.strip()
    if "document.addEventListener('DOMContentLoaded'" in s:
        dom_content_loaded_line = i
    if 'setTimeout(() => { renderSpecTable()' in s:
        setTimeout_line = i
    if s == '</script>':
        close_script_line = i
    if '</body>' in s:
        close_body_line = i

# 3h) Replace DOMContentLoaded + setTimeout with firebase-ready
print(f'DOMContentLoaded line: {dom_content_loaded_line}')
if dom_content_loaded_line is not None:
    lines[dom_content_loaded_line] = '''// Firebase 연결 후 초기화
window.addEventListener('firebase-ready', async function() {
  db = firebase.firestore();
  await loadReagents();
  initKPI();
  loadTodayLogs();
});'''

# Remove the setTimeout fallback line
for i, line in enumerate(lines):
    if 'setTimeout(() => { renderSpecTable()' in line and 'initKPI()' in line:
        lines[i] = '// setTimeout 제거됨 — firebase-ready 이벤트 사용'
        break

# 3i) Add loadReagents, renderStockTable, loadTodayLogs functions before </script>
for i, line in enumerate(lines):
    if line.strip() == '</script>':
        close_script_line = i
        break

new_functions = '''
// ============================================================
// Firestore 데이터 로드
// ============================================================
async function loadReagents() {
  try {
    const snap = await db.collection('reagents').orderBy('code').get();
    allReagents = snap.docs.map(d => {
      const data = { id: d.id, ...d.data() };
      // v3 UI 호환 필드 매핑
      data.price = data.unitPrice || 0;
      data.changes = [];
      data.priceChange = 0;
      data.consume = '-';
      return data;
    });
    console.log('[재고관리] ' + allReagents.length + '건 로드 완료');
    renderSpecTable();
    renderStockTable();
    updateKPI();
  } catch(err) {
    console.error('[재고관리] 데이터 로드 실패:', err);
    showToast('데이터 로드 중 오류가 발생했습니다', 'warning');
  }
}

// 재고 현황 테이블 렌더링
function renderStockTable() {
  const tbody = document.querySelector('#tab-stock table tbody');
  if (!tbody) return;

  const hasStockItems = allReagents.filter(r => (r.stockQty || 0) > 0);

  if (hasStockItems.length === 0) {
    tbody.innerHTML = '<tr><td colspan="10" style="text-align:center;padding:32px;color:var(--text-muted);font-size:13px">📭 재고 데이터가 없습니다.<br><span style="font-size:11px;color:var(--text-light)">입고 처리 후 이곳에 재고가 표시됩니다.</span></td></tr>';
    return;
  }

  tbody.innerHTML = hasStockItems.map(d => {
    const stockClass = (d.stockQty || 0) <= (d.minQty || 1) ? 'color:var(--danger);font-weight:700' : '';
    return '<tr>' +
      '<td>' + (d.code || '') + '</td>' +
      '<td><span class="badge" style="' + (d.dept==='이화학' ? 'background:#e0f2fe;color:#0369a1' : 'background:#fce7f3;color:#be185d') + ';padding:2px 8px;border-radius:10px;font-size:11px">' + (d.dept || '') + '</span></td>' +
      '<td>' + (d.cat || '') + '</td>' +
      '<td style="font-weight:600">' + (d.name || '') + '</td>' +
      '<td>' + (d.spec || '') + '</td>' +
      '<td>' + (d.mfr || '') + (d.supplier ? ' / ' + d.supplier : '') + '</td>' +
      '<td style="text-align:right">' + ((d.unitPrice || d.price || 0).toLocaleString()) + '</td>' +
      '<td style="text-align:center;' + stockClass + '">' + (d.stockQty || 0) + '</td>' +
      '<td>' + (d.expiryRef || '-') + '</td>' +
      '<td><button class="btn btn-outline btn-sm" onclick="viewReagentHistory(\\'' + d.id + '\\')">이력</button></td>' +
      '</tr>';
  }).join('');

  // 품목 수 업데이트
  const countEl = document.querySelector('#tab-stock .table-header span:last-child');
  if (countEl) countEl.textContent = hasStockItems.length.toLocaleString() + '개 품목 · 클릭하면 이력 보기';
}

// 시약 이력 보기
async function viewReagentHistory(reagentId) {
  if (!db) return;
  try {
    const snap = await db.collection('reagentLogs')
      .where('reagentId', '==', reagentId)
      .orderBy('createdAt', 'desc')
      .limit(50)
      .get();
    const logs = snap.docs.map(d => d.data());
    if (logs.length === 0) {
      showToast('이 시약의 입출고 기록이 없습니다', 'info');
      return;
    }
    // historyDetailModal에 표시
    const content = document.getElementById('historyDetailContent');
    if (content) {
      content.innerHTML = logs.map(l => {
        const date = l.createdAt ? new Date(l.createdAt.seconds * 1000).toLocaleString('ko-KR') : '-';
        const typeClass = l.type === '입고' ? 'tag-in' : 'tag-out';
        return '<div style="display:flex;gap:12px;align-items:center;padding:8px 0;border-bottom:1px solid var(--border)">' +
          '<span style="font-size:12px;color:var(--text-muted);min-width:120px">' + date + '</span>' +
          '<span class="tag ' + typeClass + '">' + (l.type || '') + '</span>' +
          '<span style="font-weight:600">' + (l.qty || 0) + '개</span>' +
          '<span style="font-size:12px;color:var(--text-muted)">' + (l.userId || '') + '</span>' +
          '<span style="font-size:12px;color:var(--text-muted)">' + (l.purpose || '') + '</span>' +
          '</div>';
      }).join('');
      showModal('historyDetailModal');
    }
  } catch(err) {
    console.error('이력 조회 실패:', err);
  }
}

// 오늘 입출고 로그 로드
async function loadTodayLogs() {
  if (!db) return;
  try {
    const today = new Date();
    today.setHours(0,0,0,0);
    const snap = await db.collection('reagentLogs')
      .where('createdAt', '>=', today)
      .orderBy('createdAt', 'desc')
      .limit(100)
      .get();
    _todayLogs = snap.docs.map(d => ({ id: d.id, ...d.data() }));
    renderTodayLogs();
  } catch(err) {
    console.error('오늘 로그 로드 실패:', err);
  }
}
function initTodayLogs() { loadTodayLogs(); }

// 오늘 입출고 로그 렌더링
function renderTodayLogs() {
  const tbody = document.querySelector('#tab-history table tbody');
  if (!tbody) return;

  if (_todayLogs.length === 0) {
    tbody.innerHTML = '<tr><td colspan="13" style="text-align:center;padding:32px;color:var(--text-muted);font-size:13px">📭 입출고 기록이 없습니다.<br><span style="font-size:11px;color:var(--text-light)">입출고 처리 후 이곳에 기록됩니다.</span></td></tr>';
    return;
  }

  tbody.innerHTML = _todayLogs.map(l => {
    const date = l.createdAt ? new Date(l.createdAt.seconds * 1000).toLocaleString('ko-KR') : '-';
    const typeClass = l.type === '입고' ? 'tag-in' : 'tag-out';
    const priceChange = l.prevPrice && l.unitPrice && l.prevPrice !== l.unitPrice
      ? (l.unitPrice > l.prevPrice ? '<span style="color:var(--danger)">▲</span>' : '<span style="color:var(--success)">▼</span>')
      : '';
    return '<tr>' +
      '<td>' + date + '</td>' +
      '<td><span class="tag ' + typeClass + '">' + (l.type || '') + '</span></td>' +
      '<td style="font-weight:600">' + (l.reagentName || '') + '</td>' +
      '<td>' + (l.spec || '-') + '</td>' +
      '<td style="text-align:right">' + ((l.unitPrice || 0).toLocaleString()) + '</td>' +
      '<td>' + priceChange + '</td>' +
      '<td style="text-align:center;font-weight:700">' + (l.qty || 0) + '</td>' +
      '<td>' + (l.userId || '') + '</td>' +
      '<td>-</td><td>-</td>' +
      '<td>' + (l.purpose || '') + '</td>' +
      '<td>-</td>' +
      '<td>' + (l.inputMethod || '') + '</td>' +
      '</tr>';
  }).join('');
}

// 변경 이력 로드 (제품 사양 상세)
async function loadChangeLogs(reagentId) {
  if (!db) return [];
  try {
    const snap = await db.collection('reagentChangeLogs')
      .where('reagentId', '==', reagentId)
      .orderBy('changedAt', 'desc')
      .limit(20)
      .get();
    return snap.docs.map(d => {
      const data = d.data();
      const date = data.changedAt ? new Date(data.changedAt.seconds * 1000).toLocaleDateString('ko-KR',{year:'2-digit',month:'2-digit',day:'2-digit'}).replace(/ /g,'') : '-';
      const colorMap = {'단가':'danger','구매처':'warning','제조사':'success'};
      return {
        date, type: data.changeType || '', from: data.before || '', to: data.after || '',
        by: data.changedBy || '', color: colorMap[data.changeType] || 'warning',
        rate: data.changeType === '단가' && data.before && data.after
          ? (((parseInt(data.after) - parseInt(data.before)) / parseInt(data.before) * 100).toFixed(1) + '%') : ''
      };
    });
  } catch(err) {
    console.error('변경 이력 로드 실패:', err);
    return [];
  }
}
'''

lines.insert(close_script_line, new_functions)

# Rebuild content and re-find </body>
content = '\n'.join(lines)
lines = content.split('\n')
for i, line in enumerate(lines):
    if '</body>' in line:
        close_body_line = i
        break

# ============================================================
# 4) Before </body>: Add Firebase CDN + sidebar.js
# ============================================================
firebase_scripts = '''
<!-- Firebase SDK -->
<script src="https://www.gstatic.com/firebasejs/10.14.1/firebase-app-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.14.1/firebase-firestore-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.14.1/firebase-auth-compat.js"></script>
<script src="js/firebase-init.js"></script>
<script src="js/sidebar.js"></script>'''

lines.insert(close_body_line, firebase_scripts)

# ============================================================
# 5) Make openSpecDetail async and load change logs from Firestore
# ============================================================
content = '\n'.join(lines)

# In openSpecDetail, after "d.changes" references, load from Firestore
# Find the function and make it async
content = content.replace('function openSpecDetail(idx)', 'async function openSpecDetail(idx)')

# Load change logs from Firestore when opening spec detail
content = content.replace(
    "  if (d.changes.length === 0) {",
    "  // Firestore에서 변경 이력 로드\n  if (d.id && db) { try { d.changes = await loadChangeLogs(d.id); } catch(e){} }\n  if (d.changes.length === 0) {"
)

# ============================================================
# Write output
# ============================================================
with open(SRC, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\n✅ 변환 완료! {len(content.split(chr(10)))} lines written')
