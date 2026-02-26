/**
 * BFL LIMS - 식약처 통합LIMS WEB API 호출 모듈
 * 중간모듈(Tomcat WAR)을 통해 식약처 API를 호출하는 공통 함수
 *
 * 의존성: firebase-init.js (db 전역 변수)
 *
 * 사용법:
 * <script src="js/firebase-init.js"></script>
 * <script src="js/mfds-api.js"></script>
 * <script>
 *   window.addEventListener('firebase-ready', function() {
 *     // 공통코드 조회 예시
 *     MFDS.selectListCmmnCode().then(function(data) {
 *       console.log('업무분야코드 목록:', data);
 *     });
 *   });
 * </script>
 *
 * 아키텍처:
 *   BFL LIMS (브라우저)
 *     → nginx /mfds/ 프록시
 *       → Tomcat 8080 LMS_CLIENT_API (중간모듈)
 *         → 식약처 통합LIMS API (wslims.mfds.go.kr)
 */

// ============================================================
// 전역 네임스페이스
// ============================================================
var MFDS = MFDS || {};

// ============================================================
// 1. 기본 설정
// ============================================================

/** nginx 프록시 경로 (서버 배포 시) */
MFDS.PROXY_BASE = '/mfds';

/** 식약처 테스트 서버 URL (중간모듈이 실제 호출하는 대상) */
MFDS.WSLIMS_URL = 'https://wslims.mfds.go.kr';

/** 기본 사용자 정보 (테스트용 — 운영 시 로그인한 사용자로 교체) */
MFDS.DEFAULT_USER = {
  mfdsLimsId: 'apitest34',          // 바이오푸드랩 테스트 계정
  psitnInsttCode: 'O000170',        // 테스트 기관코드 (운영 시 O000026)
  classCode: 'IM36'                 // 식품 업무분야
};

/** API 호출 타임아웃 (밀리초) */
MFDS.TIMEOUT = 30000;

// ============================================================
// 2. 핵심 API 호출 함수
// ============================================================

/**
 * 식약처 API를 호출한다 (REST 방식).
 * 중간모듈의 selectUnitTest 엔드포인트를 통해 호출.
 *
 * @param {string} serviceName - 서비스명 (예: 'selectListCmmnCode')
 * @param {Object} params - API 파라미터 (mfdsLimsId, psitnInsttCode는 자동 포함)
 * @param {Object} [options] - 추가 옵션
 * @param {string} [options.method='rest'] - 호출 방식 ('rest' 또는 'soap')
 * @returns {Promise<Object>} 식약처 API 응답 (resultData 배열 등)
 *
 * @example
 * // 공통코드 조회
 * MFDS.callApi('selectListCmmnCode', {}).then(function(res) {
 *   console.log(res.resultData);
 * });
 *
 * // 의뢰 목록 조회
 * MFDS.callApi('selectListInspctReqest', {
 *   reqestDeStart: '20260101',
 *   reqestDeEnd: '20260226'
 * }).then(function(res) {
 *   console.log(res.resultData);
 * });
 */
MFDS.callApi = function(serviceName, params, options) {
  options = options || {};
  var method = options.method || 'rest';

  // 기본 파라미터 병합 (mfdsLimsId, psitnInsttCode, classCode)
  var fullParams = Object.assign({}, MFDS.DEFAULT_USER, params || {});

  // REST URL 생성
  var restUrl = MFDS.WSLIMS_URL + '/webService/rest/' + serviceName;

  // 중간모듈 요청 데이터
  var requestBody = {
    type: method,
    url: restUrl,
    param: JSON.stringify(fullParams)
  };

  // nginx 프록시를 통해 중간모듈 호출
  var proxyUrl = MFDS.PROXY_BASE + '/selectUnitTest';

  return new Promise(function(resolve, reject) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', proxyUrl, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.timeout = MFDS.TIMEOUT;

    xhr.onload = function() {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          var response = JSON.parse(xhr.responseText);

          // 인증 실패 체크
          if (response.resultFlag === '0' && response.validate === 'false') {
            var errorMsg = response.errorMessage || '인증 실패';
            console.error('[MFDS] 인증 오류:', errorMsg, '서비스:', serviceName);
            reject({
              type: 'AUTH_ERROR',
              message: errorMsg,
              service: serviceName
            });
            return;
          }

          // 성공
          resolve(response);
        } catch (e) {
          // 빈 응답 = 중간모듈에서 API 응답 처리 중 오류 발생 (인증 실패 가능성 높음)
          if (!xhr.responseText || xhr.responseText.trim() === '') {
            reject({
              type: 'EMPTY_RESPONSE',
              message: '빈 응답 — 중간모듈 로그 확인 필요 (인증 실패 가능성)',
              service: serviceName
            });
          } else {
            reject({
              type: 'PARSE_ERROR',
              message: '응답 파싱 실패: ' + e.message,
              raw: xhr.responseText.substring(0, 200) // 앞 200자만 표시
            });
          }
        }
      } else {
        reject({
          type: 'HTTP_ERROR',
          message: 'HTTP ' + xhr.status,
          status: xhr.status
        });
      }
    };

    xhr.onerror = function() {
      reject({
        type: 'NETWORK_ERROR',
        message: '네트워크 연결 실패 (중간모듈 서버 확인 필요)'
      });
    };

    xhr.ontimeout = function() {
      reject({
        type: 'TIMEOUT_ERROR',
        message: MFDS.TIMEOUT / 1000 + '초 초과'
      });
    };

    xhr.send(JSON.stringify(requestBody));
  });
};

