/**
 * BFL LIMS - 식약처 코드매핑 데이터 공통 모듈
 * Firestore에 저장된 식약처 코드매핑 데이터를 로드/캐시/검색하는 공통 함수
 *
 * 의존성: firebase-init.js (db 전역 변수)
 *
 * Firestore 컬렉션:
 *   mfds_common_codes    — 공통코드 383건 (드롭다운용)
 *   mfds_product_codes   — 품목코드 8,404건 (식품 품목 분류 트리)
 *   mfds_test_items      — 시험항목 2,940건 (검사항목 코드)
 *   mfds_units           — 단위 106건 (결과 단위)
 *   mfds_item_mappings   — BFL↔식약처 항목 매핑 (사용자 설정)
 *
 * 정적 JSON (data/mfds/):
 *   individual_standards.json — 개별기준규격 15,803건 (식품)
 *   common_standards.json     — 공통기준규격 33,663건 (식품)
 *
 * 사용법:
 *   <script src="js/firebase-init.js"></script>
 *   <script src="js/mfds-codes.js"></script>
 */

// ============================================================
// 전역 네임스페이스 (MFDS_CODES)
// ============================================================
var MFDS_CODES = MFDS_CODES || {};

// ============================================================
// 1. 내부 캐시 변수
// ============================================================
var _mc_productCache = null;
var _mc_productCacheTime = 0;
var _mc_testItemCache = null;
var _mc_unitCache = null;
var _mc_commonCodeCache = null;
var _mc_itemMappingCache = null;
var _mc_indStdCache = null;
var _mc_cmnStdCache = null;
var _mc_productNameMap = null;   // 품목코드 → 한글명 빠른 조회용
var _mc_testItemNameMap = null;  // 시험항목코드 → 한글명 빠른 조회용
var _mc_unitNameMap = null;      // 단위코드 → 단위명 빠른 조회용

/** 캐시 유효시간 (밀리초) — 10분 */
var MC_CACHE_TTL = 600000;

// ============================================================
// 2. 품목코드 (mfds_product_codes) — 8,404건
// ============================================================

/**
 * 품목코드 전체 로드 (사용여부 Y인 것만, 10분 캐시)
 * @returns {Promise<Array>} 품목코드 배열
 */
MFDS_CODES.loadProductCodes = function() {
  var now = Date.now();
  if (_mc_productCache && (now - _mc_productCacheTime < MC_CACHE_TTL)) {
    return Promise.resolve(_mc_productCache);
  }

  return db.collection('mfds_product_codes').get()
    .then(function(snap) {
      _mc_productCache = [];
      snap.forEach(function(doc) {
        var d = doc.data();
        if (d['사용 여부'] === 'Y') {
          _mc_productCache.push(d);
        }
      });
      _mc_productCacheTime = Date.now();
      console.log('[MFDS_CODES] 품목코드 로드:', _mc_productCache.length + '건');
      return _mc_productCache;
    })
    .catch(function(err) {
      console.warn('[MFDS_CODES] 품목코드 로드 실패:', err.message);
      return _mc_productCache || [];
    });
};

/**
 * 품목코드 계층 트리 생성
 * 수준(level)별로 그룹핑: 1(대분류) → 2(중분류) → 3(소분류)
 * @param {Array} allCodes - 전체 품목코드 배열
 * @returns {Object} { level1: [...], byParent: { 부모코드: [...] } }
 */
MFDS_CODES.buildProductTree = function(allCodes) {
  var level1 = [];
  var byParent = {};

  allCodes.forEach(function(item) {
    var level = item['수준'];
    var parentCode = item['상위 품목 코드'];
    var code = item['품목 코드'];

    if (level === 1 || level === '1') {
      level1.push(item);
    }

    if (parentCode && parentCode !== code) {
      if (!byParent[parentCode]) byParent[parentCode] = [];
      byParent[parentCode].push(item);
    }
  });

  // 이름순 정렬
  level1.sort(function(a, b) {
    return (a['한글 명'] || '').localeCompare(b['한글 명'] || '');
  });

  Object.keys(byParent).forEach(function(key) {
    byParent[key].sort(function(a, b) {
      return (a['한글 명'] || '').localeCompare(b['한글 명'] || '');
    });
  });

  return { level1: level1, byParent: byParent };
};

/**
 * 품목코드 한글명 검색 (최대 30건)
 * @param {string} query - 검색어
 * @param {Array} allCodes - 전체 품목코드 배열
 * @returns {Array} 매칭된 품목코드 배열 (최대 30건)
 */
