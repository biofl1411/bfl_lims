/**
 * 시험항목별 계산식 정의 및 평가 엔진
 * - 식약처 I-LMS-0210 (insertExprDiaryCalcFrmlaResult) 연동용
 * - eval() 사용 금지: 항목별 evaluate 함수를 직접 구현
 * - nomfrmCn 문자열은 표시용 + API 전송용
 */
var CALC_FORMULAS = (function() {

  // ==============================
  // 계산식 정의 (testItemCode → 수식 설정)
  // ==============================
  var FORMULAS = {

    // ── 합산형 ──

    'A40001': {
      name: 'EPA+DHA 합',
      nomfrmCn: 'X1+X2',
      calcLawSn: '',
      variables: [
        { key: 'x1', label: 'EPA (mg/g)', required: true },
        { key: 'x2', label: 'DHA (mg/g)', required: true }
      ],
      evaluate: function(v) {
        return (Number(v.x1) || 0) + (Number(v.x2) || 0);
      }
    },

    'A40029': {
      name: '진세노사이드 Rg1+Rb1+Rg3 합',
      nomfrmCn: 'X1+X2+X3',
      calcLawSn: '',
      variables: [
        { key: 'x1', label: 'Rg1 (mg/g)', required: true },
        { key: 'x2', label: 'Rb1 (mg/g)', required: true },
        { key: 'x3', label: 'Rg3 (mg/g)', required: false }
      ],
      evaluate: function(v) {
        return (Number(v.x1) || 0) + (Number(v.x2) || 0) + (Number(v.x3) || 0);
      }
    },

    'B30005': {
      name: '총 아플라톡신 (B1+B2+G1+G2)',
      nomfrmCn: 'X1+X2+X3+X4',
      calcLawSn: '',
      variables: [
        { key: 'x1', label: 'B1 (ug/kg)', required: true },
        { key: 'x2', label: 'B2 (ug/kg)', required: false },
        { key: 'x3', label: 'G1 (ug/kg)', required: false },
        { key: 'x4', label: 'G2 (ug/kg)', required: false }
      ],
      evaluate: function(v) {
        return (Number(v.x1) || 0) + (Number(v.x2) || 0) + (Number(v.x3) || 0) + (Number(v.x4) || 0);
      }
    },

    // ── 이화학 계산형 ──

    'A30030': {
      name: '산가 (Acid Value)',
      nomfrmCn: '(X1-X2)*X3*5.611/X4',
      calcLawSn: '',
      variables: [
        { key: 'x1', label: '본시험 적정량 (mL)', required: true },
        { key: 'x2', label: '공시험 적정량 (mL)', required: true },
        { key: 'x3', label: '0.1N KOH 역가 (f)', required: true },
        { key: 'x4', label: '시료량 (g)', required: true }
      ],
      evaluate: function(v) {
        var x1 = Number(v.x1) || 0, x2 = Number(v.x2) || 0;
        var x3 = Number(v.x3) || 0, x4 = Number(v.x4) || 0;
        if (x4 === 0) return 0;
        return (x1 - x2) * x3 * 5.611 / x4;
      }
    },

    'A30023': {
      name: '과산화물가 (Peroxide Value)',
      nomfrmCn: '(X1-X2)*X3*10/X4',
      calcLawSn: '',
      variables: [
        { key: 'x1', label: '본시험 Na₂S₂O₃ 적정량 (mL)', required: true },
        { key: 'x2', label: '공시험 Na₂S₂O₃ 적정량 (mL)', required: true },
        { key: 'x3', label: 'Na₂S₂O₃ 역가 (f)', required: true },
        { key: 'x4', label: '시료량 (g)', required: true }
      ],
      evaluate: function(v) {
        var x1 = Number(v.x1) || 0, x2 = Number(v.x2) || 0;
        var x3 = Number(v.x3) || 0, x4 = Number(v.x4) || 0;
        if (x4 === 0) return 0;
        return (x1 - x2) * x3 * 10 / x4;
      }
    },

    'A10020': {
      name: '수분 (Moisture)',
      nomfrmCn: '(X1-X2)/X1*100',
      calcLawSn: '',
      variables: [
        { key: 'x1', label: '건조 전 시료 중량 (g)', required: true },
        { key: 'x2', label: '건조 후 시료 중량 (g)', required: true }
      ],
      evaluate: function(v) {
        var x1 = Number(v.x1) || 0, x2 = Number(v.x2) || 0;
        if (x1 === 0) return 0;
        return (x1 - x2) / x1 * 100;
      }
    },

    'A10050': {
      name: '회분 (Ash)',
      nomfrmCn: '(X2-X3)/(X1-X3)*100',
      calcLawSn: '',
      variables: [
        { key: 'x1', label: '시료 + 도가니 중량 (g)', required: true },
        { key: 'x2', label: '회화 후 도가니 + 회분 중량 (g)', required: true },
        { key: 'x3', label: '빈 도가니 중량 (g)', required: true }
      ],
      evaluate: function(v) {
        var x1 = Number(v.x1) || 0, x2 = Number(v.x2) || 0, x3 = Number(v.x3) || 0;
        var denom = x1 - x3;
        if (denom === 0) return 0;
        return (x2 - x3) / denom * 100;
      }
    },

    'A10058': {
      name: '휘발성염기질소 (VBN)',
      nomfrmCn: '(X1-X2)*X3*14.007/X4*100',
      calcLawSn: '',
      variables: [
        { key: 'x1', label: '본시험 0.02N H₂SO₄ 적정량 (mL)', required: true },
        { key: 'x2', label: '공시험 0.02N H₂SO₄ 적정량 (mL)', required: true },
        { key: 'x3', label: 'H₂SO₄ 역가 (f)', required: true },
        { key: 'x4', label: '시료량 (g)', required: true }
      ],
      evaluate: function(v) {
        var x1 = Number(v.x1) || 0, x2 = Number(v.x2) || 0;
        var x3 = Number(v.x3) || 0, x4 = Number(v.x4) || 0;
        if (x4 === 0) return 0;
        return (x1 - x2) * x3 * 14.007 / x4 * 100;
      }
    },

    'A20012': {
      name: '조단백질 (Crude Protein, Kjeldahl)',
      nomfrmCn: '(X1-X2)*0.02*14.007*X3/X4*100',
      calcLawSn: '',
      variables: [
        { key: 'x1', label: '본시험 0.02N NaOH 적정량 (mL)', required: true },
        { key: 'x2', label: '공시험 0.02N NaOH 적정량 (mL)', required: true },
        { key: 'x3', label: '질소계수 (N factor)', required: true },
        { key: 'x4', label: '시료량 (g)', required: true }
      ],
      evaluate: function(v) {
        var x1 = Number(v.x1) || 0, x2 = Number(v.x2) || 0;
        var x3 = Number(v.x3) || 0, x4 = Number(v.x4) || 0;
        if (x4 === 0) return 0;
        return (x1 - x2) * 0.02 * 14.007 * x3 / x4 * 100;
      }
    }
  };

  // ==============================
  // Public API
  // ==============================

  /** 해당 항목코드의 수식 설정 반환 (없으면 null) */
  function getFormula(testItemCode) {
    return FORMULAS[testItemCode] || null;
  }

  /** 수식이 정의되어 있는지 여부 */
  function hasFormula(testItemCode) {
    return !!FORMULAS[testItemCode];
  }

  /** 안전한 계산 실행 (eval 사용 안함) */
  function evaluate(testItemCode, variableValues) {
    var formula = FORMULAS[testItemCode];
    if (!formula || typeof formula.evaluate !== 'function') return null;
    try {
      return formula.evaluate(variableValues);
    } catch (e) {
      console.error('계산식 평가 오류:', testItemCode, e);
      return null;
    }
  }

  /** x1~x15 API용 insertList 객체 생성 */
  function buildInsertList(variableValues) {
    var list = {};
    for (var i = 1; i <= 15; i++) {
      list['x' + i] = String(variableValues['x' + i] || '');
    }
    return list;
  }

  /** I-LMS-0210 전체 API 파라미터 구성 */
  function buildCalcApiParams(receipt, sampleIdx, exprIemSn, testItemCode, variableValues, resultValue, exprDiarySn) {
    var formula = FORMULAS[testItemCode];
    if (!formula) return null;
    var sploreReqestNo = receipt.sploreReqestNo || receipt.receiptNo;
    var sploreSn = String(sampleIdx + 1);
    return {
      jobSeCode: 'IM18000001',
      webApi: 'Y',
      sploreReqestNo: sploreReqestNo,
      sploreSn: sploreSn,
      value: {
        sploreReqestNo: sploreReqestNo,
        sploreSn: sploreSn,
        exprIemSn: String(exprIemSn),
        calcLawSn: formula.calcLawSn || '',
        resultValue: String(resultValue),
        nomfrmNm: formula.name || '',
        nomfrmCn: formula.nomfrmCn || '',
        validCphr: ''
      },
      insertList: [buildInsertList(variableValues)],
      exprDiarySn: exprDiarySn || ''
    };
  }

  /** 수식이 정의된 항목 코드 목록 */
  function getAllFormulaCodes() {
    return Object.keys(FORMULAS);
  }

  return {
    getFormula: getFormula,
    hasFormula: hasFormula,
    evaluate: evaluate,
    buildInsertList: buildInsertList,
    buildCalcApiParams: buildCalcApiParams,
    getAllFormulaCodes: getAllFormulaCodes
  };

})();
