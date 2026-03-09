/**
 * BFL LIMS 통합 사이드바 (Single Source of Truth)
 * ─────────────────────────────────────────────────
 * 모든 HTML 페이지가 이 파일 하나를 불러옴.
 * 메뉴를 추가/수정할 때 이 파일만 수정하면 전체 반영.
 *
 * 사용법 (각 HTML 파일에서):
 *   <aside class="sidebar" id="sidebar"></aside>
 *   <script src="js/sidebar.js"><\/script>
 *
 * 이 파일이 자동으로 하는 것:
 *   1) 사이드바 CSS 주입 (중복 방지)
 *   2) 로고 + 전체 메뉴 HTML 생성
 *   3) 현재 페이지 감지 → active / expanded 자동 설정
 *   4) salesMgmt.html 등 showPage() 내부 탭 전환 자동 처리
 *   5) toggleMenu() 아코디언 함수 등록
 *
 * 적용 페이지: index.html, salesMgmt.html, sampleReceipt.html,
 *   itemAssign.html, userMgmt.html, inspectionMgmt.html
 */

// ============================================================
// 0. 사이드바 CSS 주입 (한 번만)
// ============================================================
(function injectSidebarCSS() {
  if (document.getElementById('sidebar-unified-css')) return; // 이미 주입됨
  const style = document.createElement('style');
  style.id = 'sidebar-unified-css';
  style.textContent = `
/* ====== UNIFIED SIDEBAR STYLES (injected by sidebar.js) ====== */
.sidebar{width:250px;background:#1a2332;color:white;position:fixed;left:0;top:0;bottom:0;z-index:1000;overflow-y:auto;overflow-x:hidden;display:flex;flex-direction:column;font-family:'Pretendard',-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans KR",sans-serif}
.logo{padding:20px;display:flex;align-items:center;gap:12px;border-bottom:1px solid rgba(255,255,255,0.08);flex-shrink:0}
.logo-icon{width:40px;height:40px;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:20px}
.logo-img{height:36px;width:auto;object-fit:contain;flex-shrink:0}
.logo-text{display:flex;flex-direction:column}
.logo-title{font-size:18px;font-weight:700}
.logo-subtitle{font-size:11px;color:#94a3b8}
.sidebar-nav{flex:1;padding:8px 0;overflow-y:auto}
.nav-group{margin-bottom:2px}
.nav-parent{padding:10px 20px;display:flex;align-items:center;gap:10px;color:#8ea4c0;font-size:13px;font-weight:500;cursor:pointer;text-decoration:none;transition:all 0.15s;border:none;background:none;width:100%}
.nav-parent:hover{background:rgba(255,255,255,0.05);color:#c8d6e5}
.nav-parent.active{color:#4fc3f7;background:rgba(79,195,247,0.1);font-weight:600}
.nav-parent.disabled{color:#4a6785;cursor:default}
.nav-parent.disabled:hover{background:transparent;color:#4a6785}
.nav-icon{font-size:16px;width:22px;text-align:center;flex-shrink:0}
.nav-label{flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.nav-arrow{font-size:10px;color:#5a6a7e;transition:transform 0.2s;margin-left:auto}
.nav-group.expanded .nav-arrow{transform:rotate(180deg)}
.nav-submenu{list-style:none;max-height:0;overflow:hidden;transition:max-height 0.25s ease;margin-left:32px;border-left:2px solid rgba(79,195,247,0.15);padding-left:10px}
.nav-group.expanded .nav-submenu{max-height:600px}
.nav-sub-item{display:block;padding:7px 12px;font-size:12px;color:#6b7d93;text-decoration:none;border-radius:6px;cursor:pointer;transition:all 0.15s;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.nav-sub-item:hover{color:#8ea4c0;background:rgba(255,255,255,0.03)}
.nav-sub-item.active{color:#4fc3f7;font-weight:600;background:rgba(79,195,247,0.08)}
.nav-sub-item.disabled{color:#3d5068;cursor:default}
.nav-sub-item.disabled:hover{background:transparent;color:#3d5068}
/* ── Sidebar Collapse Toggle ── */
.sidebar{transition:width 0.25s ease}
.sidebar-collapse-btn{display:flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:6px;cursor:pointer;color:#e2e8f0;font-size:16px;transition:all .15s;flex-shrink:0;background:rgba(255,255,255,.08);margin-left:auto}
.sidebar-collapse-btn:hover{background:rgba(255,255,255,.12);color:#c8d6e5}
.sidebar.collapsed{width:64px}
.sidebar.collapsed .logo-text{display:none}
.sidebar.collapsed .logo{flex-direction:column;align-items:center;padding:12px 8px;gap:8px}
.sidebar.collapsed .logo-icon{margin:0}
.sidebar.collapsed .logo-img{height:24px}
.sidebar.collapsed .sidebar-collapse-btn{margin:0 auto;transform:rotate(180deg)}
.sidebar.collapsed .nav-label{display:none}
.sidebar.collapsed .nav-arrow{display:none}
.sidebar.collapsed .nav-parent{justify-content:center;padding:10px 0}
.sidebar.collapsed .nav-icon{font-size:18px;width:auto}
.sidebar.collapsed .nav-submenu{display:none!important;max-height:0!important}
.sidebar.collapsed .nav-sub-item{display:none}
.main{transition:margin-left 0.25s ease}
body.sidebar-collapsed .main{margin-left:64px}
@media(max-width:768px){.sidebar{display:none}}
/* ── Sidebar Weather Widget ── */
.sidebar-weather{flex-shrink:0;border-top:1px solid rgba(255,255,255,0.08);padding:14px 20px;background:rgba(0,0,0,0.15)}
.sidebar-weather .weather-main{display:flex;align-items:center;gap:10px}
.sidebar-weather .weather-icon{font-size:24px;line-height:1}
.sidebar-weather .weather-temp{font-size:20px;font-weight:700;color:#e2e8f0}
.sidebar-weather .weather-city{font-size:12px;color:#94a3b8;margin-left:auto}
.sidebar-weather .weather-detail{display:flex;gap:14px;margin-top:6px;font-size:11px;color:#64748b}
.sidebar-weather .weather-detail span{display:flex;align-items:center;gap:3px}
.sidebar-weather .weather-setup{text-align:center;padding:6px 0}
.sidebar-weather .weather-setup a{color:#64748b;font-size:12px;text-decoration:none;transition:color .15s}
.sidebar-weather .weather-setup a:hover{color:#94a3b8}
.sidebar-weather .weather-error{font-size:11px;color:#64748b;text-align:center;padding:4px 0}
.sidebar-weather .weather-loading{font-size:12px;color:#64748b;text-align:center;padding:8px 0}
.sidebar.collapsed .sidebar-weather{padding:8px 4px;text-align:center}
.sidebar.collapsed .sidebar-weather .weather-main{flex-direction:column;gap:2px}
.sidebar.collapsed .sidebar-weather .weather-icon{font-size:18px}
.sidebar.collapsed .sidebar-weather .weather-temp{font-size:13px}
.sidebar.collapsed .sidebar-weather .weather-city{display:none}
.sidebar.collapsed .sidebar-weather .weather-detail{display:none}
.sidebar.collapsed .sidebar-weather .weather-setup a{font-size:10px}
/* ====== END UNIFIED SIDEBAR STYLES ====== */
`;
  document.head.appendChild(style);
})();

