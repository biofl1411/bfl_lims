/**
 * 등급 자동 산출 공통 모듈
 * companyMgmt.html, salesMgmt.html, receiptStatus.html 에서 공통 사용
 */

var _gradeCalcCache = {
  rules: null,
  userDeptMap: null
};

/** Firestore에서 등급 규칙 로드 (캐시) */
async function gradeCalcLoadRules() {
  if (_gradeCalcCache.rules) return _gradeCalcCache.rules;
  try {
    var r = await fsGetSettings('gradeRules');
    if (r && (r.grades || r.gradeThresholds)) {
      _gradeCalcCache.rules = r;
      return r;
    }
  } catch(e) { console.warn('[등급] Firestore 규칙 로드 실패:', e.message); }
  // 기본값
  _gradeCalcCache.rules = {
    grades: [
      { name:'VIP', min:90 }, { name:'A', min:70 }, { name:'B', min:50 },
      { name:'C', min:30 }, { name:'D', min:15 }, { name:'F', min:0 }
    ],
    gradeThresholds: { vip:90, a:70, b:50 },
    revenue: { scores:[5,10,20,30,40], thresholds:[1000,3000,5000,10000] },
    frequency: { scores:[5,10,15,20,25], thresholds:[1,3,5,10] },
    duration: { scores:[3,6,9,12,15], thresholds:[1,2,3,5] },
    payment: { scores:[3,6,9,12,15], conditions:['위험','경고','주의','양호','정상'] },
    department: { scores:[1,3,5], conditions:['지사','고객관리','고객지원팀, 마케팅사업부'] },
    receiptType: { scores:[3,5], conditions:['일반','홈페이지'] },
    sampleMove: { scores:[3,5], conditions:['일반물류','바이오물류'] },
    sampleReceipt: { scores:[1,2,3,4,5], conditions:['일반물류','택배','방문','내방','바이오물류'] }
  };
  return _gradeCalcCache.rules;
}

/** 사용자 이름 → 부서 매핑 로드 */
async function gradeCalcLoadUserDeptMap() {
  if (_gradeCalcCache.userDeptMap) return _gradeCalcCache.userDeptMap;
  _gradeCalcCache.userDeptMap = {};
  try {
    var users = await fsGetUsers();
    (users || []).forEach(function(u) {
      var name = u.name || u['아이디'] || '';
      var dept = u.department || u['부서명'] || '';
      if (name && dept) _gradeCalcCache.userDeptMap[name] = dept;
    });
  } catch(e) { console.warn('[등급] 사용자 부서 매핑 로드 실패:', e.message); }
  return _gradeCalcCache.userDeptMap;
}

/** 영업담당이 사람 이름이면 부서로 변환 */
function gradeResolveDept(salesRep) {
  if (!salesRep || !_gradeCalcCache.userDeptMap) return salesRep;
  if (/(팀|부|실|과|사업부|센터)$/.test(salesRep)) return salesRep;
  return _gradeCalcCache.userDeptMap[salesRep] || salesRep;
}

/** 조건 매칭 (하위 부서 포함, 콤마 구분 복수 조건) */
function gradeMatchCondition(ruleObj, value) {
  if (!ruleObj || !value) return { score: 0, max: 0, matched: '없음' };
  var scores = ruleObj.scores || [];
  var conds = ruleObj.conditions || [];
  var maxScore = scores.length ? Math.max.apply(null, scores) : 0;
  var nVal = (value || '').replace(/[\s,·]/g, '').toLowerCase();
  if (!nVal) return { score: 0, max: maxScore, matched: '없음' };

  var sorted = conds.map(function(c, i) { return { c: c, s: scores[i] || 0 }; })
    .sort(function(a, b) { return b.s - a.s; });

  for (var i = 0; i < sorted.length; i++) {
    var parts = sorted[i].c.split(/[,，]/).map(function(p) { return p.replace(/\s/g, '').toLowerCase(); });
    for (var j = 0; j < parts.length; j++) {
      if (!parts[j]) continue;
      if (parts[j] === nVal) return { score: sorted[i].s, max: maxScore, matched: sorted[i].c };
      var coreVal = nVal.replace(/(팀|부|실|과|사업부|센터)$/, '');
      var coreCond = parts[j].replace(/(팀|부|실|과|사업부|센터)$/, '');
      if (coreVal && coreCond && (coreVal.indexOf(coreCond) >= 0 || coreCond.indexOf(coreVal) >= 0)) {
        return { score: sorted[i].s, max: maxScore, matched: sorted[i].c };
      }
    }
  }
  return { score: 0, max: maxScore, matched: '미매칭: ' + value };
}

/** threshold 기반 점수 계산 (1~3번 매출/빈도/기간) */
function gradeCalcThreshold(ruleObj, val) {
  if (!ruleObj) return { score: 0, max: 0 };
  var scores = ruleObj.scores || [0];
  var thresholds = ruleObj.thresholds || [];
  var maxS = scores.length ? Math.max.apply(null, scores) : 0;
  // 값이 0이면 무조건 0점 (접수 데이터 없음)
  if (!val || val <= 0) return { score: 0, max: maxS };
  if (thresholds.length > 0) {
    var sc = scores[0] || 0;
    for (var i = thresholds.length - 1; i >= 0; i--) {
      if (val >= thresholds[i]) { sc = scores[i + 1] || scores[i] || 0; break; }
    }
    return { score: sc, max: maxS };
  }
  return { score: scores[0] || 0, max: maxS };
}

