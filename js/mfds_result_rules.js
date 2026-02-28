/**
 * 식약처 결과값 처리 규칙 유틸리티
 * - 유효자리수(validCphr) 적용
 * - 정량한계(fdqntLimit) 처리
 * - 표기값(markValue) 생성
 * - 판정형식/판정용어/최대최소 구분 코드 매핑
 *
 * 참조: 식약처 통합LIMS API 스펙
 *   I-LMS-0216 시료검사결과 저장
 *   I-LMS-0718 시험항목 저장
 *   I-LMS-0708 시험항목공통기준규격 목록조회
 */
var MFDS_RULES = (function() {

  // ── 유효자리수 적용 (반올림) ──
  function applyValidCphr(value, precision) {
    if (value === '' || value == null) return '';
    var str = String(value).trim();
    // 텍스트 값은 그대로 반환 (불검출, 음성, ND 등)
    if (isNaN(Number(str))) return str;
    var p = parseInt(precision, 10);
    if (isNaN(p) || p < 0) return str;
    return Number(str).toFixed(p);
  }

  // ── 정량한계 처리 ──
  function applyFdqntLimit(value, fdqntLimitValue, fdqntLimitBeloValue, precision) {
    var result = {
      resultValue: String(value),
      markValue: '',
      fdqntLimitApplcAt: 'N'
    };
    if (value === '' || value == null) return result;
    var str = String(value).trim();
    if (isNaN(Number(str))) {
      result.markValue = str;
      return result;
    }
    var numVal = Number(str);
    var limitVal = parseFloat(fdqntLimitValue);
    if (!isNaN(limitVal) && fdqntLimitValue !== '' && numVal < limitVal) {
      result.fdqntLimitApplcAt = 'Y';
      result.markValue = fdqntLimitBeloValue || '불검출';
    } else {
      result.fdqntLimitApplcAt = 'N';
      result.markValue = applyValidCphr(numVal, precision);
    }
    return result;
  }

  // ── 표기값 생성 ──
  function generateMarkValue(value, item) {
    if (value === '' || value == null) return '';
    var str = String(value).trim();
    // 텍스트 값 → 그대로
    if (isNaN(Number(str))) return str;
    // 정량한계가 있으면 적용
    if (item.fdqntLimitValue && item.fdqntLimitValue !== '') {
      var lResult = applyFdqntLimit(str, item.fdqntLimitValue, item.fdqntLimitBeloValue || '불검출', item.precision);
      return lResult.markValue;
    }
    // 유효자리수만 적용
    return applyValidCphr(str, item.precision);
  }

  // ── 판정형식 코드 매핑 (BFL judgmentType → IM15) ──
  var JDGMNT_FOM_MAP = {
    '최대/최소': '01',
    '적/부텍스트': '02',
    '3군법': '03',
    '2군법': '04',
    '기준없음': '05'
  };
  function mapJdgmntFomCode(judgmentType) {
    return JDGMNT_FOM_MAP[judgmentType] || '05';
  }

  // ── 판정용어 코드 매핑 (BFL judgmentResult → IM35) ──
  var JDGMNT_WORD_MAP = {
    '적합': 'IM35000001',
    '부적합': 'IM35000002',
    '상기실험확인함': 'IM35000003',
    '확인불가': 'IM35000004'
  };
  function mapJdgmntWordCode(judgmentResult) {
    return JDGMNT_WORD_MAP[judgmentResult] || '';
  }

  // ── 최대값 구분 코드 매핑 (BFL → IM16) ──
  var MAX_VALUE_SE_MAP = {
    '이하': '01',
    '미만': '02'
  };
  function mapMaxValueSeCode(maxValueCode) {
    return MAX_VALUE_SE_MAP[maxValueCode] || '';
  }

  // ── 최소값 구분 코드 매핑 (BFL → IM17) ──
  var MIN_VALUE_SE_MAP = {
    '이상': '01',
    '초과': '02'
  };
  function mapMinValueSeCode(minValueCode) {
    return MIN_VALUE_SE_MAP[minValueCode] || '';
  }

  // ── 적합/부적합 여부 코드 (sstfcYn) ──
  function mapSstfcYn(judgmentResult) {
    if (judgmentResult === '적합') return 'Y';
    if (judgmentResult === '부적합') return 'N';
    return '';
  }

  // ── 결과값 전체 처리 (입력값 → 저장/전송용 데이터) ──
  function processResultValue(rawValue, item, judgmentResult) {
    var precision = item.precision || '';
    var markValue = generateMarkValue(rawValue, item);

    // 정량한계 적용 여부
    var fdqntResult = { fdqntLimitApplcAt: 'N' };
    if (item.fdqntLimitValue && item.fdqntLimitValue !== '') {
      fdqntResult = applyFdqntLimit(rawValue, item.fdqntLimitValue, item.fdqntLimitBeloValue || '불검출', precision);
    }

    return {
      resultValue: String(rawValue || ''),
      markValue: markValue,
      validCphr: precision,
      fdqntLimitApplcAt: fdqntResult.fdqntLimitApplcAt,
      fdqntLimitValue: item.fdqntLimitValue || '',
      fdqntLimitBeloValue: item.fdqntLimitBeloValue || '',
      jdgmntFomCode: mapJdgmntFomCode(item.judgmentType),
      jdgmntWordCode: mapJdgmntWordCode(judgmentResult),
      mxmmValue: item.maxValue || '',
      mxmmValueSeCode: mapMaxValueSeCode(item.maxValueCode),
      mummValue: item.minValue || '',
      mummValueSeCode: mapMinValueSeCode(item.minValueCode),
      sstfcYn: mapSstfcYn(judgmentResult),
      unitCode: item.unit || '',
      stndrdValue: item.standard || ''
    };
  }

  // Public API
  return {
    applyValidCphr: applyValidCphr,
    applyFdqntLimit: applyFdqntLimit,
    generateMarkValue: generateMarkValue,
    mapJdgmntFomCode: mapJdgmntFomCode,
    mapJdgmntWordCode: mapJdgmntWordCode,
    mapMaxValueSeCode: mapMaxValueSeCode,
    mapMinValueSeCode: mapMinValueSeCode,
    mapSstfcYn: mapSstfcYn,
    processResultValue: processResultValue
  };

})();