MFDS_CODES.searchProductCodes = function(query, allCodes) {
  if (!query || query.length < 1) return [];
  var q = query.toLowerCase();
  var results = [];

  for (var i = 0; i < allCodes.length && results.length < 30; i++) {
    var item = allCodes[i];
    var name = (item['한글 명'] || '').toLowerCase();
    var alias = (item['별칭'] || '').toLowerCase();
    if (name.indexOf(q) >= 0 || alias.indexOf(q) >= 0) {
      results.push(item);
    }
  }
  return results;
};

/**
 * 캐스케이딩 드롭다운 렌더링 (3단계: 대분류→중분류→소분류)
 * @param {string} containerId - 컨테이너 요소 ID
 * @param {Function} onSelect - 선택 콜백 function(item) {}
 */
MFDS_CODES.renderProductPicker = function(containerId, onSelect) {
  var container = document.getElementById(containerId);
  if (!container) return;

  container.innerHTML =
    '<div class="mfds-section">' +
    '  <div class="mfds-label">식약처 품목코드</div>' +
    '  <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px;">' +
    '    <select id="mfds-cat1" style="flex:1;min-width:120px;padding:6px 8px;border:1px solid #ccc;border-radius:4px;font-size:13px;">' +
    '      <option value="">대분류 선택</option>' +
    '    </select>' +
    '    <select id="mfds-cat2" style="flex:1;min-width:140px;padding:6px 8px;border:1px solid #ccc;border-radius:4px;font-size:13px;" disabled>' +
    '      <option value="">중분류 선택</option>' +
    '    </select>' +
    '    <select id="mfds-cat3" style="flex:2;min-width:180px;padding:6px 8px;border:1px solid #ccc;border-radius:4px;font-size:13px;" disabled>' +
    '      <option value="">소분류 선택</option>' +
    '    </select>' +
    '  </div>' +
    '  <div style="position:relative;margin-bottom:8px;">' +
    '    <input type="text" id="mfds-product-search" placeholder="또는 품목명으로 검색..." ' +
    '           style="width:100%;padding:6px 8px;border:1px solid #ccc;border-radius:4px;font-size:13px;">' +
    '    <div id="mfds-product-search-results" style="display:none;position:absolute;top:100%;left:0;right:0;' +
    '         max-height:200px;overflow-y:auto;background:#fff;border:1px solid #ccc;border-top:none;' +
    '         border-radius:0 0 4px 4px;z-index:100;box-shadow:0 4px 8px rgba(0,0,0,0.1);"></div>' +
    '  </div>' +
    '  <div id="mfds-product-selected" style="display:none;padding:6px 10px;background:#e3f2fd;' +
    '       border-radius:4px;font-size:13px;color:#1565c0;">' +
    '    <span id="mfds-product-selected-text"></span>' +
    '    <button onclick="MFDS_CODES._clearProductSelection(\'' + containerId + '\')" ' +
    '            style="float:right;border:none;background:none;color:#999;cursor:pointer;font-size:14px;">✕</button>' +
    '  </div>' +
    '  <input type="hidden" id="mfds-product-code">' +
    '  <input type="hidden" id="mfds-product-name">' +
    '  <div style="margin-top:10px;border-top:1px dashed #ffe0b2;padding-top:8px">' +
    '    <div style="font-size:11px;font-weight:700;color:#e65100;margin-bottom:6px">📦 공통기준규격 항목 검색</div>' +
    '    <div style="position:relative">' +
    '      <input type="text" id="mfds-cmn-search" placeholder="공통규격 항목명 또는 코드 검색..." ' +
    '             style="width:100%;padding:5px 8px;border:1px solid #ffe0b2;border-radius:4px;font-size:12px;background:#fffbf0">' +
    '      <div id="mfds-cmn-results" style="display:none;position:absolute;top:100%;left:0;right:0;' +
    '           max-height:200px;overflow-y:auto;background:#fff;border:1px solid #ffe0b2;border-top:none;' +
    '           border-radius:0 0 4px 4px;z-index:100;box-shadow:0 4px 8px rgba(0,0,0,0.1)"></div>' +
    '    </div>' +
    '  </div>' +
    '</div>';

  // 공통규격 검색 핸들러 초기화
  MFDS_CODES._initCmnSearch();

  // 데이터 로드 후 대분류 채우기
  MFDS_CODES.loadProductCodes().then(function(allCodes) {
    var tree = MFDS_CODES.buildProductTree(allCodes);
    var cat1 = document.getElementById('mfds-cat1');
    var cat2 = document.getElementById('mfds-cat2');
    var cat3 = document.getElementById('mfds-cat3');
    var searchInput = document.getElementById('mfds-product-search');
    var searchResults = document.getElementById('mfds-product-search-results');

    // 대분류 옵션 채우기
    tree.level1.forEach(function(item) {
      var opt = document.createElement('option');
      opt.value = item['품목 코드'];
      opt.textContent = item['한글 명'];
      cat1.appendChild(opt);
    });

    // 피커 상태 저장 (외부 접근용: lockCategories 등)
    MFDS_CODES._pickerTree = tree;
    MFDS_CODES._pickerAllCodes = allCodes;
    MFDS_CODES._pickerOnSelect = onSelect;

    // 대기중인 카테고리 고정 적용
    if (MFDS_CODES._pendingLock) {
      var pl = MFDS_CODES._pendingLock;
      MFDS_CODES._pendingLock = null;
      setTimeout(function() { MFDS_CODES._applyLock(pl.cat1, pl.cat2); }, 50);
    }

    // 대분류 변경 → 중분류 채우기
    cat1.addEventListener('change', function() {
      cat2.innerHTML = '<option value="">중분류 선택</option>';
      cat3.innerHTML = '<option value="">소분류 선택</option>';
      cat2.disabled = true;
      cat3.disabled = true;

      var children = tree.byParent[cat1.value] || [];
      if (children.length > 0) {
        children.forEach(function(item) {
          var opt = document.createElement('option');
          opt.value = item['품목 코드'];
          opt.textContent = item['한글 명'];
          cat2.appendChild(opt);
        });
        cat2.disabled = false;
      }
    });

    // 중분류 변경 → 소분류 채우기
    cat2.addEventListener('change', function() {
      cat3.innerHTML = '<option value="">소분류 선택</option>';
      cat3.disabled = true;

      var children = tree.byParent[cat2.value] || [];
      if (children.length > 0) {
        children.forEach(function(item) {
          var opt = document.createElement('option');
          opt.value = item['품목 코드'];
          opt.textContent = item['한글 명'];
          cat3.appendChild(opt);
        });
        cat3.disabled = false;
      } else if (cat2.value) {
        // 중분류가 최하위인 경우 바로 선택
        var selected = allCodes.find(function(c) { return c['품목 코드'] === cat2.value; });
        if (selected) MFDS_CODES._selectProduct(selected, onSelect);
      }
    });

    // 소분류 변경 → 선택 확정
    cat3.addEventListener('change', function() {
      if (!cat3.value) return;
      var selected = allCodes.find(function(c) { return c['품목 코드'] === cat3.value; });
      if (selected) MFDS_CODES._selectProduct(selected, onSelect);
    });

    // 텍스트 검색
    var searchTimer = null;
    searchInput.addEventListener('input', function() {
      clearTimeout(searchTimer);
      var q = searchInput.value.trim();
      if (q.length < 1) {
        searchResults.style.display = 'none';
        return;
      }
      searchTimer = setTimeout(function() {
        var results = MFDS_CODES.searchProductCodes(q, allCodes);
        // 카테고리 고정 시 해당 분류 내에서만 필터링
        if (MFDS_CODES._lockedDescendants) {
          results = results.filter(function(item) {
            return MFDS_CODES._lockedDescendants.has(item['품목 코드']);
          });
        }
        if (results.length === 0) {
          searchResults.innerHTML = '<div style="padding:8px;color:#999;font-size:12px;">검색 결과 없음</div>';
        } else {
          searchResults.innerHTML = results.map(function(item) {
            var lvl = item['수준'] || '';
            var indent = lvl > 1 ? '&nbsp;'.repeat((lvl - 1) * 2) : '';
            return '<div class="mfds-search-item" data-code="' + item['품목 코드'] + '" ' +
              'style="display:flex;justify-content:space-between;align-items:center;padding:6px 10px;cursor:pointer;font-size:12px;border-bottom:1px solid #f0f0f0;" ' +
              'onmouseover="this.style.background=\'#e3f2fd\'" onmouseout="this.style.background=\'#fff\'">' +
              '<span>' + indent + '<strong>' + (item['한글 명'] || '') + '</strong> ' +
              '<span style="color:#999;font-size:11px;">(' + item['품목 코드'] + ')</span></span>' +
              '<button data-code="' + item['품목 코드'] + '" ' +
              'style="flex-shrink:0;padding:3px 12px;background:#1565c0;color:#fff;border:none;border-radius:4px;font-size:11px;cursor:pointer;white-space:nowrap;margin-left:8px;">선택</button>' +
              '</div>';
          }).join('');
        }
        searchResults.style.display = 'block';
      }, 300);
    });

    // 검색 결과 클릭
    searchResults.addEventListener('click', function(e) {
      var target = e.target.closest('.mfds-search-item');
      if (!target) return;
      var code = target.getAttribute('data-code');
      var selected = allCodes.find(function(c) { return c['품목 코드'] === code; });
      if (selected) {
        MFDS_CODES._selectProduct(selected, onSelect);
        searchInput.value = '';
        searchResults.style.display = 'none';
      }
    });

    // 포커스 아웃 시 검색 결과 닫기
    searchInput.addEventListener('blur', function() {
      setTimeout(function() { searchResults.style.display = 'none'; }, 200);
    });
  });
};