// ============================================================
// 3. 주요 API 래퍼 함수 — 의뢰 관리 (01xx)
// ============================================================

/**
 * 검사의뢰 목록 조회
 * @param {Object} params - 검색 조건
 * @param {string} params.reqestDeStart - 의뢰시작일 (YYYYMMDD)
 * @param {string} params.reqestDeEnd - 의뢰종료일 (YYYYMMDD)
 * @param {string} [params.sploreReqestNo] - 의뢰번호
 * @param {string} [params.entrpsNm] - 업체명
 * @returns {Promise<Object>}
 */
MFDS.selectListInspctReqest = function(params) {
  return MFDS.callApi('selectListInspctReqest', params);
};

/**
 * 검사의뢰 등록 (저장)
 * @param {Object} params - 의뢰 데이터
 * @returns {Promise<Object>}
 */
MFDS.saveInspctReqest = function(params) {
  return MFDS.callApi('saveInspctReqest', params);
};

/**
 * 의뢰시료 저장
 * @param {Object} params - 시료 데이터
 * @returns {Promise<Object>}
 */
MFDS.saveReqestSplore = function(params) {
  return MFDS.callApi('saveReqestSplore', params);
};

/**
 * 의뢰시료 목록조회
 * @param {Object} params - 검색 조건
 * @param {string} params.sploreReqestNo - 의뢰번호
 * @returns {Promise<Object>}
 */
MFDS.selectListReqestSplore = function(params) {
  return MFDS.callApi('selectListReqestSplore', params);
};

/**
 * 시료배정 저장
 * @param {Object} params - 배정 데이터
 * @returns {Promise<Object>}
 */
MFDS.saveReqestRcept = function(params) {
  return MFDS.callApi('saveReqestRcept', params);
};

/**
 * 품목 제조 신고번호 조회
 * @param {Object} params - 검색 조건
 * @param {string} [params.prdlstNm] - 품목명
 * @param {string} [params.bsshNm] - 업소명
 * @returns {Promise<Object>}
 */
MFDS.selectListPrdItem = function(params) {
  return MFDS.callApi('selectListPrdItem', params);
};

// ============================================================
// 4. 주요 API 래퍼 함수 — 시험/결과 (02xx)
// ============================================================

/**
 * 시험일지 등록
 * @param {Object} params - 시험일지 데이터
 * @returns {Promise<Object>}
 */
MFDS.insertExprDiary = function(params) {
  return MFDS.callApi('insertExprDiary', params);
};

/**
 * 검사결과 입력 (시료별)
 * @param {Object} params - 검사결과 데이터
 * @returns {Promise<Object>}
 */
MFDS.saveSploreInspctResult = function(params) {
  return MFDS.callApi('saveSploreInspctResult', params);
};

/**
 * 결재상신
 * @param {Object} params - 결재 데이터
 * @returns {Promise<Object>}
 */
MFDS.saveSploreSanctnRecom = function(params) {
  return MFDS.callApi('saveSploreSanctnRecom', params);
};

// ============================================================
// 5. 주요 API 래퍼 함수 — 성적서 (03xx)
// ============================================================

/**
 * 성적서 발급
 * @param {Object} params - 발급 데이터
 * @returns {Promise<Object>}
 */