// ============================================================
// 1. 메뉴 데이터 (전체 메뉴 정의 — 유일한 정의 장소)
// ============================================================
const SIDEBAR_MENU = [
  {
    id: 'dashboard',
    icon: '📊',
    label: '대시보드',
    href: 'index.html'
  },
  {
    id: 'sales',
    icon: '💼',
    label: '영업 관리',
    sub: [
      { label: '고객사 관리',      href: 'salesMgmt.html',              page: 'customerList', internalPage: 'customerList' },
      { label: '업무일지',          href: 'salesMgmt.html#daily',        page: 'daily',        internalPage: 'daily' },
      { label: '차량일지',          href: 'salesMgmt.html#vehicle',      page: 'vehicle',      internalPage: 'vehicle' },
      { label: '미수금 활동 내역',   href: 'salesMgmt.html#collection',   page: 'collection',   internalPage: 'collection' },
      { label: '거래명세표 관리',    href: 'salesMgmt.html#trade',        page: 'trade',        internalPage: 'trade' },
      { label: '계산서 발행 승인',   href: 'salesMgmt.html#invoice',      page: 'invoice',      internalPage: 'invoice' },
      { label: '업체조회',          href: 'salesMgmt.html#bizSearch',    page: 'bizSearch',    internalPage: 'bizSearch' },
      { label: '긴급 협조',         href: 'salesMgmt.html#urgent',       page: 'urgent',       internalPage: 'urgent' },
      { label: '세금계산서 미발행',   href: 'taxUnissued.html',            page: 'tax-unissued' },
      { label: '영업통계',          disabled: true },
      { label: '영업 설정',         disabled: true },
      { label: 'API 설정',         href: 'salesMgmt.html#apiSettings',  page: 'apiSettings',  internalPage: 'apiSettings' }
    ]
  },
  {
    id: 'reception',
    icon: '📋',
    label: '접수 관리',
    sub: [
      { label: '업체등록·수정',     href: 'companyMgmt.html',  page: 'reception-company' },
      { label: '검사목적 관리',     href: 'inspectionMgmt.html',  page: 'reception-inspection' },
      { label: '접수 등록',         href: 'sampleReceipt.html',   page: 'reception-register' },
      { label: '접수 공지',         href: 'receiptNotice.html',  page: 'reception-notice' },
      { label: '모바일',            href: 'mobilePhoto.html',   page: 'mobile-photo' },
      { label: '접수 현황',         href: 'receiptStatus.html',  page: 'reception-status' },
      { label: '접수대장',          disabled: true },
      { label: '접수 조회/수정',    disabled: true },
      { label: '접수 통계',         disabled: true }
    ]
  },
  {
    id: 'testing',
    icon: '🔬',
    label: '시험 결재',
    sub: [
      { label: '항목배정',          href: 'itemAssign.html',  page: 'testing-assignment' },
      { label: '시험 진행 현황',    disabled: true },
      { label: '결과 입력',         href: 'testResultInput.html',  page: 'testing-result' },
      { label: '시험일지',         href: 'testDiary.html',  page: 'testing-diary' },
      { label: '결재 승인',         disabled: true },
      { label: '시험 이력 조회',    disabled: true },
      { label: '일정관리',          disabled: true },
      { label: '지부관리',          disabled: true },
      { label: '실적보고',          disabled: true },
      { label: 'LIMS 연동',        disabled: true }
    ]
  },
  { id: 'results',       icon: '📄', label: '성적 관리',      disabled: true },
  {
    id: 'finance',
    icon: '💰',
    label: '재무 관리',
    sub: [
      { label: '매출 관리',           disabled: true },
      { label: '입금 관리',           href: 'paymentMgmt.html',    page: 'finance-payment' },
      { label: '세금계산서',          href: 'taxInvoice.html',     page: 'finance-tax' }
    ]
  },
  { id: 'stats',         icon: '📈', label: '통계 분석',      disabled: true },
  { id: 'docs',          icon: '📁', label: '문서 관리',      disabled: true },
  {
    id: 'inventory',
    icon: '🧪',
    label: '재고/시약 관리',
    sub: [
      { label: '재고/시약 관리', href: 'inventoryMgmt.html', page: 'inventory-main' }
    ]
  },
  { id: 'notice',        icon: '📢', label: '공지',           disabled: true },
  {
    id: 'admin',
    icon: '🔧',
    label: '관리자',
    sub: [
      { label: '사용자 관리',       href: 'userMgmt.html',              page: 'admin-users' },
      { label: '부서 관리',         disabled: true },
      { label: '팀 관리',           disabled: true },
      { label: '권한 설정',         disabled: true },
      { label: '기타 설정',         href: 'adminSettings.html',         page: 'admin-settings' },
      { label: '대시보드 권한',     disabled: true },
      { label: '알림 설정',         disabled: true },
      { label: '시스템 로그',       disabled: true },
      { label: 'API 수집 설정',    href: 'admin_api_settings.html',    page: 'admin-api-settings' },
      { label: '수집 현황',         href: 'admin_collect_status.html',  page: 'admin-collect-status' }
    ]
  }
];

