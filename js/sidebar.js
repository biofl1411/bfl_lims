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
.logo-link{display:flex;align-items:center;text-decoration:none}
.logo-img{height:36px;width:auto;object-fit:contain;flex-shrink:0}
.logo-text{display:flex;flex-direction:column}
.logo-title{font-size:18px;font-weight:700}
.logo-subtitle{font-size:11px;color:#94a3b8}
.sidebar-nav{flex:1;padding:8px 0;overflow-y:auto}
.nav-group{margin-bottom:2px}
.nav-parent{padding:10px 20px;display:flex;align-items:center;gap:10px;color:#b0c4de;font-size:15px;font-weight:500;cursor:pointer;text-decoration:none;transition:all 0.15s;border:none;background:none;width:100%}
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
.nav-sub-item{display:block;padding:7px 12px;font-size:14px;color:#94a8be;text-decoration:none;border-radius:6px;cursor:pointer;transition:all 0.15s;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
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

.main,.main-container,.main-wrapper{transition:margin-left 0.25s ease}
body.sidebar-collapsed .main,
body.sidebar-collapsed .main-container,
body.sidebar-collapsed .main-wrapper{margin-left:64px}
@media(max-width:768px){.sidebar{display:none}}
/* ── Sidebar Widget Bar (날씨 위 아이콘 바) ── */
.sidebar-widgets{flex-shrink:0;border-top:1px solid rgba(255,255,255,0.08);padding:8px 20px;display:flex;gap:8px;justify-content:center}
.sidebar-widgets .sw-btn{width:40px;height:40px;border-radius:10px;border:none;cursor:pointer;font-size:18px;display:flex;align-items:center;justify-content:center;transition:all .15s;background:rgba(255,255,255,0.06);color:#94a3b8}
.sidebar-widgets .sw-btn:hover{background:rgba(255,255,255,0.12);color:#e2e8f0;transform:scale(1.08)}
.sidebar-widgets .sw-btn.active{background:rgba(79,195,247,0.2);color:#4fc3f7;box-shadow:0 0 8px rgba(79,195,247,0.3)}
.sidebar.collapsed .sidebar-widgets{padding:6px 4px;flex-wrap:wrap;gap:4px}
.sidebar.collapsed .sidebar-widgets .sw-btn{width:32px;height:32px;font-size:14px;border-radius:8px}

/* ── 계산기 (드래그 가능 팝업) ── */
.calc-popup{position:fixed;z-index:99999;width:320px;background:#1e293b;border-radius:16px;box-shadow:0 20px 60px rgba(0,0,0,0.5),0 0 1px rgba(255,255,255,0.1);color:#e2e8f0;display:none;overflow:hidden;resize:none;user-select:none}
.calc-popup.visible{display:block}
.calc-titlebar{padding:10px 14px;background:linear-gradient(135deg,#334155,#1e293b);cursor:move;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid rgba(255,255,255,0.08)}
.calc-titlebar span{font-size:13px;font-weight:600}
.calc-titlebar button{background:none;border:none;color:#94a3b8;font-size:16px;cursor:pointer;padding:2px 6px;border-radius:4px}
.calc-titlebar button:hover{color:#ef4444;background:rgba(239,68,68,0.15)}
.calc-display{padding:12px 14px;background:#0f172a;font-family:'JetBrains Mono',monospace;text-align:right}
.calc-display .calc-expr{font-size:11px;color:#64748b;min-height:16px;word-break:break-all}
.calc-display .calc-val{font-size:28px;font-weight:700;color:#f1f5f9;overflow-x:auto;white-space:nowrap}
.calc-btns{display:grid;grid-template-columns:repeat(4,1fr);gap:2px;padding:6px}
.calc-btns button{padding:14px 0;border:none;border-radius:8px;font-size:16px;font-weight:600;cursor:pointer;transition:all .1s}
.calc-btns .cb-num{background:#334155;color:#e2e8f0}
.calc-btns .cb-num:hover{background:#475569}
.calc-btns .cb-op{background:#1e40af;color:#93c5fd}
.calc-btns .cb-op:hover{background:#2563eb}
.calc-btns .cb-fn{background:rgba(255,255,255,0.05);color:#94a3b8}
.calc-btns .cb-fn:hover{background:rgba(255,255,255,0.1)}
.calc-btns .cb-eq{background:#059669;color:white}
.calc-btns .cb-eq:hover{background:#10b981}
.calc-btns .cb-eq.span2{grid-column:span 2}
.calc-memory{display:flex;gap:2px;padding:0 6px 4px}
.calc-memory button{flex:1;padding:4px 0;border:none;border-radius:4px;font-size:10px;font-weight:600;cursor:pointer;background:rgba(255,255,255,0.04);color:#64748b;transition:all .1s}
.calc-memory button:hover{background:rgba(255,255,255,0.1);color:#94a3b8}
.calc-history{max-height:0;overflow:hidden;transition:max-height .25s ease;background:#0f172a;border-top:1px solid rgba(255,255,255,0.06)}
.calc-history.open{max-height:160px}
.calc-history-inner{max-height:152px;overflow-y:auto;padding:4px 8px}
.calc-history-inner::-webkit-scrollbar{width:4px}
.calc-history-inner::-webkit-scrollbar-thumb{background:#334155;border-radius:2px}
.calc-history-row{display:flex;justify-content:space-between;align-items:center;padding:3px 4px;border-bottom:1px solid rgba(255,255,255,0.04);font-family:'JetBrains Mono',monospace;font-size:10px}
.calc-history-row .ch-expr{color:#64748b;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.calc-history-row .ch-result{color:#4fc3f7;font-weight:700;margin-left:8px;white-space:nowrap}
.calc-history-toggle{display:flex;justify-content:center;padding:2px;background:rgba(255,255,255,0.03);border-top:1px solid rgba(255,255,255,0.06);cursor:pointer}
.calc-history-toggle:hover{background:rgba(255,255,255,0.06)}
.calc-history-toggle span{font-size:9px;color:#475569;transition:transform .2s}
.calc-history.open + .calc-history-toggle span{transform:rotate(180deg)}

/* ── 단위변환 팝업 ── */
.unit-popup{position:fixed;z-index:99999;width:340px;background:#1e293b;border-radius:16px;box-shadow:0 20px 60px rgba(0,0,0,0.5),0 0 1px rgba(255,255,255,0.1);color:#e2e8f0;display:none;overflow:hidden;user-select:none}
.unit-popup.visible{display:block}
.unit-titlebar{padding:10px 14px;background:linear-gradient(135deg,#334155,#1e293b);cursor:move;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid rgba(255,255,255,0.08)}
.unit-titlebar span{font-size:13px;font-weight:600}
.unit-titlebar button{background:none;border:none;color:#94a3b8;font-size:16px;cursor:pointer;padding:2px 6px;border-radius:4px}
.unit-titlebar button:hover{color:#ef4444;background:rgba(239,68,68,0.15)}
.unit-tabs{display:flex;border-bottom:1px solid rgba(255,255,255,0.08);padding:0 6px}
.unit-tabs button{flex:1;padding:8px 0;border:none;background:none;color:#64748b;font-size:11px;font-weight:600;cursor:pointer;border-bottom:2px solid transparent;transition:all .15s}
.unit-tabs button:hover{color:#94a3b8}
.unit-tabs button.active{color:#4fc3f7;border-bottom-color:#4fc3f7}
.unit-body{padding:14px}
.unit-body label{font-size:11px;color:#94a3b8;display:block;margin-bottom:4px}
.unit-body input,.unit-body select{width:100%;padding:8px 10px;border:1px solid #334155;border-radius:8px;background:#0f172a;color:#e2e8f0;font-size:14px;font-family:'JetBrains Mono',monospace;outline:none;transition:border-color .15s}
.unit-body input:focus{border-color:#4fc3f7}
.unit-body .unit-result{background:#0f172a;border:1px solid #334155;border-radius:8px;padding:10px;margin-top:8px;font-family:'JetBrains Mono',monospace;font-size:14px;color:#4fc3f7;min-height:40px;display:flex;flex-direction:column;gap:4px}
.unit-body .unit-result .ur-row{display:flex;justify-content:space-between;align-items:center}
.unit-body .unit-result .ur-label{font-size:10px;color:#64748b}
.unit-body .unit-result .ur-val{font-weight:700}
.unit-body .unit-swap{display:flex;justify-content:center;margin:8px 0}
.unit-body .unit-swap button{background:rgba(79,195,247,0.1);border:1px solid rgba(79,195,247,0.2);border-radius:50%;width:32px;height:32px;font-size:14px;cursor:pointer;color:#4fc3f7;transition:all .15s}
.unit-body .unit-swap button:hover{background:rgba(79,195,247,0.2);transform:rotate(180deg)}
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
/* ── subTabs (페이지 상단 탭 바) ── */
.sidebar-subtabs{display:flex;background:#fff;border-bottom:1px solid #e2e6ed;padding:0 24px;position:sticky;top:0;z-index:90}
.sidebar-subtab{padding:6px 16px;font-size:13px;font-weight:500;color:#5f6b7a;cursor:pointer;border:none;border-bottom:2px solid transparent;background:none;font-family:inherit;transition:all .15s}
.sidebar-subtab:hover{color:#1a2332;background:#f8f9fb}
.sidebar-subtab.active{border-bottom:2px solid #1a73e8;color:#1a73e8;font-weight:600}
body.sidebar-collapsed .sidebar-subtabs{margin-left:0}
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
      { label: '업체조회',          href: 'salesMgmt.html#bizSearch',    page: 'bizSearch',    internalPage: 'bizSearch' },
      { label: '긴급 협조',         href: 'salesMgmt.html#urgent',       page: 'urgent',       internalPage: 'urgent' },
      { label: '영업통계',          disabled: true },
      { label: '영업 설정',         disabled: true }
    ]
  },
  {
    id: 'reception',
    icon: '📋',
    label: '접수 관리',
    sub: [
      { label: '업체등록·수정',     href: 'companyMgmt.html',  page: 'reception-company' },
      { label: '검사목적 관리',     href: 'inspectionMgmt.html',  page: 'reception-inspection' },
      { label: '접수 등록',         href: 'sampleReceiptV2.html',   page: 'reception-register' },
      { label: '접수 현황',         href: 'receiptStatus.html',  page: 'reception-status' },
      { label: '실적보고',          disabled: true },
      { label: '지부관리',          disabled: true },
      { label: '설정',              href: 'receiptSettings.html',  page: 'reception-settings' }
    ]
  },
  {
    id: 'testing',
    icon: '🔬',
    label: '시험 결재',
    sub: [
      { label: '시험 진행 현황',    href: 'testResultInput.html',  page: 'testing-progress',
        tabGroup: 'testProgress',
        pageTabs: [
          { label: '결과 입력', href: 'testResultInput.html' },
          { label: '시험일지',  href: 'testDiary.html?from=progress' },
          { label: '결재 승인', disabled: true }
        ]
      },
      { label: '시험 이력 조회',    disabled: true },
      { label: '일정관리',          disabled: true },
      { label: '설정',              href: 'itemAssign.html',  page: 'testing-settings',
        tabGroup: 'testSettings',
        pageTabs: [
          { label: '항목배정', href: 'itemAssign.html' },
          { label: '시험 결재', href: 'approvalSettings.html' }
        ]
      },
      { label: '기록서 양식 수집',  href: 'formCollector.html',  page: 'testing-formCollector' }
    ]
  },
  { id: 'results',       icon: '📄', label: '성적 관리',      disabled: true },
  {
    id: 'finance',
    icon: '💰',
    label: '재무 관리',
    sub: [
      { label: '매출처원장',           href: 'ledgerMgmt.html',  page: 'finance-ledger' },
      { label: '입금 관리',           href: 'paymentMgmt.html',    page: 'finance-payment' },
      { label: '세금계산서',          href: 'taxInvoice.html',     page: 'finance-tax' },
      { label: '입금 통계',           href: 'paymentStats.html',   page: 'finance-stats' }
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
      { label: 'API 설정(영업부용)', href: 'salesMgmt.html#apiSettings',  page: 'apiSettings',  internalPage: 'apiSettings' },
      { label: 'API 수집 설정',    href: 'admin_api_settings.html',    page: 'admin-api-settings' },
      { label: '수집 현황',         href: 'admin_collect_status.html',  page: 'admin-collect-status' },
      { label: '신규 업체 알림',    href: 'admin_new_businesses.html',  page: 'admin-new-biz' }
    ]
  }
];

// 헬퍼: 특정 파일+hash 조합이 메뉴에서 hash 매칭되는 항목이 있는지 확인
function _hasHashMatchInMenu(file, hash) {
  if (!hash) return false;
  for (var i = 0; i < SIDEBAR_MENU.length; i++) {
    var group = SIDEBAR_MENU[i];
    if (!group.sub) continue;
    for (var j = 0; j < group.sub.length; j++) {
      var item = group.sub[j];
      if (!item.href) continue;
      var hBase = item.href.split('#')[0];
      var hHash = item.href.split('#')[1] || '';
      if (hBase === file && hHash === hash) return true;
      if (hBase === file && item.subTabs) {
        for (var k = 0; k < item.subTabs.length; k++) {
          if (item.subTabs[k].tab === hash) return true;
        }
      }
    }
  }
  return false;
}

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
    <a href="index.html" class="logo-link" title="대시보드로 이동"><img src="img/bfl_logo.svg?v=3" alt="BFL" class="logo-img"></a>
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
        if (item.dailyTab) {
          linkOnclick = ` onclick="showPage('${item.internalPage}');setTimeout(function(){var b=document.querySelector('[data-tab=${item.dailyTab}]');if(b)switchDailyTab(b);},50)"`;
        } else {
          linkOnclick = ` onclick="showPage('${item.internalPage}')"`;
        }
      } else {
        linkHref = item.href;
        linkOnclick = '';
      }

      // active 판별 (hash 고려 — salesMgmt.html이 영업관리/재무관리 양쪽에 있으므로)
      const hrefBase = item.href.split('#')[0];
      const hrefHash = item.href.split('#')[1] || '';
      const currentHash = location.hash.replace('#', '') || '';
      let isActive = false;

      // pageTabs가 있으면 해당 페이지들도 이 메뉴로 인식
      if (item.pageTabs) {
        var _curSearch = location.search || '';
        var _curFrom = '';
        try { _curFrom = (new URLSearchParams(_curSearch)).get('from') || ''; } catch(e) {}
        isActive = item.pageTabs.some(function(pt) {
          var ptFile = (pt.href || '').split('?')[0];
          if (ptFile !== currentFile) return false;
          var ptFrom = '';
          if (pt.href && pt.href.indexOf('from=') !== -1) {
            try { ptFrom = (new URLSearchParams(pt.href.split('?')[1])).get('from') || ''; } catch(e) {}
          }
          if (ptFrom && _curFrom) return ptFrom === _curFrom;
          if (!ptFrom && !_curFrom) return true;
          return false;
        });
      } else if (hrefBase === currentFile) {
        if (hrefHash) {
          // href에 hash가 있으면 hash까지 일치해야 active
          // subTabs가 있으면 해당 탭들도 같은 메뉴로 인식
          if (currentHash === hrefHash) {
            isActive = true;
          } else if (item.subTabs) {
            var tabNames = item.subTabs.map(function(t) { return t.tab; });
            if (tabNames.indexOf(currentHash) !== -1) {
              isActive = true;
            }
          }
        } else if (!currentHash || !_hasHashMatchInMenu(currentFile, currentHash)) {
          // href에 hash가 없고, 현재 URL에 hash가 없거나 다른 메뉴에서 매칭되지 않을 때
          isActive = true;
        }
      }
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
  <div class="sidebar-widgets" id="sidebar-widgets">
    <button class="sw-btn" onclick="toggleCalcPopup()" title="계산기">🧮</button>
    <button class="sw-btn" onclick="toggleUnitPopup()" title="단위변환">📐</button>
    <button class="sw-btn" onclick="window.open('https://192.168.0.96:8443/adminSettings.html','_blank')" title="설정">⚙️</button>
    <button class="sw-btn" onclick="toggleSidebarCollapse()" title="사이드바 접기/펼치기">📌</button>
  </div>
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
// 3-2. subTabs 렌더링 (메뉴 항목에 subTabs가 있을 때 페이지 상단에 탭 바 표시)
// ============================================================
function _renderSubTabs() {
  var currentFile = decodeURIComponent(location.pathname.split('/').pop()) || 'index.html';
  var currentHash = location.hash.replace('#', '') || '';

  // ── A. pageTabs (페이지 간 탭 네비게이션) ──
  var currentSearch = location.search || '';
  var currentFrom = (new URLSearchParams(currentSearch)).get('from') || '';
  var activePageTabItem = null;
  SIDEBAR_MENU.forEach(function(group) {
    if (!group.sub) return;
    group.sub.forEach(function(item) {
      if (!item.pageTabs || !item.pageTabs.length || item.disabled) return;
      var match = item.pageTabs.some(function(pt) {
        var ptFile = (pt.href || '').split('?')[0];
        var ptFrom = '';
        if (pt.href && pt.href.indexOf('from=') !== -1) {
          try { ptFrom = (new URLSearchParams(pt.href.split('?')[1])).get('from') || ''; } catch(e) {}
        }
        // 파일명 일치 확인
        if (ptFile !== currentFile) return false;
        // from 파라미터가 있는 경우 정확히 일치해야 함
        if (ptFrom && currentFrom) return ptFrom === currentFrom;
        // from 파라미터가 없으면 기본 매칭
        if (!currentFrom && !ptFrom) return true;
        // 현재 URL에 from이 없고 pageTabs에 from이 있는 경우 → 불일치
        if (!currentFrom && ptFrom) return false;
        // 현재 URL에 from이 있고 pageTabs에 from이 없는 경우 → 불일치
        return false;
      });
      if (match) activePageTabItem = item;
    });
  });

  if (activePageTabItem && activePageTabItem.pageTabs) {
    var tabBar = document.createElement('div');
    tabBar.className = 'sidebar-subtabs';
    tabBar.id = 'sidebar-subtabs';

    activePageTabItem.pageTabs.forEach(function(pt) {
      if (pt.disabled) {
        var span = document.createElement('span');
        span.className = 'sidebar-subtab disabled';
        span.textContent = pt.label;
        span.style.color = '#c0c8d0';
        span.style.cursor = 'default';
        tabBar.appendChild(span);
        return;
      }
      var ptFile = (pt.href || '').split('?')[0];
      var isActiveTab = (ptFile === currentFile);
      var btn = document.createElement('a');
      btn.className = 'sidebar-subtab' + (isActiveTab ? ' active' : '');
      btn.textContent = pt.label;
      btn.href = pt.href;
      btn.style.textDecoration = 'none';
      tabBar.appendChild(btn);
    });

    // top-header 바로 아래에 삽입
    var topHeader = document.querySelector('.top-header');
    if (topHeader && topHeader.nextSibling) {
      topHeader.parentNode.insertBefore(tabBar, topHeader.nextSibling);
    } else if (topHeader) {
      topHeader.parentNode.appendChild(tabBar);
    } else {
      var mainEl = document.querySelector('.main-container') || document.querySelector('.main') || document.querySelector('.main-wrapper');
      if (mainEl) mainEl.insertBefore(tabBar, mainEl.firstChild);
    }
    return; // pageTabs가 있으면 subTabs는 무시
  }

  // ── B. subTabs (같은 페이지 내 hash 탭 전환) ──
  var activeSubTabs = null;
  SIDEBAR_MENU.forEach(function(group) {
    if (!group.sub) return;
    group.sub.forEach(function(item) {
      if (!item.subTabs || !item.subTabs.length || item.disabled) return;
      var itemHref = item.href || '';
      var hrefBase = itemHref.split('#')[0];
      var hrefHash = itemHref.split('#')[1] || '';
      if (hrefBase !== currentFile) return;
      var tabNames = item.subTabs.map(function(t) { return t.tab; });
      var isCurrentPage = false;
      if (currentHash && tabNames.indexOf(currentHash) !== -1) {
        isCurrentPage = true;
      } else if (hrefHash && currentHash === hrefHash) {
        isCurrentPage = true;
      }
      if (isCurrentPage) activeSubTabs = item;
    });
  });

  if (!activeSubTabs || !activeSubTabs.subTabs || !activeSubTabs.subTabs.length) return;

  var activeTab = currentHash || activeSubTabs.subTabs[0].tab;

  var tabBar = document.createElement('div');
  tabBar.className = 'sidebar-subtabs';
  tabBar.id = 'sidebar-subtabs';

  activeSubTabs.subTabs.forEach(function(t) {
    var btn = document.createElement('button');
    btn.className = 'sidebar-subtab' + (t.tab === activeTab ? ' active' : '');
    btn.textContent = t.label;
    btn.setAttribute('data-subtab', t.tab);
    btn.onclick = function() {
      tabBar.querySelectorAll('.sidebar-subtab').forEach(function(b) { b.classList.remove('active'); });
      btn.classList.add('active');
      try { localStorage.setItem('salesMgmt_activeTab', t.tab); } catch(e) {}
      history.replaceState(null, '', currentFile + '#' + t.tab);
      window.dispatchEvent(new CustomEvent('subtab-change', { detail: { tab: t.tab } }));
      if (typeof window.switchSubTab === 'function') {
        window.switchSubTab(t.tab);
      }
    };
    tabBar.appendChild(btn);
  });

  var topbar = document.querySelector('.topbar');
  if (topbar && topbar.nextSibling) {
    topbar.parentNode.insertBefore(tabBar, topbar.nextSibling);
  } else if (topbar) {
    topbar.parentNode.appendChild(tabBar);
  } else {
    var mainEl = document.querySelector('.main') || document.querySelector('.main-wrapper');
    if (mainEl) mainEl.insertBefore(tabBar, mainEl.firstChild);
  }

  try { localStorage.setItem('salesMgmt_activeTab', activeTab); } catch(e) {}
  window.dispatchEvent(new CustomEvent('subtab-change', { detail: { tab: activeTab } }));
  if (typeof window.switchSubTab === 'function') {
    window.switchSubTab(activeTab);
  }
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
    _renderSubTabs();
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

// ============================================================
// 6. 계산기 위젯 (별도 팝업 윈도우 — 듀얼 모니터 이동 가능)
// ============================================================
(function() {
  var _calcWindows = [];
  var _calcCount = 0;

  function _calcHTML(id) {
    return '<!DOCTYPE html><html><head><meta charset="UTF-8"><title>🧮 계산기 #' + id + '</title><style>' +
      '*{margin:0;padding:0;box-sizing:border-box}' +
      'body{background:#1e293b;color:#e2e8f0;font-family:"Pretendard",-apple-system,"Segoe UI","Noto Sans KR",sans-serif;overflow:hidden;user-select:none}' +
      '.disp{padding:12px 14px;background:#0f172a}' +
      '.disp .expr{font-size:12px;color:#64748b;min-height:18px;word-break:break-all;font-family:"JetBrains Mono",monospace;text-align:right}' +
      '.disp .val{font-size:32px;font-weight:700;color:#f1f5f9;text-align:right;overflow-x:auto;white-space:nowrap;font-family:"JetBrains Mono",monospace}' +
      '.hist{max-height:0;overflow:hidden;transition:max-height .25s;background:#0f172a;border-top:1px solid rgba(255,255,255,0.06)}' +
      '.hist.open{max-height:140px}' +
      '.hist-inner{max-height:132px;overflow-y:auto;padding:4px 8px}' +
      '.hist-inner::-webkit-scrollbar{width:4px}.hist-inner::-webkit-scrollbar-thumb{background:#334155;border-radius:2px}' +
      '.hr{display:flex;justify-content:space-between;padding:3px 4px;border-bottom:1px solid rgba(255,255,255,0.04);font-family:"JetBrains Mono",monospace;font-size:11px}' +
      '.hr .he{color:#64748b;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}' +
      '.hr .hv{color:#4fc3f7;font-weight:700;margin-left:8px;white-space:nowrap}' +
      '.htog{text-align:center;padding:3px;background:rgba(255,255,255,0.03);border-top:1px solid rgba(255,255,255,0.06);cursor:pointer;font-size:10px;color:#475569}' +
      '.htog:hover{background:rgba(255,255,255,0.06)}' +
      '.mem{display:flex;gap:2px;padding:2px 6px}' +
      '.mem button{flex:1;padding:5px 0;border:none;border-radius:4px;font-size:11px;font-weight:600;cursor:pointer;background:rgba(255,255,255,0.04);color:#64748b}' +
      '.mem button:hover{background:rgba(255,255,255,0.1);color:#94a3b8}' +
      '.btns{display:grid;grid-template-columns:repeat(4,1fr);gap:2px;padding:4px 6px 6px}' +
      '.btns button{padding:16px 0;border:none;border-radius:8px;font-size:18px;font-weight:600;cursor:pointer;transition:all .1s}' +
      '.bn{background:#334155;color:#e2e8f0}.bn:hover{background:#475569}' +
      '.bo{background:#1e40af;color:#93c5fd}.bo:hover{background:#2563eb}' +
      '.bf{background:rgba(255,255,255,0.05);color:#94a3b8}.bf:hover{background:rgba(255,255,255,0.1)}' +
      '.be{background:#059669;color:white}.be:hover{background:#10b981}' +
      '</style></head><body>' +
      '<div class="disp"><div class="expr" id="expr"></div><div class="val" id="val">0</div></div>' +
      '<div class="hist" id="hist"><div class="hist-inner" id="hlist"></div></div>' +
      '<div class="htog" id="htog">▼ 이력</div>' +
      '<div class="mem">' +
        '<button onclick="mf(\'mc\')">MC</button><button onclick="mf(\'mr\')">MR</button>' +
        '<button onclick="mf(\'m+\')">M+</button><button onclick="mf(\'m-\')">M−</button>' +
      '</div>' +
      '<div class="btns">' +
        '<button class="bf" onclick="fn(\'C\')">C</button>' +
        '<button class="bf" onclick="fn(\'pm\')">±</button>' +
        '<button class="bf" onclick="fn(\'pct\')">%</button>' +
        '<button class="bo" onclick="op(\'÷\')">÷</button>' +
        '<button class="bn" onclick="ni(\'7\')">7</button>' +
        '<button class="bn" onclick="ni(\'8\')">8</button>' +
        '<button class="bn" onclick="ni(\'9\')">9</button>' +
        '<button class="bo" onclick="op(\'×\')">×</button>' +
        '<button class="bn" onclick="ni(\'4\')">4</button>' +
        '<button class="bn" onclick="ni(\'5\')">5</button>' +
        '<button class="bn" onclick="ni(\'6\')">6</button>' +
        '<button class="bo" onclick="op(\'−\')">−</button>' +
        '<button class="bn" onclick="ni(\'1\')">1</button>' +
        '<button class="bn" onclick="ni(\'2\')">2</button>' +
        '<button class="bn" onclick="ni(\'3\')">3</button>' +
        '<button class="bo" onclick="op(\'+\')">+</button>' +
        '<button class="bn" onclick="ni(\'0\')" style="grid-column:span 2">0</button>' +
        '<button class="bn" onclick="ni(\'.\')">.</button>' +
        '<button class="be" onclick="eq()">=</button>' +
      '</div>' +
      '<script>' +
      'var S={mem:0,expr:"",val:"0",ni:true,op:"",prev:0,hist:[]};' +
      'function ud(){' +
        'var e=S.expr;' +
        'if(S.op&&!S.ni)e=S.prev+" "+S.op+" "+S.val;' +
        'document.getElementById("expr").textContent=e;' +
        'document.getElementById("val").textContent=S.val;' +
      '}' +
      'function uh(){' +
        'var h="";' +
        'for(var i=S.hist.length-1;i>=0;i--)' +
          'h+="<div class=hr><span class=he>"+S.hist[i].e+"</span><span class=hv>= "+S.hist[i].r+"</span></div>";' +
        'if(!h)h="<div style=\\"text-align:center;padding:8px;color:#475569;font-size:10px\\">계산 이력 없음</div>";' +
        'document.getElementById("hlist").innerHTML=h;' +
      '}' +
      'document.getElementById("htog").onclick=function(){document.getElementById("hist").classList.toggle("open")};' +
      'function ni(n){' +
        'if(S.ni){S.val=(n==="."?"0.":n);S.ni=false}' +
        'else{if(n==="."&&S.val.includes("."))return;if(S.val==="0"&&n!==".")S.val=n;else S.val+=n}' +
        'ud();' +
      '}' +
      'function op(o){if(S.op&&!S.ni)eq();S.prev=parseFloat(S.val);S.op=o;S.expr=S.val+" "+o;S.ni=true;ud()}' +
      'function eq(){' +
        'if(!S.op)return;var c=parseFloat(S.val),r=0;' +
        'if(S.op==="+")r=S.prev+c;else if(S.op==="\\u2212")r=S.prev-c;' +
        'else if(S.op==="\\u00d7")r=S.prev*c;else if(S.op==="\\u00f7")r=c!==0?S.prev/c:NaN;' +
        'var fe=S.prev+" "+S.op+" "+c;' +
        'var rs=isNaN(r)||!isFinite(r)?"Error":String(parseFloat(r.toPrecision(12)));' +
        'S.hist.push({e:fe,r:rs});S.expr=fe+" =";S.val=rs;S.op="";S.ni=true;' +
        'ud();uh();' +
        'var h=document.getElementById("hist");if(!h.classList.contains("open"))h.classList.add("open");' +
      '}' +
      'function fn(f){' +
        'if(f==="C"){S.val="0";S.expr="";S.op="";S.prev=0;S.ni=true}' +
        'else if(f==="pm")S.val=String(-parseFloat(S.val));' +
        'else if(f==="pct")S.val=String(parseFloat(S.val)/100);' +
        'else if(f==="BS"){S.val=S.val.length>1?S.val.slice(0,-1):"0"}' +
        'ud();' +
      '}' +
      'function mf(f){' +
        'var v=parseFloat(S.val)||0;' +
        'if(f==="mc")S.mem=0;else if(f==="mr"){S.val=String(S.mem);S.ni=true}' +
        'else if(f==="m+")S.mem+=v;else if(f==="m-")S.mem-=v;' +
        'ud();' +
      '}' +
      'document.addEventListener("keydown",function(e){' +
        'if(e.key>="0"&&e.key<="9")ni(e.key);' +
        'else if(e.key===".")ni(".");' +
        'else if(e.key==="+")op("+");' +
        'else if(e.key==="-")op("\\u2212");' +
        'else if(e.key==="*")op("\\u00d7");' +
        'else if(e.key==="/"){e.preventDefault();op("\\u00f7")}' +
        'else if(e.key==="Enter"||e.key==="=")eq();' +
        'else if(e.key==="Escape")fn("C");' +
        'else if(e.key==="Backspace")fn("BS");' +
      '});' +
      '<\/script></body></html>';
  }

  window.toggleCalcPopup = function() {
    var id = ++_calcCount;
    var offset = ((id - 1) % 5) * 40;
    var w = window.open('', '_blank', 'width=320,height=520,top=' + (100 + offset) + ',left=' + (screen.width - 340 + offset) + ',resizable=no,menubar=no,toolbar=no,location=no,status=no');
    if (!w) { alert('팝업이 차단되었습니다. 팝업 허용 후 다시 시도하세요.'); return; }
    w.document.open();
    w.document.write(_calcHTML(id));
    w.document.close();
    _calcWindows.push(w);
    // 닫힐 때 목록에서 제거
    var check = setInterval(function() {
      if (w.closed) { clearInterval(check); _calcWindows = _calcWindows.filter(function(x) { return x !== w; }); }
    }, 1000);
  };
})();

// ============================================================
// 7. 단위변환 위젯
// ============================================================
(function() {
  var _unitTab = 'ph';

  function _ensureUnitDOM() {
    if (document.getElementById('unit-popup')) return;
    var div = document.createElement('div');
    div.id = 'unit-popup';
    div.className = 'unit-popup';
    div.innerHTML =
      '<div class="unit-titlebar" id="unit-drag">' +
        '<span>📐 단위변환</span>' +
        '<button onclick="toggleUnitPopup()">✕</button>' +
      '</div>' +
      '<div class="unit-tabs" id="unit-tabs">' +
        '<button class="active" onclick="_unitSw(\'ph\',this)">pH</button>' +
        '<button onclick="_unitSw(\'conc\',this)">농도</button>' +
        '<button onclick="_unitSw(\'abs\',this)">흡광도</button>' +
        '<button onclick="_unitSw(\'temp\',this)">온도</button>' +
        '<button onclick="_unitSw(\'vol\',this)">부피</button>' +
        '<button onclick="_unitSw(\'wt\',this)">무게</button>' +
      '</div>' +
      '<div class="unit-body" id="unit-body"></div>';
    document.body.appendChild(div);
    _makeDraggable(div, document.getElementById('unit-drag'));
  }

  function _renderUnit(type) {
    var el = document.getElementById('unit-body');
    if (!el) return;
    var h = '';
    if (type === 'ph') {
      h += '<label>pH 값</label>';
      h += '<input type="number" step="any" id="uv-ph" placeholder="7.0" oninput="_unitCalcPH()">';
      h += '<div class="unit-swap"><button onclick="_unitSwapPH()">⇅</button></div>';
      h += '<label>H⁺ 농도 (mol/L)</label>';
      h += '<input type="text" id="uv-hplus" placeholder="1.0e-7" oninput="_unitCalcH()" style="font-size:13px">';
      h += '<div class="unit-result" id="uv-ph-result"></div>';
    } else if (type === 'conc') {
      h += '<label>입력 농도</label>';
      h += '<div style="display:flex;gap:6px"><input type="number" step="any" id="uv-conc" placeholder="0.3" oninput="_unitCalcConc()" style="flex:1">';
      h += '<select id="uv-conc-unit" onchange="_unitCalcConc()" style="width:90px">';
      h += '<option value="mgkg">mg/kg</option><option value="ppm">ppm</option><option value="ppb">ppb</option><option value="ppt">ppt</option><option value="mgl">mg/L</option><option value="ugl">μg/L</option><option value="ugkg">μg/kg</option><option value="pct">%</option></select></div>';
      h += '<div class="unit-result" id="uv-conc-result"></div>';
    } else if (type === 'abs') {
      h += '<div style="background:rgba(255,255,255,0.04);border-radius:8px;padding:8px 10px;margin-bottom:10px;font-size:10px;color:#64748b;font-family:monospace">A = ε × c × l &nbsp;→&nbsp; c = A / (ε × l)</div>';
      h += '<label>흡광도 (A)</label>';
      h += '<input type="number" step="any" id="uv-abs" placeholder="0.542" oninput="_unitCalcBeer()">';
      h += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:8px">';
      h += '<div><label>몰흡광계수 ε (L/mol·cm)</label><input type="number" step="any" id="uv-eps" placeholder="6420" value="6420" oninput="_unitCalcBeer()"></div>';
      h += '<div><label>셀 길이 l (cm)</label><input type="number" step="any" id="uv-path" placeholder="1" value="1" oninput="_unitCalcBeer()"></div>';
      h += '</div>';
      h += '<div class="unit-result" id="uv-beer-result"></div>';
    } else if (type === 'temp') {
      h += '<label>입력 온도</label>';
      h += '<div style="display:flex;gap:6px"><input type="number" step="any" id="uv-temp" placeholder="25" oninput="_unitCalcTemp()" style="flex:1">';
      h += '<select id="uv-temp-unit" onchange="_unitCalcTemp()" style="width:70px"><option value="C">℃</option><option value="F">℉</option><option value="K">K</option></select></div>';
      h += '<div class="unit-result" id="uv-temp-result"></div>';
    } else if (type === 'vol') {
      h += '<label>입력 부피</label>';
      h += '<div style="display:flex;gap:6px"><input type="number" step="any" id="uv-vol" placeholder="500" oninput="_unitCalcVol()" style="flex:1">';
      h += '<select id="uv-vol-unit" onchange="_unitCalcVol()" style="width:70px"><option value="mL">mL</option><option value="L">L</option><option value="uL">μL</option></select></div>';
      h += '<div class="unit-result" id="uv-vol-result"></div>';
    } else if (type === 'wt') {
      h += '<label>입력 무게</label>';
      h += '<div style="display:flex;gap:6px"><input type="number" step="any" id="uv-wt" placeholder="100" oninput="_unitCalcWt()" style="flex:1">';
      h += '<select id="uv-wt-unit" onchange="_unitCalcWt()" style="width:80px"><option value="g">g</option><option value="mg">mg</option><option value="ug">μg</option><option value="ng">ng</option></select></div>';
      h += '<div class="unit-result" id="uv-wt-result"></div>';
    }
    el.innerHTML = h;
  }

  function _rr(label, val, unit) {
    return '<div class="ur-row"><span class="ur-label">' + label + '</span><span class="ur-val">' + val + ' <small style="color:#64748b">' + unit + '</small></span></div>';
  }

  // pH ↔ H⁺
  window._unitCalcPH = function() {
    var ph = parseFloat((document.getElementById('uv-ph') || {}).value);
    var res = document.getElementById('uv-ph-result');
    if (!res || isNaN(ph)) { if(res) res.innerHTML=''; return; }
    var hplus = Math.pow(10, -ph);
    var ohMinus = Math.pow(10, -(14 - ph));
    document.getElementById('uv-hplus').value = hplus.toExponential(4);
    res.innerHTML = _rr('H⁺ 농도', hplus.toExponential(4), 'mol/L') + _rr('OH⁻ 농도', ohMinus.toExponential(4), 'mol/L') + _rr('pOH', (14 - ph).toFixed(2), '') + _rr('성질', ph < 7 ? '🔴 산성' : ph > 7 ? '🔵 염기성' : '⚪ 중성', '');
  };

  window._unitCalcH = function() {
    var val = (document.getElementById('uv-hplus') || {}).value;
    var h = parseFloat(val);
    var res = document.getElementById('uv-ph-result');
    if (!res || isNaN(h) || h <= 0) { if(res) res.innerHTML=''; return; }
    var ph = -Math.log10(h);
    document.getElementById('uv-ph').value = ph.toFixed(4);
    var ohMinus = Math.pow(10, -(14 - ph));
    res.innerHTML = _rr('pH', ph.toFixed(4), '') + _rr('OH⁻ 농도', ohMinus.toExponential(4), 'mol/L') + _rr('pOH', (14 - ph).toFixed(2), '') + _rr('성질', ph < 7 ? '🔴 산성' : ph > 7 ? '🔵 염기성' : '⚪ 중성', '');
  };

  window._unitSwapPH = function() {
    var phEl = document.getElementById('uv-ph');
    var hEl = document.getElementById('uv-hplus');
    if (!phEl || !hEl) return;
    var tmp = phEl.value; phEl.value = hEl.value; hEl.value = tmp;
  };

  // Beer-Lambert
  window._unitCalcBeer = function() {
    var A = parseFloat((document.getElementById('uv-abs') || {}).value);
    var eps = parseFloat((document.getElementById('uv-eps') || {}).value);
    var l = parseFloat((document.getElementById('uv-path') || {}).value);
    var res = document.getElementById('uv-beer-result');
    if (!res) return;
    if (isNaN(A) || isNaN(eps) || isNaN(l) || eps === 0 || l === 0) { res.innerHTML = ''; return; }
    var c = A / (eps * l); // mol/L
    var cMM = c * 1000; // mmol/L
    var cUM = c * 1e6; // μmol/L
    var T = Math.pow(10, -A) * 100; // 투과율 %
    res.innerHTML = _rr('농도 c', c.toExponential(4), 'mol/L') + _rr('', cMM.toFixed(4), 'mmol/L') + _rr('', cUM.toFixed(2), 'μmol/L') + _rr('투과율 %T', T.toFixed(2), '%');
  };

  // 온도
  window._unitCalcTemp = function() {
    var v = parseFloat((document.getElementById('uv-temp') || {}).value);
    var u = (document.getElementById('uv-temp-unit') || {}).value || 'C';
    var res = document.getElementById('uv-temp-result');
    if (!res || isNaN(v)) { if(res) res.innerHTML = ''; return; }
    var c, f, k;
    if (u === 'C') { c = v; f = v * 9/5 + 32; k = v + 273.15; }
    else if (u === 'F') { c = (v - 32) * 5/9; f = v; k = c + 273.15; }
    else { c = v - 273.15; f = c * 9/5 + 32; k = v; }
    res.innerHTML = _rr('섭씨', c.toFixed(2), '℃') + _rr('화씨', f.toFixed(2), '℉') + _rr('켈빈', k.toFixed(2), 'K');
  };

  // 부피
  window._unitCalcVol = function() {
    var v = parseFloat((document.getElementById('uv-vol') || {}).value);
    var u = (document.getElementById('uv-vol-unit') || {}).value || 'mL';
    var res = document.getElementById('uv-vol-result');
    if (!res || isNaN(v)) { if(res) res.innerHTML = ''; return; }
    var ml;
    if (u === 'mL') ml = v;
    else if (u === 'L') ml = v * 1000;
    else ml = v / 1000; // μL
    res.innerHTML = _rr('', ml.toFixed(4), 'mL') + _rr('', (ml / 1000).toFixed(6), 'L') + _rr('', (ml * 1000).toFixed(2), 'μL');
  };

  // 무게
  window._unitCalcWt = function() {
    var v = parseFloat((document.getElementById('uv-wt') || {}).value);
    var u = (document.getElementById('uv-wt-unit') || {}).value || 'g';
    var res = document.getElementById('uv-wt-result');
    if (!res || isNaN(v)) { if(res) res.innerHTML = ''; return; }
    var mg;
    if (u === 'g') mg = v * 1000;
    else if (u === 'mg') mg = v;
    else if (u === 'ug') mg = v / 1000;
    else mg = v / 1e6; // ng
    res.innerHTML = _rr('', (mg / 1000).toFixed(6), 'g') + _rr('', mg.toFixed(4), 'mg') + _rr('', (mg * 1000).toFixed(2), 'μg') + _rr('', (mg * 1e6).toFixed(0), 'ng');
  };

  // 농도 변환 (mg/kg = ppm, μg/kg = ppb, ng/kg = ppt, % = 10000ppm)
  window._unitCalcConc = function() {
    var v = parseFloat((document.getElementById('uv-conc') || {}).value);
    var u = (document.getElementById('uv-conc-unit') || {}).value || 'mgkg';
    var res = document.getElementById('uv-conc-result');
    if (!res || isNaN(v)) { if(res) res.innerHTML = ''; return; }
    // 모두 ppm(=mg/kg=mg/L) 기준으로 변환
    var ppm;
    if (u === 'mgkg' || u === 'ppm' || u === 'mgl') ppm = v;
    else if (u === 'ppb' || u === 'ugl' || u === 'ugkg') ppm = v / 1000;
    else if (u === 'ppt') ppm = v / 1e6;
    else if (u === 'pct') ppm = v * 10000;
    else ppm = v;
    var ppb = ppm * 1000;
    var ppt = ppm * 1e6;
    var pct = ppm / 10000;
    res.innerHTML =
      _rr('', pct < 0.0001 ? pct.toExponential(4) : pct.toFixed(6), '%') +
      _rr('', ppm < 0.0001 ? ppm.toExponential(4) : ppm.toFixed(4), 'ppm (mg/kg, mg/L)') +
      _rr('', ppb < 0.01 ? ppb.toExponential(4) : ppb.toFixed(2), 'ppb (μg/kg, μg/L)') +
      _rr('', ppt < 1 ? ppt.toExponential(4) : ppt.toFixed(0), 'ppt (ng/kg, ng/L)');
  };

  window._unitSw = function(type, btn) {
    _unitTab = type;
    document.querySelectorAll('#unit-tabs button').forEach(function(b) { b.classList.remove('active'); });
    if (btn) btn.classList.add('active');
    _renderUnit(type);
  };

  window.toggleUnitPopup = function() {
    _ensureUnitDOM();
    var el = document.getElementById('unit-popup');
    var isVisible = el.classList.contains('visible');
    if (isVisible) {
      el.classList.remove('visible');
    } else {
      var sb = document.querySelector('.sidebar');
      var sbW = sb ? sb.offsetWidth : 250;
      el.style.top = '100px';
      el.style.left = (sbW + 16) + 'px';
      el.classList.add('visible');
      _renderUnit(_unitTab);
    }
    var btns = document.querySelectorAll('.sidebar-widgets .sw-btn');
    if (btns[1]) btns[1].classList.toggle('active', !isVisible);
  };
})();

// ============================================================
// 8. 드래그 유틸리티 (듀얼 모니터 지원)
// ============================================================
function _makeDraggable(el, handle) {
  var isDrag = false, sx, sy, ox, oy;
  handle.addEventListener('mousedown', function(e) {
    isDrag = true;
    sx = e.clientX; sy = e.clientY;
    var r = el.getBoundingClientRect();
    ox = r.left; oy = r.top;
    e.preventDefault();
  });
  document.addEventListener('mousemove', function(e) {
    if (!isDrag) return;
    var dx = e.clientX - sx, dy = e.clientY - sy;
    el.style.left = (ox + dx) + 'px';
    el.style.top = (oy + dy) + 'px';
    el.style.right = 'auto';
    el.style.bottom = 'auto';
  });
  document.addEventListener('mouseup', function() { isDrag = false; });
}
