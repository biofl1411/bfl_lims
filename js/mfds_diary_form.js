/**
 * 식약처 시험일지 양식 조회 및 인터랙티브 뷰어
 *
 * API 체인:
 *   exprIemCode → 0241(selectListExprMth) → exprMthSn
 *   exprMthSn + useScopeCode → 0242(selectListExprDiaryForm) → codename2 (HTML)
 *
 * 의존성: js/mfds-api.js (MFDS 전역 객체)
 */
var DIARY_FORM = (function() {

  // ── 캐시 ──
  var _methodCache = {};   // exprIemCode → [{ codeName, codeNo }]
  var _formCache = {};     // "exprMthSn_useScopeCode" → [{ codename2, codename, codeno }]

  // 사용범위코드: 개인 → 부서 → 기관 순서로 조회
  var USE_SCOPE_CODES = [
    { code: 'SY05000003', label: '개인' },
    { code: 'SY05000002', label: '부서' },
    { code: 'SY05000001', label: '기관' }
  ];

  // ── 시험방법 조회 (I-LMS-0241) ──
  function fetchMethods(exprIemCode) {
    if (_methodCache[exprIemCode]) {
      return Promise.resolve(_methodCache[exprIemCode]);
    }
    return MFDS.selectListExprMth({ exprIemCode: exprIemCode })
      .then(function(res) {
        var methods = [];
        if (res && res.resultData) {
          methods = Array.isArray(res.resultData) ? res.resultData : [res.resultData];
        }
        _methodCache[exprIemCode] = methods;
        return methods;
      });
  }

  // ── 시험일지 양식 조회 (I-LMS-0242) ──
  function fetchForm(exprMthSn, useScopeCode) {
    var key = exprMthSn + '_' + useScopeCode;
    if (_formCache[key]) {
      return Promise.resolve(_formCache[key]);
    }
    return MFDS.selectListExprDiaryForm({
      exprMthSn: String(exprMthSn),
      useScopeCode: useScopeCode
    }).then(function(res) {
      var forms = [];
      if (res && res.resultData) {
        forms = Array.isArray(res.resultData) ? res.resultData : [res.resultData];
      }
      _formCache[key] = forms;
      return forms;
    });
  }

  // ── 전체 체인: exprIemCode → 양식 목록 ──
  function fetchFormsForItem(exprIemCode) {
    return fetchMethods(exprIemCode).then(function(methods) {
      if (!methods || !methods.length) {
        return { methods: [], forms: [], exprIemCode: exprIemCode };
      }

      var allForms = [];
      var promises = [];

      methods.forEach(function(mth) {
        var exprMthSn = mth.codeNo || mth.codeno;
        if (!exprMthSn) return;

        USE_SCOPE_CODES.forEach(function(scope) {
          var p = fetchForm(exprMthSn, scope.code)
            .then(function(forms) {
              forms.forEach(function(f) {
                allForms.push({
                  codename2: f.codename2 || '',
                  codename: f.codename || '',
                  codeno: f.codeno || '',
                  exprMthSn: exprMthSn,
                  methodName: mth.codeName || mth.codename || '',
                  useScopeCode: scope.code,
                  useScopeLabel: scope.label
                });
              });
            })
            .catch(function(e) {
              console.warn('[DIARY_FORM] 양식 조회 실패:', exprIemCode, exprMthSn, scope.code, e.message || e);
            });
          promises.push(p);
        });
      });

      return Promise.all(promises).then(function() {
        return { methods: methods, forms: allForms, exprIemCode: exprIemCode };
      });
    });
  }

  // ── HTML 양식을 인터랙티브하게 렌더링 ──
  function renderInteractive(htmlContent, container) {
    if (typeof container === 'string') container = document.getElementById(container);
    if (!container) return;

    // HTML 삽입
    container.innerHTML = htmlContent;

    // 테이블 기본 스타일 보정
    var tables = container.querySelectorAll('table');
    tables.forEach(function(t) {
      t.style.borderCollapse = 'collapse';
      t.style.width = '100%';
      t.style.fontSize = '13px';
    });

    // 모든 td에 기본 border
    var allTds = container.querySelectorAll('td, th');
    allTds.forEach(function(td) {
      if (!td.style.border && !td.style.borderBottom) {
        td.style.border = '1px solid #ccc';
        td.style.padding = '4px 6px';
      }
    });

    // 빈 <td> 셀을 편집 가능하게 만들기
    var tds = container.querySelectorAll('td');
    tds.forEach(function(td) {
      // 자식에 테이블이 있으면 건너뜀 (구조 셀)
      if (td.querySelector('table')) return;
      // 이미 input/select가 있으면 건너뜀
      if (td.querySelector('input, select, textarea')) return;

      var text = td.textContent.trim();
      var html = td.innerHTML.trim();

      // 빈 셀이거나 &nbsp;만 있는 셀 → 편집 가능
      if (!text || text === '\u00a0' || html === '&nbsp;' || html === '') {
        td.setAttribute('contenteditable', 'true');
        td.classList.add('df-editable');
        td.title = '클릭하여 입력';
      }
    });
  }

  // ── 편집된 폼 HTML 수집 ──
  function collectFormHtml(container) {
    if (typeof container === 'string') container = document.getElementById(container);
    if (!container) return '';

    // contenteditable 속성 제거한 클린 HTML 반환
    var clone = container.cloneNode(true);
    var editables = clone.querySelectorAll('[contenteditable]');
    editables.forEach(function(el) {
      el.removeAttribute('contenteditable');
      el.classList.remove('df-editable');
    });
    return clone.innerHTML;
  }

  // ── 편집된 셀 데이터 수집 (key-value) ──
  function collectEditedValues(container) {
    if (typeof container === 'string') container = document.getElementById(container);
    if (!container) return {};

    var values = {};
    var editables = container.querySelectorAll('.df-editable');
    var idx = 0;
    editables.forEach(function(el) {
      var val = el.textContent.trim();
      if (val) {
        values['cell_' + idx] = val;
      }
      idx++;
    });
    return values;
  }

  // ── 캐시 초기화 ──
  function clearCache() {
    _methodCache = {};
    _formCache = {};
  }

  // Public API
  return {
    fetchMethods: fetchMethods,
    fetchForm: fetchForm,
    fetchFormsForItem: fetchFormsForItem,
    renderInteractive: renderInteractive,
    collectFormHtml: collectFormHtml,
    collectEditedValues: collectEditedValues,
    clearCache: clearCache,
    USE_SCOPE_CODES: USE_SCOPE_CODES
  };

})();

console.log('[DIARY_FORM] 시험일지 양식 모듈 로드 완료');