// ============================================================
// 2. 사이드바 HTML 렌더링
// ============================================================
function renderSidebar() {
  const sidebar = document.getElementById('sidebar');
  if (!sidebar) return;

  // 현재 페이지 파일명 감지
  const currentFile = decodeURIComponent(location.pathname.split('/').pop()) || 'index.html';
  // salesMgmt.html 등 내부 탭 전환 함수 존재 여부
  const hasShowPage = typeof window.showPage === 'function';

  // 로고 + 접기 버튼
  let html = `
  <div class="logo">
    <img src="img/bfl_logo.svg?v=3" alt="BFL" class="logo-img">
    <div class="sidebar-collapse-btn" onclick="toggleSidebar()" title="사이드바 접기/펼치기">☰</div>
  </div>
  <nav class="sidebar-nav">`;

  SIDEBAR_MENU.forEach(group => {
    // 서브메뉴가 없는 단일 항목
    if (!group.sub) {
      if (group.disabled) {
        html += `
    <div class="nav-group">
      <span class="nav-parent disabled" data-id="${group.id}">
        <span class="nav-icon">${group.icon}</span>
        <span class="nav-label">${group.label}</span>
      </span>
    </div>`;
      } else {
        // 대시보드 같은 단일 링크
        const isActive = (group.href === currentFile || (currentFile === '' && group.href === 'index.html'));
        html += `
    <div class="nav-group">
      <a href="${group.href}" class="nav-parent${isActive ? ' active' : ''}" data-id="${group.id}">
        <span class="nav-icon">${group.icon}</span>
        <span class="nav-label">${group.label}</span>
      </a>
    </div>`;
      }
      return;
    }

    // 서브메뉴가 있는 그룹
    let groupHasActive = false;
    const subHtmlArr = group.sub.map(item => {
      if (item.disabled) {
        return `        <li><span class="nav-sub-item disabled">${item.label}</span></li>`;
      }

      // 링크 결정: 같은 페이지에서 showPage가 있으면 내부 탭 전환
      const targetFile = item.href.split('#')[0];
      const isSamePage = (targetFile === currentFile);
      const useInternal = isSamePage && hasShowPage && item.internalPage;

      let linkHref, linkOnclick;
      if (useInternal) {
        linkHref = 'javascript:void(0)';
        linkOnclick = ` onclick="showPage('${item.internalPage}')"`;
      } else {
        linkHref = item.href;
        linkOnclick = '';
      }

      // active 판별
      const hrefBase = item.href.split('#')[0];
      const isActive = (hrefBase === currentFile);
      if (isActive) groupHasActive = true;

      return `        <li><a href="${linkHref}" class="nav-sub-item${isActive ? ' active' : ''}" data-page="${item.page || ''}"${linkOnclick}>${item.label}</a></li>`;
    });

    html += `
    <div class="nav-group${groupHasActive ? ' expanded' : ''}">
      <div class="nav-parent${groupHasActive ? ' active' : ''}" data-id="${group.id}" onclick="toggleMenu(this)">
        <span class="nav-icon">${group.icon}</span>
        <span class="nav-label">${group.label}</span>
        <span class="nav-arrow">▾</span>
      </div>
      <ul class="nav-submenu">
${subHtmlArr.join('\n')}
      </ul>
    </div>`;
  });

  html += `
  </nav>
  <div class="sidebar-weather" id="sidebar-weather">
    <div class="weather-loading">🌤️ 날씨 로딩...</div>
  </div>`;

  sidebar.innerHTML = html;
}