/**
 * 품목 선택 처리 (내부용)
 */
MFDS_CODES._selectProduct = function(item, onSelect) {
  var code = item['품목 코드'];
  var name = item['한글 명'] || '';

  document.getElementById('mfds-product-code').value = code;
  document.getElementById('mfds-product-name').value = name;

  var selectedDiv = document.getElementById('mfds-product-selected');
  var selectedText = document.getElementById('mfds-product-selected-text');
  selectedText.textContent = code + ' — ' + name;
  selectedDiv.style.display = 'block';

  if (typeof onSelect === 'function') {
    onSelect(item);
  }
};

/**
 * 품목 선택 해제 (내부용)
 */
MFDS_CODES._clearProductSelection = function(containerId) {
  document.getElementById('mfds-product-code').value = '';
  document.getElementById('mfds-product-name').value = '';
  document.getElementById('mfds-product-selected').style.display = 'none';
  document.getElementById('mfds-cat1').value = '';
  document.getElementById('mfds-cat2').innerHTML = '<option value="">중분류 선택</option>';
  document.getElementById('mfds-cat2').disabled = true;
  document.getElementById('mfds-cat3').innerHTML = '<option value="">소분류 선택</option>';
  document.getElementById('mfds-cat3').disabled = true;
  // 기준규격 섹션도 숨기기
  if (typeof clearMfdsStandardItems === 'function') clearMfdsStandardItems();
};

