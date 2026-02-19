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
      { label: '세금계산서미발행',    href: 'salesMgmt.html#arManage',     page: 'arManage',     internalPage: 'arManage' },
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
      { label: '업체등록·수정',     disabled: true },
      { label: '검사목적 관리',     href: 'inspectionMgmt.html',  page: 'reception-inspection' },
      { label: '접수 등록',         href: 'sampleReceipt.html',   page: 'reception-register' },
      { label: '접수 현황',         disabled: true },
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
      { label: '결과 입력',         disabled: true },
      { label: '결재 승인',         disabled: true },
      { label: '시험 이력 조회',    disabled: true },
      { label: '일정관리',          disabled: true },
      { label: '지부관리',          disabled: true },
      { label: '실적보고',          disabled: true },
      { label: 'LIMS 연동',        disabled: true }
    ]
  },
  { id: 'results',       icon: '📄', label: '성적 관리',      disabled: true },
  { id: 'finance',       icon: '💰', label: '재무 관리',      disabled: true },
  { id: 'stats',         icon: '📈', label: '통계 분석',      disabled: true },
  { id: 'docs',          icon: '📁', label: '문서 관리',      disabled: true },
  { id: 'inventory',     icon: '🧪', label: '재고/시약 관리', disabled: true },
  { id: 'notice',        icon: '📢', label: '공지',           disabled: true },
  {
    id: 'admin',
    icon: '🔧',
    label: '관리자',
    sub: [
      { label: '사용자 관리',       href: 'userMgmt.html',              page: 'admin-users' },
      { label: '부서 관리',         disabled: true },
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
  </nav>`;

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
// 4. 초기화 — DOM 준비 후 실행
// ============================================================
(function initSidebar() {
  function _init() {
    renderSidebar();
    _restoreSidebarState();
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', _init);
  } else {
    _init();
  }
})();