// ============================================================
// 3. 토글 메뉴 (아코디언)
// ============================================================
function toggleMenu(el) {
  const group = el.closest('.nav-group');
  const wasExpanded = group.classList.contains('expanded');
  // 다른 그룹 닫기
  document.querySelectorAll('.nav-group.expanded').forEach(g => {
    if (g !== group) g.classList.remove('expanded');
  });
  group.classList.toggle('expanded', !wasExpanded);
}

// ============================================================
// 3-1. 사이드바 접기/펼치기
// ============================================================
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  if (!sidebar) return;
  const isCollapsed = sidebar.classList.toggle('collapsed');
  document.body.classList.toggle('sidebar-collapsed', isCollapsed);
  // localStorage에 상태 저장
  try { localStorage.setItem('bfl_sidebar_collapsed', isCollapsed ? '1' : '0'); } catch(e) {}
}

function _restoreSidebarState() {
  try {
    if (localStorage.getItem('bfl_sidebar_collapsed') === '1') {
      const sidebar = document.getElementById('sidebar');
      if (sidebar) {
        sidebar.classList.add('collapsed');
        document.body.classList.add('sidebar-collapsed');
      }
    }
  } catch(e) {}
}

// ============================================================
// 4. 사이드바 날씨 위젯
// ============================================================
var _weatherRefreshTimer = null;