// ============================================================
// 카테고리 고정/해제 (자가품질위탁검사용 등 특정 분류 고정)
// ============================================================

/** 대기중인 카테고리 고정 요청 */
MFDS_CODES._pendingLock = null;

/** 고정된 분류 하위 품목코드 셋 (검색 필터링용) */
MFDS_CODES._lockedDescendants = null;

/**
 * 대분류/중분류를 이름으로 고정하고 소분류(품목명)만 선택 가능하게 함
 * @param {string} cat1Name - 대분류 한글명 (예: '가공식품')
 * @param {string} cat2Name - 중분류 한글명 (예: '가공식품(전부개정)')
 */
MFDS_CODES.lockCategories = function(cat1Name, cat2Name) {
  if (!MFDS_CODES._pickerTree) {
    MFDS_CODES._pendingLock = { cat1: cat1Name, cat2: cat2Name };
    return;
  }
  MFDS_CODES._applyLock(cat1Name, cat2Name);
};

/**
 * 카테고리 고정 실행 (내부용)
 */
MFDS_CODES._applyLock = function(cat1Name, cat2Name) {
  var tree = MFDS_CODES._pickerTree;
  var cat1El = document.getElementById('mfds-cat1');
  var cat2El = document.getElementById('mfds-cat2');
  var searchInput = document.getElementById('mfds-product-search');
  if (!cat1El || !tree) return;

  // 대분류 찾기 + 선택
  var cat1Item = tree.level1.find(function(item) { return item['한글 명'] === cat1Name; });
  if (!cat1Item) { console.warn('[MFDS] 대분류 찾기 실패:', cat1Name); return; }

  cat1El.value = cat1Item['품목 코드'];
  cat1El.dispatchEvent(new Event('change'));

  // 중분류 찾기 + 선택
  var cat2Children = tree.byParent[cat1Item['품목 코드']] || [];
  var cat2Item = cat2Children.find(function(item) { return item['한글 명'] === cat2Name; });
  if (cat2Item) {
    cat2El.value = cat2Item['품목 코드'];
    cat2El.dispatchEvent(new Event('change'));

    // 하위 품목코드 셋 구축 (검색 필터링용)
    var descendants = new Set();
    var addDesc = function(parentCode) {
      var ch = tree.byParent[parentCode] || [];
      ch.forEach(function(c) {
        descendants.add(c['품목 코드']);
        addDesc(c['품목 코드']);
      });
    };
    addDesc(cat2Item['품목 코드']);
    MFDS_CODES._lockedDescendants = descendants;
    console.log('[MFDS] 카테고리 고정:', cat1Name, '>', cat2Name, '(하위', descendants.size, '건)');
  } else {
    console.warn('[MFDS] 중분류 찾기 실패:', cat2Name);
  }

  // 검색 placeholder 업데이트
  if (searchInput) {
    searchInput.placeholder = '품목명 검색 (' + cat2Name + ' 내)...';
  }
};