MFDS.saveGrdcrtIssu = function(params) {
  return MFDS.callApi('saveGrdcrtIssu', params);
};

/**
 * 성적서 발급 이력 조회
 * @param {Object} params - 검색 조건
 * @returns {Promise<Object>}
 */
MFDS.selectListGrdcrtIssuHist = function(params) {
  return MFDS.callApi('selectListGrdcrtIssuHist', params);
};

// ============================================================
// 6. 주요 API 래퍼 함수 — 진행상황 조회 (04xx)
// ============================================================

/**
 * 진행상황 조회
 * @param {Object} params - 검색 조건
 * @returns {Promise<Object>}
 */
MFDS.selectListProgrsSittn = function(params) {
  return MFDS.callApi('selectListProgrsSittn', params);
};

// ============================================================
// 7. 주요 API 래퍼 함수 — 기관/사용자 관리 (06xx)
// ============================================================

/**
 * 부서 목록 조회
 * @returns {Promise<Object>}
 */
MFDS.selectListDept = function(params) {
  return MFDS.callApi('selectListDept', params || {});
};

/**
 * 직원 목록 조회
 * @param {Object} [params] - 검색 조건
 * @returns {Promise<Object>}
 */
MFDS.selectListEmp = function(params) {
  return MFDS.callApi('selectListEmp', params || {});
};

// ============================================================
// 8. 주요 API 래퍼 함수 — 공통 조회 (08xx)
// ============================================================

/**
 * 공통코드 조회 (업무분야코드 등)
 * @param {Object} [params] - 추가 조건
 * @returns {Promise<Object>}
 */
MFDS.selectListCmmnCode = function(params) {
  return MFDS.callApi('selectListCmmnCode', params || {});
};

/**
 * 품목분류 대분류 조회
 * @param {Object} [params] - 추가 조건
 * @returns {Promise<Object>}
 */
MFDS.selectListPrdlstLclas = function(params) {
  return MFDS.callApi('selectListPrdlstLclas', params || {});
};

/**
 * 품목분류 조회
 * @param {Object} [params] - 추가 조건
 * @returns {Promise<Object>}
 */
MFDS.selectListPrdlstCl = function(params) {
  return MFDS.callApi('selectListPrdlstCl', params || {});
};

/**
 * 기관 목록 조회
 * @param {Object} [params] - 추가 조건
 * @returns {Promise<Object>}
 */
MFDS.selectListInstt = function(params) {
  return MFDS.callApi('selectListInstt', params || {});
};

/**
 * 공통기준규격종류 조회
 * @param {Object} params - 검색 조건
 * @returns {Promise<Object>}
 */
MFDS.selectListCmmnStdrStndrdKnd = function(params) {
  return MFDS.callApi('selectListCmmnStdrStndrdKnd', params || {});
};

/**
 * 공통기준규격 조회
 * @param {Object} params - 검색 조건
 * @returns {Promise<Object>}
 */
MFDS.selectListCmmnStdrStndrd = function(params) {
  return MFDS.callApi('selectListCmmnStdrStndrd', params || {});
};

// ============================================================
// 9. 유틸리티 함수
// ============================================================

/**
 * 오늘 날짜를 YYYYMMDD 형식으로 반환
 * @returns {string}
 */
MFDS.today = function() {
  var d = new Date();
  var yyyy = d.getFullYear();
  var mm = String(d.getMonth() + 1).padStart(2, '0');
  var dd = String(d.getDate()).padStart(2, '0');
  return yyyy + mm + dd;
};

/**
 * N일 전 날짜를 YYYYMMDD 형식으로 반환
 * @param {number} days - 이전 일수
 * @returns {string}
 */
MFDS.daysAgo = function(days) {
  var d = new Date();
  d.setDate(d.getDate() - days);
  var yyyy = d.getFullYear();
  var mm = String(d.getMonth() + 1).padStart(2, '0');
  var dd = String(d.getDate()).padStart(2, '0');
  return yyyy + mm + dd;
};

/**
 * API 연결 상태 테스트
 * 중간모듈에 간단한 공통코드 조회를 보내서 파이프라인 확인.
 * - 연결 성공 + 인증 성공 → { connected: true, authenticated: true }
 * - 연결 성공 + 인증 실패 → { connected: true, authenticated: false, error: '...' }
 * - 연결 실패 → { connected: false }
 *
 * @returns {Promise<Object>} 연결 상태 객체
 */