function _getWeatherBaseTime() {
  var now = new Date();
  var h = now.getHours();
  var m = now.getMinutes();
  if (m < 40) h = h - 1;
  if (h < 0) h = 23;
  return String(h).padStart(2, '0') + '00';
}

function _getWeatherBaseDate(bt) {
  var now = new Date();
  if (bt === '2300' && now.getHours() < 1) {
    now.setDate(now.getDate() - 1);
  }
  var y = now.getFullYear();
  var mo = String(now.getMonth() + 1).padStart(2, '0');
  var d = String(now.getDate()).padStart(2, '0');
  return y + mo + d;
}

function _getWeatherIcon(pty) {
  var p = parseInt(pty) || 0;
  if (p === 1) return '🌧️';
  if (p === 2) return '🌨️';
  if (p === 3) return '❄️';
  if (p === 5) return '💧';
  if (p === 6) return '💧';
  if (p === 7) return '🌨️';
  var h = new Date().getHours();
  return (h >= 6 && h < 18) ? '☀️' : '🌙';
}

function _renderWeatherWidget(data) {
  var el = document.getElementById('sidebar-weather');
  if (!el) return;
  if (!data) {
    el.innerHTML = '<div class="weather-setup"><a href="adminSettings.html" title="날씨 설정">⚙️ 날씨 설정</a></div>';
    return;
  }
  if (data.error) {
    el.innerHTML = '<div class="weather-error">' + data.error + '</div>';
    return;
  }
  var icon = _getWeatherIcon(data.pty);
  el.innerHTML =
    '<div class="weather-main">' +
      '<span class="weather-icon">' + icon + '</span>' +
      '<span class="weather-temp">' + data.temp + '°</span>' +
      '<span class="weather-city">' + (data.city || '') + '</span>' +
    '</div>' +
    '<div class="weather-detail">' +
      '<span>💧 ' + data.hum + '%</span>' +
      '<span>🌬️ ' + data.wind + 'm/s</span>' +
    '</div>';
}