/**
 * 카테고리 고정 해제 (드롭다운 활성화, 필터 해제)
 */
MFDS_CODES.unlockCategories = function() {
  MFDS_CODES._pendingLock = null;
  MFDS_CODES._lockedDescendants = null;
  var cat1El = document.getElementById('mfds-cat1');
  var cat2El = document.getElementById('mfds-cat2');
  var cat3El = document.getElementById('mfds-cat3');
  var searchInput = document.getElementById('mfds-product-search');
  if (cat1El) { cat1El.disabled = false; cat1El.style.background = ''; }
  if (cat2El) { cat2El.disabled = false; cat2El.style.background = ''; }
  if (cat3El) { cat3El.disabled = false; cat3El.style.background = ''; }
  if (searchInput) { searchInput.placeholder = '또는 품목명으로 검색...'; }
};

// ============================================================
// 3. 시험항목 (mfds_test_items) — 2,940건
// ============================================================

/**
 * 시험항목 전체 로드 (캐시)
 * @returns {Promise<Array>}
 */
MFDS_CODES.loadTestItems = function() {
  if (_mc_testItemCache) return Promise.resolve(_mc_testItemCache);

  return db.collection('mfds_test_items').get()
    .then(function(snap) {
      _mc_testItemCache = [];
      snap.forEach(function(doc) { _mc_testItemCache.push(doc.data()); });
      console.log('[MFDS_CODES] 시험항목 로드:', _mc_testItemCache.length + '건');
      return _mc_testItemCache;
    })
    .catch(function(err) {
      console.warn('[MFDS_CODES] 시험항목 로드 실패:', err.message);
      return [];
    });
};

/**
 * 시험항목 사용여부 확인 (전역 함수)
 * @param {string} code - 시험항목코드
 * @returns {boolean} 활성(true) / 비활성(false)
 */
MFDS_CODES.isActive = function(code) {
  if (!code || !_mc_testItemCache || !_mc_testItemCache.length) return true;
  var item = _mc_testItemCache.find(function(t) { return (t['시험항목코드'] || '').toUpperCase() === code.toUpperCase(); });
  return item ? (item['사용여부'] || 'Y') === 'Y' : true;
};

// 전역 함수로도 제공 (다른 페이지에서 간편 사용)
window.isTestItemActiveGlobal = MFDS_CODES.isActive;

/**
 * 시험항목 검색 (코드, 한글명, 영문명, 별칭)
 * @param {string} query - 검색어
 * @param {Array} allItems - 전체 시험항목 배열
 * @returns {Array} 매칭된 항목 (최대 50건)
 */
MFDS_CODES.searchTestItems = function(query, allItems) {
  if (!query || query.length < 1) return allItems.slice(0, 50);
  var q = query.toLowerCase();
  var results = [];

  for (var i = 0; i < allItems.length && results.length < 50; i++) {
    var item = allItems[i];
    var code = (item['시험항목코드'] || '').toLowerCase();
    var name = (item['한글명'] || '').toLowerCase();
    var eng = (item['영문명'] || '').toLowerCase();
    var alias = (item['별칭'] || '').toLowerCase();
    if (code.indexOf(q) >= 0 || name.indexOf(q) >= 0 ||
        eng.indexOf(q) >= 0 || alias.indexOf(q) >= 0) {
      results.push(item);
    }
  }
  return results;
};

// ============================================================
// 4. 단위 (mfds_units) — 106건
// ============================================================

/**
 * 단위 전체 로드 (캐시)
 * @returns {Promise<Array>}
 */
MFDS_CODES.loadUnits = function() {
  if (_mc_unitCache) return Promise.resolve(_mc_unitCache);

  return db.collection('mfds_units').get()
    .then(function(snap) {
      _mc_unitCache = [];
      snap.forEach(function(doc) { _mc_unitCache.push(doc.data()); });
      _mc_unitCache.sort(function(a, b) {
        return (a['단위명'] || '').localeCompare(b['단위명'] || '');
      });
      console.log('[MFDS_CODES] 단위 로드:', _mc_unitCache.length + '건');
      return _mc_unitCache;
    })
    .catch(function(err) {
      console.warn('[MFDS_CODES] 단위 로드 실패:', err.message);
      return [];
    });
};