/**
 * 등급 산출 (통합 함수)
 * @param {Object} company - 업체 데이터 (salesRep, trafficLight 등)
 * @param {Object} [stats] - 접수 통계 (annualRevenue, monthlyFrequency, tradeDuration 등)
 * @returns {Object} { grade, score, detail }
 */
async function gradeCalcCompany(company, stats) {
  try {
    var rules = await gradeCalcLoadRules();
    await gradeCalcLoadUserDeptMap();
    stats = stats || {};
    var details = {};
    var total = 0;

    // 1. 연간 매출액
    var revVal = stats.annualRevenue || company.annualRevenue || 0;
    var rev = gradeCalcThreshold(rules.revenue, revVal);
    details.revenue = { label: '연간매출액', value: revVal + '만원', score: rev.score, max: rev.max };
    total += rev.score;

    // 2. 거래 빈도
    var freqVal = stats.monthlyFrequency || company.monthlyFrequency || 0;
    var freq = gradeCalcThreshold(rules.frequency, freqVal);
    details.frequency = { label: '거래빈도', value: '월 ' + freqVal + '건', score: freq.score, max: freq.max };
    total += freq.score;

    // 3. 거래 기간
    var durVal = stats.tradeDuration || company.tradeDuration || 0;
    var dur = gradeCalcThreshold(rules.duration, durVal);
    details.duration = { label: '거래기간', value: durVal + '년', score: dur.score, max: dur.max };
    total += dur.score;

    // 4. 결제 신뢰도 (신호등)
    var tl = stats.trafficLight || company.trafficLight || 'blue';
    var tlLabels = { green: '정상', blue: '양호', yellow: '주의', orange: '경고', red: '위험' };
    var tlLabel = tlLabels[tl] || '정상';
    var pay = rules.payment || { scores: [3,6,9,12,15], conditions: ['위험','경고','주의','양호','정상'] };
    var payResult = gradeMatchCondition(pay, tlLabel);
    details.payment = { label: '결제신뢰도', value: tlLabel, score: payResult.score, max: payResult.max };
    total += payResult.score;

    // 5. 담당부서 (이름→부서 변환)
    var salesRep = company.salesRep || '';
    var deptName = gradeResolveDept(salesRep);
    var deptResult = gradeMatchCondition(rules.department, deptName);
    details.department = { label: '담당부서', value: salesRep + (deptName !== salesRep ? '→' + deptName : ''), score: deptResult.score, max: deptResult.max };
    total += deptResult.score;

    // 6. 접수형태
    var formType = stats.receiptFormType || company.receiptType || '';
    var rcptResult = gradeMatchCondition(rules.receiptType, formType);
    details.receiptType = { label: '접수형태', value: formType || '없음', score: rcptResult.score, max: rcptResult.max };
    total += rcptResult.score;

    // 7. 시료 이동
    var moveType = stats.sampleMoveType || '';
    var moveResult = gradeMatchCondition(rules.sampleMove, moveType);
    details.sampleMove = { label: '시료이동', value: moveType || '없음', score: moveResult.score, max: moveResult.max };
    total += moveResult.score;

    // 8. 시료접수
    var sampleType = stats.sampleReceiveType || '';
    var sampleResult = gradeMatchCondition(rules.sampleReceipt, sampleType);
    details.sampleReceipt = { label: '시료접수', value: sampleType || '없음', score: sampleResult.score, max: sampleResult.max };
    total += sampleResult.score;

    // 등급 판정
    var grade = 'F';
    if (rules.grades && rules.grades.length > 0) {
      var sortedG = rules.grades.slice().sort(function(a, b) { return b.min - a.min; });
      for (var gi = 0; gi < sortedG.length; gi++) {
        if (total >= sortedG[gi].min) { grade = sortedG[gi].name; break; }
      }
    } else {
      var th = rules.gradeThresholds || { vip: 90, a: 70, b: 50 };
      if (total >= th.vip) grade = 'VIP';
      else if (total >= th.a) grade = 'A';
      else if (total >= th.b) grade = 'B';
      else grade = 'C';
    }

    // 상세 문자열
    var detailStr = Object.keys(details).map(function(k) {
      var d = details[k];
      return d.label + ': ' + d.score + '/' + d.max + ' (' + d.value + ')';
    }).join('\n');

    return { grade: grade, score: total, detail: detailStr, details: details };
  } catch(e) {
    console.error('[등급] 계산 오류:', e.message);
    return { grade: 'F', score: 0, detail: '계산 오류', details: {} };
  }
}

/** 등급 뱃지 HTML 생성 */
function gradeRenderBadge(grade, score, detailStr) {
  var colors = {
    'VIP': { bg: '#fce4ec', color: '#c62828' },
    'A': { bg: '#e8f5e9', color: '#2e7d32' },
    'B': { bg: '#e3f2fd', color: '#1565c0' },
    'C': { bg: '#fff3e0', color: '#e65100' },
    'D': { bg: '#f3e5f5', color: '#7b1fa2' },
    'F': { bg: '#f5f5f5', color: '#616161' }
  };
  var c = colors[grade] || colors['F'];
  var tip = detailStr ? ' title="' + (detailStr || '').replace(/"/g, '&quot;') + '"' : '';
  return '<span class="tag" style="background:' + c.bg + ';color:' + c.color + ';cursor:help"' + tip + '>' + grade + '</span>' +
    (score != null ? '<span style="font-size:9px;color:#999;display:block">(' + score + '점)</span>' : '');
}