MFDS.testConnection = function() {
  var testBody = {
    type: 'rest',
    url: MFDS.WSLIMS_URL + '/webService/rest/selectListCmmnCode',
    param: JSON.stringify({
      mfdsLimsId: MFDS.DEFAULT_USER.mfdsLimsId,
      psitnInsttCode: MFDS.DEFAULT_USER.psitnInsttCode,
      classCode: MFDS.DEFAULT_USER.classCode,
      cmmnCodeClList: [{ cmmnCodeClCode: 'IM01' }]
    })
  };

  return new Promise(function(resolve) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', MFDS.PROXY_BASE + '/selectUnitTest', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.timeout = 10000;

    xhr.onload = function() {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          var res = JSON.parse(xhr.responseText);
          if (res.resultFlag === '1') {
            resolve({ connected: true, authenticated: true, data: res });
          } else {
            resolve({ connected: true, authenticated: false, error: res.errorMessage || '인증 실패' });
          }
        } catch (e) {
          // 빈 응답 = 중간모듈 연결은 됐지만 파싱 실패
          resolve({ connected: true, authenticated: false, error: '응답 파싱 실패' });
        }
      } else {
        resolve({ connected: false, error: 'HTTP ' + xhr.status });
      }
    };

    xhr.onerror = function() {
      resolve({ connected: false, error: '네트워크 오류 (중간모듈 서버 확인)' });
    };
    xhr.ontimeout = function() {
      resolve({ connected: false, error: '타임아웃 (10초)' });
    };

    xhr.send(JSON.stringify(testBody));
  });
};

/**
 * 식약처 API 호출 결과를 Firestore에 캐시 저장한다.
 * 동일한 요청을 반복하지 않도록 캐시 활용.
 *
 * @param {string} cacheKey - 캐시 키 (예: 'cmmnCode_IM36')
 * @param {Object} data - 저장할 데이터
 * @param {number} [ttlHours=24] - 캐시 유효시간 (시간 단위)
 */
MFDS.saveToCache = function(cacheKey, data, ttlHours) {
  if (typeof db === 'undefined') return;
  ttlHours = ttlHours || 24;
  var expireAt = new Date();
  expireAt.setHours(expireAt.getHours() + ttlHours);

  db.collection('mfds_cache').doc(cacheKey).set({
    data: data,
    expireAt: firebase.firestore.Timestamp.fromDate(expireAt),
    updatedAt: firebase.firestore.FieldValue.serverTimestamp()
  }).catch(function(err) {
    console.warn('[MFDS] 캐시 저장 실패:', err);
  });
};

/**
 * Firestore 캐시에서 데이터를 읽는다.
 * 유효기간이 지났으면 null 반환.
 *
 * @param {string} cacheKey - 캐시 키
 * @returns {Promise<Object|null>} 캐시된 데이터 또는 null
 */
MFDS.getFromCache = function(cacheKey) {
  if (typeof db === 'undefined') return Promise.resolve(null);

  return db.collection('mfds_cache').doc(cacheKey).get()
    .then(function(doc) {
      if (!doc.exists) return null;
      var cached = doc.data();
      // 유효기간 체크
      if (cached.expireAt && cached.expireAt.toDate() < new Date()) {
        return null; // 만료됨
      }
      return cached.data;
    })
    .catch(function() {
      return null;
    });
};

/**
 * 캐시 우선 API 호출 — 캐시에 있으면 캐시 사용, 없으면 API 호출 후 캐시 저장
 *
 * @param {string} serviceName - 서비스명
 * @param {Object} params - API 파라미터
 * @param {string} cacheKey - 캐시 키
 * @param {number} [ttlHours=24] - 캐시 유효시간
 * @returns {Promise<Object>}
 */
MFDS.callApiWithCache = function(serviceName, params, cacheKey, ttlHours) {
  return MFDS.getFromCache(cacheKey).then(function(cached) {
    if (cached) {
      console.log('[MFDS] 캐시 사용:', cacheKey);
      return cached;
    }
    return MFDS.callApi(serviceName, params).then(function(response) {
      if (response.resultFlag === '1') {
        MFDS.saveToCache(cacheKey, response, ttlHours);
      }
      return response;
    });
  });
};

// ============================================================
// 10. 초기화 로그
// ============================================================
console.log('[MFDS] 식약처 통합LIMS API 모듈 로드 완료');
console.log('[MFDS] 프록시:', MFDS.PROXY_BASE, '| 사용자:', MFDS.DEFAULT_USER.mfdsLimsId);