// ============================================================
// 5. 공통코드 (mfds_common_codes) — 383건
// ============================================================

/**
 * 공통코드 전체 로드 (캐시)
 * @returns {Promise<Array>}
 */
MFDS_CODES.loadCommonCodes = function() {
  if (_mc_commonCodeCache) return Promise.resolve(_mc_commonCodeCache);

  return db.collection('mfds_common_codes').get()
    .then(function(snap) {
      _mc_commonCodeCache = [];
      snap.forEach(function(doc) { _mc_commonCodeCache.push(doc.data()); });
      console.log('[MFDS_CODES] 공통코드 로드:', _mc_commonCodeCache.length + '건');
      return _mc_commonCodeCache;
    })
    .catch(function(err) {
      console.warn('[MFDS_CODES] 공통코드 로드 실패:', err.message);
      return [];
    });
};

/**
 * 특정 코드 종류의 공통코드 필터
 * @param {string} codeType - 코드종류 (예: 'IM01', 'IM02')
 * @returns {Promise<Array>} 해당 종류의 코드 배열
 */
MFDS_CODES.getCommonCodesByType = function(codeType) {
  return MFDS_CODES.loadCommonCodes().then(function(all) {
    return all.filter(function(c) {
      return c['공통코드종류'] === codeType && c['사용여부'] === 'Y';
    }).sort(function(a, b) {
      return (a['순서'] || 0) - (b['순서'] || 0);
    });
  });
};

// ============================================================
// 6. BFL ↔ 식약처 항목 매핑 (mfds_item_mappings)
// ============================================================

/**
 * 항목 매핑 전체 로드 (캐시)
 * @returns {Promise<Object>} { bflItemName: mappingData, ... }
 */
MFDS_CODES.loadItemMappings = function() {
  if (_mc_itemMappingCache) return Promise.resolve(_mc_itemMappingCache);

  return db.collection('mfds_item_mappings').get()
    .then(function(snap) {
      _mc_itemMappingCache = {};
      snap.forEach(function(doc) {
        _mc_itemMappingCache[doc.id] = doc.data();
      });
      console.log('[MFDS_CODES] 항목매핑 로드:', Object.keys(_mc_itemMappingCache).length + '건');
      return _mc_itemMappingCache;
    })
    .catch(function(err) {
      console.warn('[MFDS_CODES] 항목매핑 로드 실패:', err.message);
      return {};
    });
};

/**
 * 항목 매핑 저장
 * @param {Object} mapping - 매핑 데이터
 * @param {string} mapping.bflItemName - BFL 항목명
 * @param {string} mapping.bflUnit - BFL 항목단위
 * @param {string} mapping.mfdsTestItemCode - 식약처 시험항목코드
 * @param {string} mapping.mfdsTestItemName - 식약처 시험항목명
 * @param {string} mapping.mfdsUnitCode - 식약처 단위코드
 * @param {string} mapping.mfdsUnitName - 식약처 단위명
 * @returns {Promise}
 */
MFDS_CODES.saveItemMapping = function(mapping) {
  var docId = mapping.bflItemName;
  if (!docId) return Promise.reject(new Error('bflItemName 필수'));

  mapping.mappedAt = firebase.firestore.FieldValue.serverTimestamp();

  return db.collection('mfds_item_mappings').doc(docId).set(mapping, { merge: true })
    .then(function() {
      // 캐시 업데이트
      if (_mc_itemMappingCache) {
        _mc_itemMappingCache[docId] = mapping;
      }
      console.log('[MFDS_CODES] 매핑 저장:', docId, '→', mapping.mfdsTestItemCode);
    });
};

/**
 * 항목 매핑 삭제
 * @param {string} bflItemName - BFL 항목명
 * @returns {Promise}
 */
MFDS_CODES.deleteItemMapping = function(bflItemName) {
  return db.collection('mfds_item_mappings').doc(bflItemName).delete()
    .then(function() {
      if (_mc_itemMappingCache) {
        delete _mc_itemMappingCache[bflItemName];
      }
      console.log('[MFDS_CODES] 매핑 삭제:', bflItemName);
    });
};

// ============================================================
// 7. 기준규격 (정적 JSON — data/mfds/)
// ============================================================

/**
 * 개별기준규격 로드 (식품 15,803건, 정적 JSON)
 * @returns {Promise<Array>}
 */
