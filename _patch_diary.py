#!/usr/bin/env python3
"""Patch salesMgmt.html: replace old diary HTML and JS with new versions."""
import sys

with open('salesMgmt.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ============================================================
# STEP 1: Replace old diary HTML (3 page blocks) with new (2 page blocks)
# ============================================================
html_start = '    <!-- ===== 업무일지 - 목록 ===== -->'
html_end = '    <!-- ===== 차량일지 ===== -->'

si = content.index(html_start)
ei = content.index(html_end)

new_html = r'''    <!-- ===== 업무일지 - 목록 ===== -->
    <div class="page" id="page-daily" style="display:none">
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px">
        <h2 style="font-size:17px;font-weight:700;color:#1a2332">업무일지</h2>
        <span id="diaryYearLabel" style="font-size:13px;color:#8892a4"></span>
        <div style="margin-left:auto;display:flex;gap:6px">
          <button class="btn btn-secondary btn-sm" onclick="diaryChangeYear(-1)">&lt;</button>
          <button class="btn btn-secondary btn-sm" onclick="diaryChangeYear(1)">&gt;</button>
        </div>
      </div>
      <div id="diaryMonthTabs" style="display:flex;gap:4px;margin-bottom:14px;flex-wrap:wrap"></div>
      <div class="card">
        <div class="card-hd">
          <h3 id="diaryListTitle">업무일지</h3>
          <div class="right">
            <span id="diaryListCount" style="font-size:11px;color:#8892a4"></span>
            <button class="btn btn-primary btn-sm" onclick="openDiaryToday()">+ 오늘 일지 작성</button>
          </div>
        </div>
        <div id="diaryListBody" class="card-bd" style="padding:0">
          <div style="padding:40px;text-align:center;color:#8892a4;font-size:13px">로딩 중...</div>
        </div>
      </div>
    </div>

    <!-- ===== 업무일지 - 작성/상세 ===== -->
    <div class="page" id="page-dailyDetail" style="display:none">
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px;flex-wrap:wrap">
        <button class="btn btn-secondary btn-sm" onclick="showPage('daily')">← 목록으로</button>
        <span id="diaryDetailDateLabel" style="font-size:14px;font-weight:700;color:#1a2332"></span>
        <span id="diaryDetailAuthor" style="font-size:11px;color:#8892a4"></span>
        <div style="margin-left:auto;display:flex;align-items:center;gap:8px;flex-wrap:wrap">
          <span id="diaryDraftBadge" class="draft-badge" style="display:none">임시저장 중</span>
          <button class="btn btn-secondary btn-sm" onclick="saveDiary('draft')">임시저장</button>
          <button class="btn btn-primary btn-sm" onclick="saveDiary('saved')">저장완료</button>
        </div>
      </div>

      <div class="sec-title"><span class="sec-num">1</span> 방문 업체 <span style="font-size:11px;font-weight:400;color:#8892a4;margin-left:2px">업체별 검사목적·매출·특이사항 기록</span></div>
      <div id="diaryCompanyCards"></div>
      <button class="btn-add" onclick="addDiaryCompanyCard()" style="margin-top:8px;margin-bottom:16px;width:100%;padding:10px;border:2px dashed #d0d7de;border-radius:10px;background:none;color:#8892a4;font-size:13px;font-weight:600;cursor:pointer;font-family:inherit;transition:all .15s" onmouseover="this.style.borderColor='#1a73e8';this.style.color='#1a73e8'" onmouseout="this.style.borderColor='#d0d7de';this.style.color='#8892a4'">+ 업체 추가</button>

      <div class="sec-title"><span class="sec-num">2</span> 오늘 매출 합계 <span style="font-size:11px;font-weight:400;color:#8892a4;margin-left:2px">부가세 별도 기준</span></div>
      <div id="diarySumBlock" class="sum-card" style="margin-bottom:16px">
        <div style="color:#8892a4;font-size:12px;text-align:center;padding:14px">업체별 금액을 입력하면 자동 취합됩니다.</div>
      </div>

      <div class="sec-title"><span class="sec-num">3</span> 경쟁사 동향</div>
      <textarea id="diaryCompetitor" class="bottom-input yellow" style="margin-bottom:16px" placeholder="경쟁사 관련 특이사항&#10;예: A기관 미생물 단가 8% 인하, B기관 신규 서비스 런칭 등"></textarea>

      <div class="sec-title"><span class="sec-num">4</span> 신규영업 활동</div>
      <textarea id="diaryNewSales" class="bottom-input" style="margin-bottom:16px" placeholder="신규 영업 활동 내용&#10;예: 하림그룹 식품안전팀 미팅 — 제안서 전달"></textarea>

      <div class="sec-title"><span class="sec-num">5</span> 비고</div>
      <textarea id="diaryRemark" class="bottom-input" style="min-height:44px;margin-bottom:16px" placeholder="기타 전달사항"></textarea>

      <div class="sec-title"><span class="sec-num">6</span> 익일 계획</div>
      <div class="tmr-tabs">
        <button class="tmr-tab tmr-tab-act" onclick="switchTmrTab('existing',this)">기존 거래처 방문</button>
        <button class="tmr-tab" onclick="switchTmrTab('new',this)">신규 영업</button>
        <button class="tmr-tab" onclick="switchTmrTab('memo',this)">메모</button>
      </div>

      <div id="tmr-existing" class="tmr-panel">
        <div class="tmr-panel-hd">
          <span style="font-size:11px;color:#5f6b7a">내일 방문할 업체와 예상매출을 입력하세요.</span>
          <button class="btn btn-secondary btn-sm" onclick="addTmrExisting()">+ 업체 추가</button>
        </div>
        <div id="tmrExistingList"></div>
        <div id="tmrExistingEmpty" class="tmr-empty">추가된 업체가 없습니다.</div>
        <div id="tmrExistingSummary" class="tmr-summary" style="display:none"></div>
      </div>

      <div id="tmr-new" class="tmr-panel" style="display:none">
        <div style="display:flex;gap:0;margin-bottom:12px;border:1px solid #e2e6ed;border-radius:8px;overflow:hidden">
          <button id="modeBtn-search" onclick="switchNewMode('search')" style="flex:1;padding:8px 0;font-size:12px;font-weight:600;cursor:pointer;border:none;background:#1a73e8;color:#fff;transition:all .15s;font-family:inherit">업체명 검색</button>
          <button id="modeBtn-area" onclick="switchNewMode('area')" style="flex:1;padding:8px 0;font-size:12px;font-weight:600;cursor:pointer;border:none;background:#fff;color:#5f6b7a;transition:all .15s;font-family:inherit;border-left:1px solid #e2e6ed">지역 탐색</button>
        </div>
        <div id="mode-search">
          <div style="display:flex;gap:8px;align-items:center;margin-bottom:8px">
            <input id="tmrNewSearchInput" class="tmr-search-inp" type="text" placeholder="업체명·품목·업종 검색" oninput="searchFssLive(this.value)" autocomplete="off">
            <button class="btn btn-secondary btn-sm" onclick="clearTmrSearch()">지우기</button>
          </div>
          <div id="tmrNewSearchResult" class="tmr-search-result">
            <div style="color:#8892a4;font-size:12px;text-align:center;padding:20px">업체명·품목·업종을 입력하면 식약처 인허가 데이터에서 검색합니다.</div>
          </div>
        </div>
        <div id="mode-area" style="display:none">
          <div id="areaBreadcrumb" style="display:flex;align-items:center;gap:4px;font-size:12px;margin-bottom:10px;flex-wrap:wrap">
            <span style="color:#8892a4">전체 지역</span>
          </div>
          <div id="sidoPanel">
            <div style="font-size:11px;font-weight:700;color:#5f6b7a;margin-bottom:8px">시/도 선택</div>
            <div id="sidoGrid" style="display:grid;grid-template-columns:repeat(5,1fr);gap:6px"></div>
          </div>
          <div id="sgPanel" style="display:none">
            <div style="font-size:11px;font-weight:700;color:#5f6b7a;margin-bottom:8px">시/군/구 선택</div>
            <div id="sgGrid" style="display:grid;grid-template-columns:repeat(4,1fr);gap:6px"></div>
          </div>
          <div id="dongPanel" style="display:none">
            <div style="font-size:11px;font-weight:700;color:#5f6b7a;margin-bottom:8px">읍/면/동 선택</div>
            <div id="dongGrid" style="display:grid;grid-template-columns:repeat(4,1fr);gap:6px"></div>
          </div>
          <div id="areaResultPanel" style="display:none">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
              <span id="areaResultTitle" style="font-size:12px;font-weight:700;color:#1a2332"></span>
              <span id="areaResultCount" style="font-size:11px;color:#8892a4"></span>
            </div>
            <div id="areaResultList" class="tmr-search-result"></div>
          </div>
        </div>
        <div id="tmrNewList" style="margin-top:12px"></div>
        <div id="tmrNewEmpty" class="tmr-empty">추가된 신규 영업 업체가 없습니다.</div>
      </div>

      <div id="tmr-memo" class="tmr-panel" style="display:none">
        <textarea id="diaryTomorrowMemo" class="bottom-input blue" placeholder="기타 내일 계획 메모&#10;예: 견적서 발송, 미수금 전화, 내부 보고 등"></textarea>
      </div>

      <div style="padding-top:16px;margin-top:16px;border-top:1px solid #eef0f4;display:flex;justify-content:flex-end;gap:8px">
        <button class="btn btn-secondary" onclick="showPage('daily')">취소</button>
        <button class="btn btn-secondary" onclick="saveDiary('draft')">임시저장</button>
        <button class="btn btn-primary" onclick="saveDiary('saved')">저장완료</button>
      </div>
    </div>

'''

content = content[:si] + new_html + content[ei:]

# ============================================================
# STEP 2: Replace old diary JS (4434~5030) with new diary JS
# ============================================================
js_start = '// ── 업무일지 탭 전환 ──\n'
js_end = '\n// ============================================================================\n// 세금계산서 미발행 / 발행요청 — Firestore receipts 연동'

jsi = content.index(js_start)
jei = content.index(js_end)

new_js = '''// ============================================================================
// 업무일지 시스템 (salesDiaries Firestore 연동)
// ============================================================================
var _diaryYear = new Date().getFullYear();
var _diaryMonth = new Date().getMonth() + 1;
var _diaryDate = null;
var _diaryDoc = null;
var _diaryCardIdx = 0;
var _diaryPurposes = [];
var _diaryCompanies = [];
var _diaryMonthCache = {};
var _diaryInited = false;

// 익일 계획
var _tmrExisting = [];
var _tmrNew = [];
var _newMode = 'search';
var _areaSido = '', _areaSg = '', _areaDong = '';
var _fssSearchTimer = null;

// 검사목적 색상 팔레트
var DIARY_PURPOSE_PALETTE = [
  {color:'#e3f2fd',textColor:'#1565c0'},
  {color:'#e8f5e9',textColor:'#2e7d32'},
  {color:'#fff3e0',textColor:'#e65100'},
  {color:'#f3e5f5',textColor:'#7b1fa2'},
  {color:'#fce4ec',textColor:'#c62828'},
  {color:'#e0f2f1',textColor:'#00695c'}
];

// ── 초기화 ──
async function initDiary() {
  if (_diaryInited) return;
  try {
    // 검사목적 로드
    var pDoc = await db.collection('settings').doc('inspectionPurposes').get();
    if (pDoc.exists) {
      var arr = (pDoc.data().purposes || []).filter(function(p) { return p.o !== 0; });
      // 중복 이름 제거
      var seen = {};
      _diaryPurposes = [];
      arr.forEach(function(p) {
        var n = p.n || '';
        if (!seen[n] && n) { seen[n] = true; _diaryPurposes.push(p); }
      });
    }
    // 업체 로드
    var cSnap = await db.collection('companies').get();
    _diaryCompanies = cSnap.docs.map(function(d) {
      var data = d.data();
      return { id: d.id, name: data.company || data.name || '', addr: data.addr1 || data.bizAddress || '', salesRep: data.salesRep || '' };
    }).filter(function(c) { return c.name; });
    _diaryCompanies.sort(function(a,b) { return a.name.localeCompare(b.name); });
  } catch(e) { console.error('업무일지 초기화 실패:', e); }
  _diaryInited = true;
}

// ── 연도/월 탭 ──
function diaryChangeYear(d) {
  _diaryYear += d;
  renderDiaryMonthTabs();
  loadDiaryList();
}

function renderDiaryMonthTabs() {
  var el = document.getElementById('diaryMonthTabs');
  var label = document.getElementById('diaryYearLabel');
  if (!el) return;
  if (label) label.textContent = _diaryYear + '년';
  var html = '';
  for (var m = 1; m <= 12; m++) {
    var key = _diaryYear + '-' + String(m).padStart(2,'0');
    var hasData = _diaryMonthCache[key];
    var isActive = m === _diaryMonth && _diaryYear === new Date().getFullYear() ? true : m === _diaryMonth;
    var cls = isActive ? 'month-tab mt-active' : (hasData ? 'month-tab mt-has' : 'month-tab mt-empty');
    html += '<button class="' + cls + '" onclick="selectDiaryMonth(' + m + ')">' + m + '월</button>';
  }
  el.innerHTML = html;
}

function selectDiaryMonth(m) {
  _diaryMonth = m;
  renderDiaryMonthTabs();
  loadDiaryList();
}

// ── 목록 로드 ──
async function loadDiaryList() {
  var body = document.getElementById('diaryListBody');
  var titleEl = document.getElementById('diaryListTitle');
  var countEl = document.getElementById('diaryListCount');
  if (!body) return;
  body.innerHTML = '<div style="padding:40px;text-align:center;color:#8892a4;font-size:13px">로딩 중...</div>';
  if (titleEl) titleEl.textContent = _diaryMonth + '월 업무일지';

  var mm = String(_diaryMonth).padStart(2,'0');
  var prefix = _diaryYear + '' + mm;
  try {
    var snap = await db.collection('salesDiaries')
      .where(firebase.firestore.FieldPath.documentId(), '>=', prefix + '01')
      .where(firebase.firestore.FieldPath.documentId(), '<', prefix + '32')
      .orderBy(firebase.firestore.FieldPath.documentId(), 'desc')
      .get();

    var docs = snap.docs.map(function(d) { var data = d.data(); data._id = d.id; return data; });
    var key = _diaryYear + '-' + mm;
    _diaryMonthCache[key] = docs.length > 0;
    renderDiaryMonthTabs();

    if (countEl) countEl.textContent = '총 ' + docs.length + '건';

    if (docs.length === 0) {
      body.innerHTML = '<div style="padding:40px;text-align:center;color:#8892a4;font-size:13px">작성된 업무일지가 없습니다.</div>';
      return;
    }

    var todayStr = getTodayStr().replace(/-/g,'');
    var html = '';
    docs.forEach(function(doc) {
      var dateStr = doc.date || '';
      var docId = doc._id || '';
      var isToday = docId === todayStr;
      var isDraft = doc.status === 'draft';

      // 날짜 파싱
      var dateObj = null, dayLabel = '', dowLabel = '';
      if (dateStr) {
        dateObj = new Date(dateStr);
        dayLabel = (dateObj.getMonth()+1) + '월 ' + dateObj.getDate() + '일';
        var dows = ['일','월','화','수','목','금','토'];
        dowLabel = '(' + dows[dateObj.getDay()] + ')';
      }

      // 업체 칩
      var companies = doc.companies || [];
      var chipHtml = '';
      companies.forEach(function(c) {
        var isNew = c.type === 'new';
        var cls = isNew ? 'chip chip-new' : 'chip chip-exist';
        var prefix = isNew ? '★ ' : '';
        chipHtml += '<span class="' + cls + '">' + prefix + escHtml(c.companyName || '미지정') + '</span> ';
      });
      if (isDraft) chipHtml += '<span class="draft-badge">임시저장</span>';
      if (isToday) chipHtml += '<span style="font-size:9px;background:#1a73e8;color:#fff;padding:1px 5px;border-radius:3px;margin-left:2px">오늘</span>';

      // 매출 합계
      var total = 0;
      companies.forEach(function(c) {
        if (c.purposeSales) Object.values(c.purposeSales).forEach(function(v) { total += (v.amount || 0); });
      });
      var revHtml = total > 0 ? '<span style="font-weight:700;color:#1565c0">' + total.toLocaleString() + '원</span>' : '<span style="color:#c8d6e5">—</span>';

      html += '<div class="diary-row" onclick="openDiaryDetail(\\'' + docId + '\\')">';
      html += '<div><div style="font-weight:600;font-size:13px">' + dayLabel + '</div><div style="font-size:10px;color:#8892a4">' + dowLabel + '</div></div>';
      html += '<div class="chips">' + chipHtml + '</div>';
      html += '<div style="text-align:right">' + revHtml + '</div>';
      html += '<div style="text-align:center;font-size:14px;color:#8892a4">›</div>';
      html += '</div>';
    });
    body.innerHTML = html;

    // 통계 업데이트
    updateDiaryStats(docs);
  } catch(e) {
    console.error('업무일지 목록 로드 실패:', e);
    body.innerHTML = '<div style="padding:40px;text-align:center;color:#e53935;font-size:13px">로드 실패: ' + e.message + '</div>';
  }
}

function updateDiaryStats(docs) {
  var count = docs.length;
  var visits = 0, revenue = 0, newBiz = 0;
  docs.forEach(function(doc) {
    (doc.companies || []).forEach(function(c) {
      if (c.collectMethod === '방문') visits++;
      if (c.purposeSales) Object.values(c.purposeSales).forEach(function(v) { revenue += (v.amount||0); });
      if (c.type === 'new') newBiz++;
    });
    if (doc.newSalesActivity) newBiz++;
  });
  var el1 = document.getElementById('wl-stat-count'); if (el1) el1.textContent = count;
  var el2 = document.getElementById('wl-stat-visit'); if (el2) el2.textContent = visits;
  var el3 = document.getElementById('wl-stat-revenue'); if (el3) el3.textContent = revenue > 0 ? revenue.toLocaleString() : '0';
  var el4 = document.getElementById('wl-stat-new'); if (el4) el4.textContent = newBiz;
}

function getTodayStr() {
  var d = new Date();
  return d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0');
}

function openDiaryToday() {
  var todayId = getTodayStr().replace(/-/g,'');
  openDiaryDetail(todayId);
}

// ── 상세 페이지 ──
async function openDiaryDetail(docId) {
  _diaryDate = docId; // YYYYMMDD
  _diaryDoc = null;
  _diaryCardIdx = 0;
  _tmrExisting = [];
  _tmrNew = [];

  await initDiary();
  showPage('dailyDetail');

  // 날짜 라벨
  var dateStr = docId.slice(0,4)+'-'+docId.slice(4,6)+'-'+docId.slice(6,8);
  var dateObj = new Date(dateStr);
  var dows = ['일','월','화','수','목','금','토'];
  var label = dateObj.getFullYear() + '년 ' + (dateObj.getMonth()+1) + '월 ' + dateObj.getDate() + '일 (' + dows[dateObj.getDay()] + ')';
  var el = document.getElementById('diaryDetailDateLabel');
  if (el) el.textContent = label;
  var authorEl = document.getElementById('diaryDetailAuthor');
  if (authorEl) authorEl.textContent = '작성자: 사용자';

  // Firestore 로드
  try {
    var docRef = db.collection('salesDiaries').doc(docId);
    var snap = await docRef.get();
    if (snap.exists) {
      _diaryDoc = snap.data();
      _diaryDoc._id = docId;
    }
  } catch(e) { console.error(e); }

  renderDiaryDetailForm();
}

function renderDiaryDetailForm() {
  var d = _diaryDoc || {};
  var cards = document.getElementById('diaryCompanyCards');
  if (cards) cards.innerHTML = '';
  _diaryCardIdx = 0;

  // 업체 카드
  var companies = d.companies || [];
  if (companies.length === 0) {
    addDiaryCompanyCard(); // 최소 1개
  } else {
    companies.forEach(function(c) { addDiaryCompanyCard(c); });
  }

  // 텍스트 필드
  var f = function(id,val) { var e=document.getElementById(id); if(e) e.value = val||''; };
  f('diaryCompetitor', d.competitorNote);
  f('diaryNewSales', d.newSalesActivity);
  f('diaryRemark', d.remark);
  f('diaryTomorrowMemo', d.tomorrowMemo);

  // 임시저장 뱃지
  var badge = document.getElementById('diaryDraftBadge');
  if (badge) badge.style.display = (d.status === 'draft') ? 'inline-flex' : 'none';

  // 익일 계획
  _tmrExisting = d.tomorrowExisting || [];
  _tmrNew = d.tomorrowNew || [];
  renderTmrExisting();
  renderTmrNew();

  updateDiarySumBlock();
}

// ── 업체 카드 ──
function addDiaryCompanyCard(data) {
  var d = data || {};
  var uid = d.uid || (Date.now() + '_' + Math.random().toString(36).slice(2,6));
  var idx = _diaryCardIdx++;
  var isNew = d.type === 'new';
  var container = document.getElementById('diaryCompanyCards');
  if (!container) return;

  var card = document.createElement('div');
  card.id = 'dc-' + uid;
  card.className = 'sub-card' + (isNew ? ' sub-card-new' : '');
  card.setAttribute('data-uid', uid);

  // 업체 select
  var compOpts = '<option value="">업체 선택...</option>';
  _diaryCompanies.forEach(function(c) {
    var sel = (d.companyName === c.name) ? ' selected' : '';
    compOpts += '<option value="' + escHtml(c.name) + '"' + sel + '>' + escHtml(c.name) + '</option>';
  });
  if (_diaryCompanies.length === 0) compOpts = '<option value="">등록된 업체 없음</option>';

  // 소개경로 버튼
  var introPaths = ['고객지원팀소개','마케팅팀소개','지인소개','기존거래처소개','신규영업'];
  var introLabels = ['고객지원팀','마케팅팀','지인','기존거래처','직접영업'];
  var introHtml = '';
  introPaths.forEach(function(p,i) {
    var act = (d.introPath === p) ? ' act' : '';
    introHtml += '<button class="intro-btn' + act + '" onclick="selectDiaryIntro(\\'' + uid + '\\',\\'' + p + '\\')">' + introLabels[i] + '</button> ';
  });

  // 수거방법
  var methods = ['방문','택배','퀵','내방'];
  var methodOpts = '<option value="">선택</option>';
  methods.forEach(function(m) {
    var sel = (d.collectMethod === m) ? ' selected' : '';
    methodOpts += '<option' + sel + '>' + m + '</option>';
  });

  // 검사목적별 매출 테이블
  var savedPS = d.purposeSales || {};
  var ptHtml = '<table class="pt"><thead><tr><th style="width:40%">검사목적</th><th style="width:30%">금액(원)</th><th>메모</th></tr></thead><tbody>';
  if (_diaryPurposes.length === 0) {
    ptHtml += '<tr><td colspan="3" style="text-align:center;color:#8892a4;font-size:11px;padding:12px">검사목적 관리에서 먼저 검사목적을 등록하세요.</td></tr>';
  } else {
    _diaryPurposes.forEach(function(p,pi) {
      var pn = p.n || '';
      var pColor = p.color || DIARY_PURPOSE_PALETTE[pi % DIARY_PURPOSE_PALETTE.length].color;
      var pTc = p.textColor || DIARY_PURPOSE_PALETTE[pi % DIARY_PURPOSE_PALETTE.length].textColor;
      var saved = savedPS[pn] || {};
      var amt = saved.amount || '';
      var memo = saved.memo || '';
      ptHtml += '<tr>';
      ptHtml += '<td><span style="background:' + pColor + ';color:' + pTc + ';padding:2px 8px;border-radius:4px;font-size:10px;font-weight:600">' + escHtml(pn) + '</span></td>';
      ptHtml += '<td><input data-uid="' + uid + '" data-pn="' + escHtml(pn) + '" data-field="amount" value="' + amt + '" oninput="onDiaryAmtChange(this)" placeholder="0"></td>';
      ptHtml += '<td><input data-uid="' + uid + '" data-pn="' + escHtml(pn) + '" data-field="memo" value="' + escHtml(memo) + '" style="text-align:left" placeholder="메모"></td>';
      ptHtml += '</tr>';
    });
  }
  ptHtml += '</tbody></table>';
  ptHtml += '<div id="dc-sub-' + uid + '" style="text-align:right;font-size:12px;font-weight:700;color:#1565c0;margin-top:6px"></div>';

  card.innerHTML =
    '<div class="sub-card-hd">' +
      '<span class="sub-card-num' + (isNew?' sub-card-num-new':'') + '" id="dc-num-' + uid + '">' + (idx+1) + '</span>' +
      '<button class="type-btn ' + (isNew?'type-btn-exist':'type-btn-exist-act') + '" onclick="setDiaryCardType(\\'' + uid + '\\',\\'existing\\')">' + '기존 거래처</button>' +
      '<button class="type-btn ' + (isNew?'type-btn-new-act':'type-btn-new') + '" onclick="setDiaryCardType(\\'' + uid + '\\',\\'new\\')">' + '신규 업체</button>' +
      (('<button class="btn-remove" onclick="removeDiaryCard(\\'' + uid + '\\')" style="margin-left:auto">✕</button>') if idx > 0 else '<span style="margin-left:auto"></span>') +
    '</div>' +
    // 소개경로 (신규만)
    '<div id="dc-intro-' + uid + '" style="' + ('' if isNew else 'display:none;') + 'padding:8px 14px;background:#f1f8e9;border:1px solid #c5e1a5;border-radius:8px;margin:8px 14px 0;display:flex;gap:6px;flex-wrap:wrap;align-items:center">' +
      '<span style="font-size:10px;color:#5f6b7a;margin-right:4px">소개경로:</span>' + introHtml +
    '</div>' +
    '<div style="padding:12px 14px">' +
      // 업체명, 주소, 수거방법
      '<div class="fg-row3" style="margin-bottom:8px">' +
        '<div class="fg" style="margin:0">' +
          '<label>업체명 <span class="req">*</span></label>' +
          '<div id="dc-comp-wrap-' + uid + '">' +
            (('<input id="dc-comp-' + uid + '" value="' + escHtml(d.companyName or '') + '" placeholder="신규 업체명 입력" style="padding:7px 10px;border:1px solid #e2e6ed;border-radius:6px;font-size:12px;width:100%">') if isNew else
              ('<select id="dc-comp-' + uid + '" onchange="onDiaryCompanyChange(\\'' + uid + '\\')" style="padding:7px 10px;border:1px solid #e2e6ed;border-radius:6px;font-size:12px;width:100%">' + compOpts + '</select>')
            ) +
          '</div>' +
        '</div>' +
        '<div class="fg" style="margin:0"><label>주소</label>' +
          '<input id="dc-addr-' + uid + '" value="' + escHtml(d.region or '') + '" placeholder="자동" readonly style="background:#f8f9fb;padding:7px 10px;border:1px solid #e2e6ed;border-radius:6px;font-size:12px;width:100%">' +
        '</div>' +
        '<div class="fg" style="margin:0"><label>수거방법</label>' +
          '<select id="dc-method-' + uid + '" style="padding:7px 10px;border:1px solid #e2e6ed;border-radius:6px;font-size:12px;width:100%">' + methodOpts + '</select>' +
        '</div>' +
      '</div>' +
      // 목적별 매출
      '<div style="margin-bottom:8px">' +
        '<label style="font-size:10px;color:#8892a4;display:block;margin-bottom:4px">검사목적별 매출 (부가세 별도)</label>' +
        ptHtml +
      '</div>' +
      // 특이사항
      '<div class="fg" style="margin:0"><label>특이사항</label>' +
        '<textarea id="dc-note-' + uid + '" placeholder="방문/접수 관련 메모" style="min-height:40px;font-size:12px">' + escHtml(d.note or '') + '</textarea>' +
      '</div>' +
    '</div>';

  container.appendChild(card);

  // 주소 자동 로드
  if (!isNew && d.companyName) onDiaryCompanyChange(uid);
  // 소계 갱신
  refreshCardSubtotal(uid);
}
'''

print('ERROR: This approach with Python f-strings for JS is too complex.')
print('Will use a different approach.')
sys.exit(1)