async function loadSidebarWeather() {
  var el = document.getElementById('sidebar-weather');
  if (!el) return;

  // 1. 캐시 확인 (30분)
  try {
    var cached = localStorage.getItem('bfl_weather_cache');
    if (cached) {
      var cache = JSON.parse(cached);
      var age = Date.now() - (cache.ts || 0);
      if (age < 30 * 60 * 1000) {
        _renderWeatherWidget(cache.data);
        // 30분 후 자동 갱신 타이머
        if (_weatherRefreshTimer) clearTimeout(_weatherRefreshTimer);
        _weatherRefreshTimer = setTimeout(loadSidebarWeather, 30 * 60 * 1000 - age);
        return;
      }
    }
  } catch(e) {}

  // 2. Firestore에서 설정 로드
  var settings = null;
  try {
    if (typeof waitForFirebase === 'function') await waitForFirebase();
    if (typeof fsGetSettings === 'function') {
      settings = await fsGetSettings('weatherSettings');
    }
  } catch(e) {
    console.warn('[sidebar-weather] Firestore 설정 로드 실패:', e.message);
  }

  if (!settings || !settings.apiKey || !settings.nx) {
    _renderWeatherWidget(null); // "설정 필요" 표시
    return;
  }

  // 3. 기상청 API 호출
  var bt = _getWeatherBaseTime();
  var bd = _getWeatherBaseDate(bt);
  var url = 'https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst'
    + '?serviceKey=' + settings.apiKey
    + '&dataType=JSON&numOfRows=10&pageNo=1'
    + '&base_date=' + bd
    + '&base_time=' + bt
    + '&nx=' + settings.nx + '&ny=' + settings.ny;

  try {
    var resp = await fetch(url);
    var text = await resp.text();
    var json;
    try { json = JSON.parse(text); } catch(pe) {
      console.warn('[sidebar-weather] 응답 파싱 실패:', text.substring(0, 100));
      _renderWeatherWidget({ error: '인증키 확인 필요' });
      return;
    }

    if (json.response && json.response.header && json.response.header.resultCode === '00') {
      var items = json.response.body.items.item;
      var vals = {};
      items.forEach(function(it) { vals[it.category] = it.obsrValue; });

      var weatherData = {
        temp: vals.T1H || '-',
        hum: vals.REH || '-',
        wind: vals.WSD || '-',
        pty: vals.PTY || '0',
        city: settings.city || ''
      };

      _renderWeatherWidget(weatherData);

      // 캐시 저장
      try {
        localStorage.setItem('bfl_weather_cache', JSON.stringify({
          ts: Date.now(),
          data: weatherData
        }));
      } catch(e) {}

      // 30분 후 갱신 타이머
      if (_weatherRefreshTimer) clearTimeout(_weatherRefreshTimer);
      _weatherRefreshTimer = setTimeout(loadSidebarWeather, 30 * 60 * 1000);
    } else {
      var errMsg = (json.response && json.response.header) ? json.response.header.resultMsg : '';
      console.warn('[sidebar-weather] API 오류:', errMsg);
      _renderWeatherWidget({ error: '날씨 로드 실패' });
    }
  } catch(e) {
    console.warn('[sidebar-weather] 요청 실패:', e.message);
    // 캐시 데이터가 있으면 만료되어도 표시
    try {
      var old = localStorage.getItem('bfl_weather_cache');
      if (old) {
        _renderWeatherWidget(JSON.parse(old).data);
        return;
      }
    } catch(ex) {}
    _renderWeatherWidget({ error: '날씨 로드 실패' });
  }
}

// ============================================================
// 5. 초기화 — DOM 준비 후 실행
// ============================================================
(function initSidebar() {
  function _init() {
    renderSidebar();
    _restoreSidebarState();
    // 날씨 위젯 로드 (Firebase 준비 후)
    if (typeof waitForFirebase === 'function') {
      loadSidebarWeather();
    } else {
      // firebase-init.js 미로드 시 firebase-ready 이벤트 대기
      window.addEventListener('firebase-ready', function() {
        loadSidebarWeather();
      });
    }
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', _init);
  } else {
    _init();
  }
})();