MFDS_CODES.loadIndividualStandards = function() {
  if (_mc_indStdCache) return Promise.resolve(_mc_indStdCache);

  return fetch('data/mfds/individual_standards.json')
    .then(function(res) { return res.json(); })
    .then(function(data) {
      _mc_indStdCache = data;
      console.log('[MFDS_CODES] 개별기준규격 로드:', data.length + '건');
      return data;
    })
    .catch(function(err) {
      console.warn('[MFDS_CODES] 개별기준규격 로드 실패:', err.message);
      return [];
    });
};

/**
 * 공통기준규격 로드 (식품 33,663건, 정적 JSON)
 * @returns {Promise<Array>}
 */
MFDS_CODES.loadCommonStandards = function() {
  if (_mc_cmnStdCache) return Promise.resolve(_mc_cmnStdCache);

  return fetch('data/mfds/common_standards.json')
    .then(function(res) { return res.json(); })
    .then(function(data) {
      _mc_cmnStdCache = data;
      console.log('[MFDS_CODES] 공통기준규격 로드:', data.length + '건');
      return data;
    })
    .catch(function(err) {
      console.warn('[MFDS_CODES] 공통기준규격 로드 실패:', err.message);
      return [];
    });
};

/**
 * 기준규격 검색 (품목코드, 시험항목코드, 기준규격값, 기준규격값설명)
 * @param {string} query - 검색어
 * @param {Array} standards - 기준규격 배열
 * @returns {Array} 매칭된 기준규격 (최대 200건)
 */
MFDS_CODES.searchStandards = function(query, standards) {
  if (!query || query.length < 1) return [];
  var q = query.toLowerCase();
  var results = [];

  for (var i = 0; i < standards.length && results.length < 200; i++) {
    var s = standards[i];
    var pCode = (s['품목코드'] || '').toLowerCase();
    var tCode = (s['시험항목코드'] || '').toLowerCase();
    var val = (s['기준규격값'] || '').toLowerCase();
    var desc = (s['기준규격값설명'] || '').toLowerCase();
    var src = (s['출처'] || '').toLowerCase();
    if (pCode.indexOf(q) >= 0 || tCode.indexOf(q) >= 0 ||
        val.indexOf(q) >= 0 || desc.indexOf(q) >= 0 || src.indexOf(q) >= 0) {
      results.push(s);
    }
  }
  return results;
};

/**
 * 품목코드 → 한글명 조회 맵 생성 (최초 1회)
 * @returns {Promise<Object>} { 품목코드: 한글명, ... }
 */
MFDS_CODES.getProductNameMap = function() {
  if (_mc_productNameMap) return Promise.resolve(_mc_productNameMap);
  return MFDS_CODES.loadProductCodes().then(function(codes) {
    _mc_productNameMap = {};
    codes.forEach(function(c) {
      _mc_productNameMap[c['품목 코드']] = c['한글 명'] || '';
    });
    return _mc_productNameMap;
  });
};

/**
 * 시험항목코드 → 한글명 조회 맵 생성 (최초 1회)
 * @returns {Promise<Object>} { 시험항목코드: 한글명, ... }
 */
MFDS_CODES.getTestItemNameMap = function() {
  if (_mc_testItemNameMap) return Promise.resolve(_mc_testItemNameMap);
  return MFDS_CODES.loadTestItems().then(function(items) {
    _mc_testItemNameMap = {};
    items.forEach(function(t) {
      _mc_testItemNameMap[t['시험항목코드']] = t['한글명'] || '';
    });
    return _mc_testItemNameMap;
  });
};

/**
 * 단위코드 → 단위명 조회 맵 생성 (최초 1회)
 * @returns {Promise<Object>} { 단위코드: 단위명, ... }
 */
MFDS_CODES.getUnitNameMap = function() {
  if (_mc_unitNameMap) return Promise.resolve(_mc_unitNameMap);
  return MFDS_CODES.loadUnits().then(function(units) {
    _mc_unitNameMap = {};
    units.forEach(function(u) {
      _mc_unitNameMap[u['단위코드']] = u['단위명'] || '';
    });
    return _mc_unitNameMap;
  });
};

// ============================================================
// 8. 캐시 초기화
// ============================================================

/**
 * 모든 캐시 초기화 (데이터 리로드 필요 시)
 */
MFDS_CODES.clearCache = function() {
  _mc_productCache = null;
  _mc_productCacheTime = 0;
  _mc_testItemCache = null;
  _mc_unitCache = null;
  _mc_commonCodeCache = null;
  _mc_itemMappingCache = null;
  _mc_indStdCache = null;
  _mc_cmnStdCache = null;
  _mc_productNameMap = null;
  _mc_testItemNameMap = null;
  _mc_unitNameMap = null;
  console.log('[MFDS_CODES] 캐시 초기화');
};

