"""
testResultInput.html, testDiary.html에 검사목적/검사항목 필터 및 접수번호 검색 추가
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

# ========================================
# 1. testResultInput.html 수정
# ========================================
with open('testResultInput.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1-1. toolbar-row 두번째 줄에 검사목적/검사항목 필터 추가
# 기존: 담당자 + 기간 + 건수
# 변경: 담당자 + 검사목적 + 검사항목 + 기간 + 건수
old_toolbar2 = '''        <div class="toolbar-row">
          <div class="filter-group">
            <div class="filter-label">담당자</div>
            <select id="filter-tester" class="form-select" style="width:160px" onchange="applyFilters()">
              <option value="">전체</option>
            </select>
          </div>
          <div class="filter-group">
            <div class="filter-label">기간</div>
            <input type="date" id="filter-from" onchange="applyFilters()">
            <span style="color:#aaa;font-size:12px">~</span>
            <input type="date" id="filter-to" onchange="applyFilters()">
          </div>
          <div style="margin-left:auto;font-size:12px;color:#999" id="list-count">0건</div>
        </div>'''

new_toolbar2 = '''        <div class="toolbar-row">
          <div class="filter-group">
            <div class="filter-label">담당자</div>
            <select id="filter-tester" class="form-select" style="width:120px" onchange="applyFilters()">
              <option value="">전체</option>
            </select>
          </div>
          <div class="filter-group">
            <div class="filter-label">검사목적</div>
            <select id="filter-purpose" class="form-select" style="width:150px" onchange="applyFilters()">
              <option value="">전체</option>
            </select>
          </div>
          <div class="filter-group">
            <div class="filter-label">검사항목</div>
            <select id="filter-test-item" class="form-select" style="width:130px" onchange="applyFilters()">
              <option value="">전체</option>
            </select>
          </div>
          <div class="filter-group">
            <div class="filter-label">기간</div>
            <input type="date" id="filter-from" onchange="applyFilters()">
            <span style="color:#aaa;font-size:12px">~</span>
            <input type="date" id="filter-to" onchange="applyFilters()">
          </div>
          <div style="margin-left:auto;font-size:12px;color:#999" id="list-count">0건</div>
        </div>'''

if old_toolbar2 in content:
    content = content.replace(old_toolbar2, new_toolbar2)
    print('[testResultInput] 1. 검사목적/검사항목 필터 UI 추가 완료')
else:
    print('[testResultInput] ERROR: toolbar-row 2 not found')

# 1-2. filters 상태 객체에 purpose, testItem 추가
old_filters = "var filters = { field: '전체', status: '전체', tester: '', search: '', dateFrom: '', dateTo: '' };"
new_filters = "var filters = { field: '전체', status: '전체', tester: '', purpose: '', testItem: '', search: '', dateFrom: '', dateTo: '' };"

if old_filters in content:
    content = content.replace(old_filters, new_filters)
    print('[testResultInput] 2. filters 상태 객체 업데이트 완료')
else:
    print('[testResultInput] ERROR: filters object not found')

# 1-3. applyFilters 함수 업데이트 — 검사목적/검사항목 필터 추가
old_apply = '''function applyFilters() {
  filters.tester = document.getElementById('filter-tester').value;
  filters.dateFrom = document.getElementById('filter-from').value;
  filters.dateTo = document.getElementById('filter-to').value;

  filteredReceipts = allReceipts.filter(function(r) {
    // 분야
    if (filters.field !== '전체' && r.testField !== filters.field) return false;
    // 상태: 접수완료, 시험중, 결과입력완료만 표시
    var validStatuses = ['접수완료', '시험중', '결과입력완료'];
    if (!validStatuses.includes(r.status || '')) return false;
    if (filters.status !== '전체' && r.status !== filters.status) return false;
    // 담당자
    if (filters.tester && r.testerName !== filters.tester) return false;
    // 텍스트 검색
    if (filters.search) {
      var q = filters.search;
      var haystack = ((r.receiptNo || '') + ' ' + (r.companyName || '') + ' ' + getSampleNames(r)).toLowerCase();
      if (haystack.indexOf(q) === -1) return false;
    }
    // 날짜
    var rd = r.receiptDate || '';
    if (filters.dateFrom && rd < filters.dateFrom) return false;
    if (filters.dateTo && rd > filters.dateTo) return false;
    return true;
  });

  renderReceiptList();
  document.getElementById('list-count').textContent = filteredReceipts.length + '건';
}'''

new_apply = '''function applyFilters() {
  filters.tester = document.getElementById('filter-tester').value;
  filters.purpose = document.getElementById('filter-purpose').value;
  filters.testItem = document.getElementById('filter-test-item').value;
  filters.dateFrom = document.getElementById('filter-from').value;
  filters.dateTo = document.getElementById('filter-to').value;

  filteredReceipts = allReceipts.filter(function(r) {
    // 분야
    if (filters.field !== '전체' && r.testField !== filters.field) return false;
    // 상태: 접수완료, 시험중, 결과입력완료만 표시
    var validStatuses = ['접수완료', '시험중', '결과입력완료'];
    if (!validStatuses.includes(r.status || '')) return false;
    if (filters.status !== '전체' && r.status !== filters.status) return false;
    // 담당자
    if (filters.tester && r.testerName !== filters.tester) return false;
    // 검사목적
    if (filters.purpose && (r.testPurpose || '') !== filters.purpose) return false;
    // 검사항목
    if (filters.testItem) {
      var items = getTestItemNames(r);
      if (items.toLowerCase().indexOf(filters.testItem.toLowerCase()) === -1) return false;
    }
    // 텍스트 검색 (접수번호, 거래처, 제품명)
    if (filters.search) {
      var q = filters.search;
      var haystack = ((r.receiptNo || '') + ' ' + (r.companyName || '') + ' ' + getSampleNames(r)).toLowerCase();
      if (haystack.indexOf(q) === -1) return false;
    }
    // 날짜
    var rd = r.receiptDate || '';
    if (filters.dateFrom && rd < filters.dateFrom) return false;
    if (filters.dateTo && rd > filters.dateTo) return false;
    return true;
  });

  renderReceiptList();
  document.getElementById('list-count').textContent = filteredReceipts.length + '건';
}'''

if old_apply in content:
    content = content.replace(old_apply, new_apply)
    print('[testResultInput] 3. applyFilters() 업데이트 완료')
else:
    print('[testResultInput] ERROR: applyFilters not found')

# 1-4. getSampleNames 뒤에 getTestItemNames 함수 + populateFilterDropdowns 함수 추가
old_get_sample = '''function getSampleNames(r) {
  if (!r.samples || !r.samples.length) return '';
  return r.samples.map(function(s) { return s.productName || ''; }).join(' ');
}'''

new_get_sample = '''function getSampleNames(r) {
  if (!r.samples || !r.samples.length) return '';
  return r.samples.map(function(s) { return s.productName || ''; }).join(' ');
}

function getTestItemNames(r) {
  var names = [];
  if (r.testItems && r.testItems.length) {
    r.testItems.forEach(function(ti) { if (ti.itemName) names.push(ti.itemName); });
  }
  if (r.samples && r.samples.length) {
    r.samples.forEach(function(s) {
      if (s.testItems && s.testItems.length) {
        s.testItems.forEach(function(ti) { if (ti.itemName) names.push(ti.itemName); });
      }
    });
  }
  return names.join(' ');
}

function populateFilterDropdowns() {
  // 검사목적 드롭다운
  var purposes = {};
  allReceipts.forEach(function(r) {
    if (r.testPurpose) purposes[r.testPurpose] = true;
  });
  var purposeSel = document.getElementById('filter-purpose');
  var prevPurpose = purposeSel.value;
  purposeSel.innerHTML = '<option value="">전체</option>';
  Object.keys(purposes).sort().forEach(function(p) {
    purposeSel.innerHTML += '<option value="' + p + '">' + p + '</option>';
  });
  purposeSel.value = prevPurpose;

  // 검사항목 드롭다운
  var items = {};
  allReceipts.forEach(function(r) {
    if (r.testItems && r.testItems.length) {
      r.testItems.forEach(function(ti) { if (ti.itemName) items[ti.itemName] = true; });
    }
    if (r.samples && r.samples.length) {
      r.samples.forEach(function(s) {
        if (s.testItems && s.testItems.length) {
          s.testItems.forEach(function(ti) { if (ti.itemName) items[ti.itemName] = true; });
        }
      });
    }
  });
  var itemSel = document.getElementById('filter-test-item');
  var prevItem = itemSel.value;
  itemSel.innerHTML = '<option value="">전체</option>';
  Object.keys(items).sort().forEach(function(n) {
    itemSel.innerHTML += '<option value="' + n + '">' + n + '</option>';
  });
  itemSel.value = prevItem;

  // 담당자 드롭다운
  var testers = {};
  allReceipts.forEach(function(r) { if (r.testerName) testers[r.testerName] = true; });
  var testerSel = document.getElementById('filter-tester');
  var prevTester = testerSel.value;
  testerSel.innerHTML = '<option value="">전체</option>';
  Object.keys(testers).sort().forEach(function(t) {
    testerSel.innerHTML += '<option value="' + t + '">' + t + '</option>';
  });
  testerSel.value = prevTester;
}'''

if old_get_sample in content:
    content = content.replace(old_get_sample, new_get_sample)
    print('[testResultInput] 4. getTestItemNames + populateFilterDropdowns 추가 완료')
else:
    print('[testResultInput] ERROR: getSampleNames not found')

# 1-5. loadReceipts에서 기존 담당자 드롭다운 채우기 대신 populateFilterDropdowns 호출
# 기존에 tester 드롭다운을 수동으로 채우는 코드가 있는지 확인
old_load_after = '''    applyFilters();
    updateStats();'''
new_load_after = '''    populateFilterDropdowns();
    applyFilters();
    updateStats();'''

if old_load_after in content:
    content = content.replace(old_load_after, new_load_after, 1)  # 첫 번째만
    print('[testResultInput] 5. loadReceipts에 populateFilterDropdowns 호출 추가 완료')
else:
    print('[testResultInput] ERROR: loadReceipts after section not found')

with open('testResultInput.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('[testResultInput] 저장 완료!\n')


# ========================================
# 2. testDiary.html 수정
# ========================================
with open('testDiary.html', 'r', encoding='utf-8') as f:
    content2 = f.read()

# 2-1. 툴바에 접수번호 검색 + 검사목적/검사항목 필터 추가
old_toolbar_diary = '''      <div class="toolbar">
        <div class="toolbar-row">
          <label style="font-size:12px;font-weight:600;color:#64748b">접수기간</label>
          <input type="date" id="date-from" />
          <span style="color:#999">~</span>
          <input type="date" id="date-to" />
          <select class="form-select" id="progress-filter">
            <option value="">진행상황 전체</option>
            <option value="IM04000001">접수</option>
            <option value="IM04000002">시험중</option>
            <option value="IM04000003">완료</option>
            <option value="IM04000004">결재</option>
          </select>
          <select class="form-select" id="job-filter">
            <option value="IM18000001">자체의뢰</option>
            <option value="IM18000002">외부의뢰</option>
            <option value="IM18000003">수거</option>
          </select>
          <button class="btn btn-primary btn-sm" onclick="searchSamples()">조회</button>
          <button class="btn btn-outline btn-sm" onclick="searchFromFirestore()">Firestore 조회</button>
        </div>
      </div>'''

new_toolbar_diary = '''      <div class="toolbar">
        <div class="toolbar-row">
          <label style="font-size:12px;font-weight:600;color:#64748b">접수기간</label>
          <input type="date" id="date-from" />
          <span style="color:#999">~</span>
          <input type="date" id="date-to" />
          <select class="form-select" id="progress-filter">
            <option value="">진행상황 전체</option>
            <option value="IM04000001">접수</option>
            <option value="IM04000002">시험중</option>
            <option value="IM04000003">완료</option>
            <option value="IM04000004">결재</option>
          </select>
          <select class="form-select" id="job-filter">
            <option value="IM18000001">자체의뢰</option>
            <option value="IM18000002">외부의뢰</option>
            <option value="IM18000003">수거</option>
          </select>
          <button class="btn btn-primary btn-sm" onclick="searchSamples()">조회</button>
          <button class="btn btn-outline btn-sm" onclick="searchFromFirestore()">Firestore 조회</button>
        </div>
        <div class="toolbar-row" style="gap:8px;flex-wrap:wrap">
          <input type="text" id="diary-search-input" placeholder="접수번호, 시료명, 거래처 검색..." style="padding:5px 10px;border:1px solid #cbd5e1;border-radius:6px;font-size:12px;width:220px" oninput="filterDiarySamples()">
          <select class="form-select" id="diary-filter-purpose" style="width:150px" onchange="filterDiarySamples()">
            <option value="">검사목적 전체</option>
          </select>
          <select class="form-select" id="diary-filter-item" style="width:130px" onchange="filterDiarySamples()">
            <option value="">검사항목 전체</option>
          </select>
          <span style="font-size:12px;color:#999;margin-left:auto" id="diary-filter-count"></span>
        </div>
      </div>'''

if old_toolbar_diary in content2:
    content2 = content2.replace(old_toolbar_diary, new_toolbar_diary)
    print('[testDiary] 1. 접수번호 검색 + 필터 UI 추가 완료')
else:
    print('[testDiary] ERROR: toolbar not found')

# 2-2. renderSampleList에서 필터링 로직 적용
old_render = '''function renderSampleList() {
  var el = document.getElementById('sample-list');
  document.getElementById('sample-count').textContent = allSamples.length + '건';

  if (!allSamples.length) {
    el.innerHTML = '<div class="empty-state"><div class="icon">📭</div>조회 결과가 없습니다</div>';
    return;
  }

  var html = '';
  allSamples.forEach(function(s, i) {
    var jnlCnt = parseInt(s.exprIemJnlCnt) || 0;
    var totCnt = parseInt(s.totExprIemCnt) || 0;
    var statusCls = jnlCnt > 0 ? (jnlCnt >= totCnt ? 'badge-done' : 'badge-progress') : 'badge-wait';
    var statusTxt = jnlCnt > 0 ? (jnlCnt >= totCnt ? '완료' : jnlCnt+'/'+totCnt) : '미작성';

    html += '<div class="sample-row" onclick="selectSample('+i+')" id="sample-'+i+'">';
    html += '<div class="row-top"><span class="row-no">' + (s.sploreRceptNo || '-') + '</span>';
    html += '<span class="row-status '+statusCls+'">' + statusTxt + '</span></div>';
    html += '<div class="row-bottom">';
    html += '<span>' + (s.sploreNm || s.prductNm || '-') + '</span>';
    html += '<span>' + (s.entrpsNm || '') + '</span>';
    html += '<span>' + (s.rceptDeStr || s.rceptDe || '') + '</span>';
    html += '</div></div>';
  });
  el.innerHTML = html;
}'''

new_render = '''function renderSampleList() {
  var el = document.getElementById('sample-list');
  var displayed = getFilteredSamples();
  document.getElementById('sample-count').textContent = displayed.length + '건';
  var countEl = document.getElementById('diary-filter-count');
  if (countEl) {
    if (displayed.length !== allSamples.length) {
      countEl.textContent = '필터: ' + displayed.length + '/' + allSamples.length + '건';
    } else {
      countEl.textContent = '';
    }
  }

  if (!displayed.length) {
    el.innerHTML = '<div class="empty-state"><div class="icon">📭</div>조회 결과가 없습니다</div>';
    return;
  }

  var html = '';
  displayed.forEach(function(item) {
    var s = item.sample;
    var i = item.idx;
    var jnlCnt = parseInt(s.exprIemJnlCnt) || 0;
    var totCnt = parseInt(s.totExprIemCnt) || 0;
    var statusCls = jnlCnt > 0 ? (jnlCnt >= totCnt ? 'badge-done' : 'badge-progress') : 'badge-wait';
    var statusTxt = jnlCnt > 0 ? (jnlCnt >= totCnt ? '완료' : jnlCnt+'/'+totCnt) : '미작성';

    html += '<div class="sample-row" onclick="selectSample('+i+')" id="sample-'+i+'">';
    html += '<div class="row-top"><span class="row-no">' + (s.sploreRceptNo || '-') + '</span>';
    html += '<span class="row-status '+statusCls+'">' + statusTxt + '</span></div>';
    html += '<div class="row-bottom">';
    html += '<span>' + (s.sploreNm || s.prductNm || '-') + '</span>';
    html += '<span>' + (s.entrpsNm || '') + '</span>';
    html += '<span>' + (s.rceptDeStr || s.rceptDe || '') + '</span>';
    html += '</div></div>';
  });
  el.innerHTML = html;

  // 필터 드롭다운 채우기
  populateDiaryFilterDropdowns();
}

function getFilteredSamples() {
  var searchVal = (document.getElementById('diary-search-input') || {}).value || '';
  var purposeVal = (document.getElementById('diary-filter-purpose') || {}).value || '';
  var itemVal = (document.getElementById('diary-filter-item') || {}).value || '';
  var q = searchVal.trim().toLowerCase();

  var result = [];
  allSamples.forEach(function(s, i) {
    // 텍스트 검색 (접수번호, 시료명, 거래처)
    if (q) {
      var haystack = ((s.sploreRceptNo || '') + ' ' + (s.sploreNm || '') + ' ' + (s.prductNm || '') + ' ' + (s.entrpsNm || '')).toLowerCase();
      if (haystack.indexOf(q) === -1) return;
    }
    // 검사목적 필터
    if (purposeVal) {
      var purpose = '';
      if (s._data && s._data.testPurpose) purpose = s._data.testPurpose;
      if (purpose !== purposeVal) return;
    }
    // 검사항목 필터
    if (itemVal) {
      var itemNames = getDiaryTestItemNames(s);
      if (itemNames.toLowerCase().indexOf(itemVal.toLowerCase()) === -1) return;
    }
    result.push({ sample: s, idx: i });
  });
  return result;
}

function getDiaryTestItemNames(s) {
  var names = [];
  if (s._data) {
    if (s._data.testItems && s._data.testItems.length) {
      s._data.testItems.forEach(function(ti) { if (ti.itemName) names.push(ti.itemName); });
    }
    if (s._data.samples && s._data.samples.length) {
      s._data.samples.forEach(function(sam) {
        if (sam.testItems && sam.testItems.length) {
          sam.testItems.forEach(function(ti) { if (ti.itemName) names.push(ti.itemName); });
        }
      });
    }
  }
  return names.join(' ');
}

function filterDiarySamples() {
  renderSampleList();
}

function populateDiaryFilterDropdowns() {
  // 검사목적 드롭다운
  var purposes = {};
  allSamples.forEach(function(s) {
    if (s._data && s._data.testPurpose) purposes[s._data.testPurpose] = true;
  });
  var purposeSel = document.getElementById('diary-filter-purpose');
  if (purposeSel) {
    var prev = purposeSel.value;
    var opts = '<option value="">검사목적 전체</option>';
    Object.keys(purposes).sort().forEach(function(p) {
      opts += '<option value="' + p + '"' + (p === prev ? ' selected' : '') + '>' + p + '</option>';
    });
    purposeSel.innerHTML = opts;
  }

  // 검사항목 드롭다운
  var items = {};
  allSamples.forEach(function(s) {
    if (s._data) {
      if (s._data.testItems && s._data.testItems.length) {
        s._data.testItems.forEach(function(ti) { if (ti.itemName) items[ti.itemName] = true; });
      }
      if (s._data.samples && s._data.samples.length) {
        s._data.samples.forEach(function(sam) {
          if (sam.testItems && sam.testItems.length) {
            sam.testItems.forEach(function(ti) { if (ti.itemName) items[ti.itemName] = true; });
          }
        });
      }
    }
  });
  var itemSel = document.getElementById('diary-filter-item');
  if (itemSel) {
    var prev2 = itemSel.value;
    var opts2 = '<option value="">검사항목 전체</option>';
    Object.keys(items).sort().forEach(function(n) {
      opts2 += '<option value="' + n + '"' + (n === prev2 ? ' selected' : '') + '>' + n + '</option>';
    });
    itemSel.innerHTML = opts2;
  }
}'''

if old_render in content2:
    content2 = content2.replace(old_render, new_render)
    print('[testDiary] 2. renderSampleList + 필터링 로직 추가 완료')
else:
    print('[testDiary] ERROR: renderSampleList not found')

# 2-3. searchFromFirestore에서 testPurpose 정보도 매핑에 포함
old_firestore_map = '''      return {
        _firestoreId: d.id,
        sploreRceptNo: data.receiptNo || d.id,
        sploreNm: data.productName || data.sampleName || '-',
        prductNm: data.productName || '-',
        prdlstNm: data.foodType || data.testField || '-',
        entrpsNm: data.companyName || '-',
        rceptDe: (data.receiptDate || '').replace(/-/g, ''),
        rceptDeStr: data.receiptDate || '-',
        progrsSittnCode: data.status || '-',
        exprIemJnlCnt: '0',
        totExprIemCnt: String((data.testItems || []).length),
        _firestore: true,
        _data: data
      };'''

new_firestore_map = '''      return {
        _firestoreId: d.id,
        sploreRceptNo: data.receiptNo || d.id,
        sploreNm: data.productName || data.sampleName || '-',
        prductNm: data.productName || '-',
        prdlstNm: data.foodType || data.testField || '-',
        entrpsNm: data.companyName || '-',
        rceptDe: (data.receiptDate || '').replace(/-/g, ''),
        rceptDeStr: data.receiptDate || '-',
        progrsSittnCode: data.status || '-',
        exprIemJnlCnt: '0',
        totExprIemCnt: String((data.testItems || []).length),
        testPurpose: data.testPurpose || '',
        _firestore: true,
        _data: data
      };'''

if old_firestore_map in content2:
    content2 = content2.replace(old_firestore_map, new_firestore_map)
    print('[testDiary] 3. Firestore 매핑에 testPurpose 추가 완료')
else:
    print('[testDiary] ERROR: Firestore mapping not found')

with open('testDiary.html', 'w', encoding='utf-8') as f:
    f.write(content2)
print('[testDiary] 저장 완료!')

print('\n모든 수정 완료!')