// ============================================================
// 9. 공통기준규격 검색 (품목코드 피커 하단)
// ============================================================

MFDS_CODES._cmnSearchCache = null;

/** 공통규격 검색 데이터 캐시 빌드 */
MFDS_CODES._loadCmnSearchData = function() {
  if (MFDS_CODES._cmnSearchCache) return Promise.resolve(MFDS_CODES._cmnSearchCache);
  return Promise.all([
    MFDS_CODES.loadCommonStandards(),
    MFDS_CODES.getTestItemNameMap(),
    MFDS_CODES.getUnitNameMap()
  ]).then(function(results) {
    var cmnData = results[0], testNameMap = results[1], unitMap = results[2];
    var seen = {};
    cmnData.forEach(function(s) {
      if (s['사용여부'] !== 'Y') return;
      var code = s['시험항목코드'] || '';
      if (!code || seen[code]) return;
      seen[code] = {
        code: code,
        name: (testNameMap && testNameMap[code]) || code,
        stdVal: s['기준규격값'] || s['기준규격값설명'] || '',
        unitCode: s['단위코드'] || '',
        unit: (unitMap && unitMap[s['단위코드']]) || s['단위코드'] || ''
      };
    });
    MFDS_CODES._cmnSearchCache = Object.values(seen);
    MFDS_CODES._cmnSearchCache.sort(function(a, b) { return a.name.localeCompare(b.name); });
    return MFDS_CODES._cmnSearchCache;
  });
};

/** 공통규격 검색 UI 이벤트 바인딩 */
MFDS_CODES._initCmnSearch = function() {
  var searchEl = document.getElementById('mfds-cmn-search');
  var resultsEl = document.getElementById('mfds-cmn-results');
  if (!searchEl || !resultsEl) return;

  var timer = null;
  searchEl.addEventListener('input', function() {
    clearTimeout(timer);
    var q = searchEl.value.trim().toLowerCase();
    if (q.length < 1) { resultsEl.style.display = 'none'; return; }
    timer = setTimeout(function() {
      MFDS_CODES._loadCmnSearchData().then(function(items) {
        var matched = items.filter(function(item) {
          return item.name.toLowerCase().indexOf(q) >= 0 || item.code.toLowerCase().indexOf(q) >= 0;
        });
        if (matched.length === 0) {
          resultsEl.innerHTML = '<div style="padding:8px 10px;color:#999;font-size:11px">검색 결과 없음</div>';
        } else {
          var regex = new RegExp('(' + q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi');
          resultsEl.innerHTML = matched.slice(0, 30).map(function(item) {
            var fee = (typeof getFeeByCode === 'function') ? getFeeByCode(item.code) : 0;
            var feeText = fee > 0 ? fee.toLocaleString() + '원' : '';
            return '<div class="mfds-cmn-item" data-code="' + item.code + '" ' +
              'style="display:flex;justify-content:space-between;align-items:center;padding:5px 10px;cursor:pointer;font-size:11px;border-bottom:1px solid #f5f5f5" ' +
              'onmouseover="this.style.background=\'#fff3e0\'" onmouseout="this.style.background=\'#fff\'">' +
              '<span>' + item.name.replace(regex, '<mark>$1</mark>') +
              ' <span style="color:#e65100;font-size:9px;background:#fff3e0;padding:0 4px;border-radius:3px">공통</span></span>' +
              '<span style="font-size:10px;color:#999;white-space:nowrap">' +
              '<span style="font-family:monospace">' + item.code + '</span>' +
              (item.stdVal ? ' · ' + item.stdVal.substring(0, 12) : '') +
              (feeText ? ' · <b style="color:#1565c0">' + feeText + '</b>' : '') +
              '</span></div>';
          }).join('');
        }
        resultsEl.style.display = 'block';
      });
    }, 200);
  });

  // 클릭 시 addCmnStdItem 호출
  resultsEl.addEventListener('click', function(e) {
    var target = e.target.closest('.mfds-cmn-item');
    if (!target) return;
    var code = target.getAttribute('data-code');
    if (typeof addCmnStdItem === 'function') {
      addCmnStdItem(code);
    } else {
      console.warn('[공통규격] addCmnStdItem 함수를 찾을 수 없습니다');
    }
    // 검색 결과 유지 (계속 추가 가능)
  });

  // 포커스 아웃 시 닫기
  searchEl.addEventListener('blur', function() {
    setTimeout(function() { resultsEl.style.display = 'none'; }, 200);
  });
};

// ============================================================
// 초기화 로그
// ============================================================
console.log('[MFDS_CODES] 식약처 코드매핑 모듈 로드 완료');
