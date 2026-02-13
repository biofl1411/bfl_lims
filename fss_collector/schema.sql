-- ============================================================
-- BioFoodLab 식약처 인허가 데이터 수집 DB
-- MariaDB / MySQL
-- 생성일: 2026-02-14
-- ============================================================

CREATE DATABASE IF NOT EXISTS fss_data
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE fss_data;

-- ============================================================
-- 1. 업소 인허가 대장 (9개 API 통합)
-- ============================================================
-- I1220  식품제조가공업
-- I2829  즉석판매제조가공업
-- I-0020 건강기능식품 전문/벤처제조업
-- I1300  축산물 가공업
-- I1320  축산물 식육포장처리업
-- I2835  식육즉석판매가공업
-- I2831  식품소분업
-- C001   수입식품등영업신고
-- I1260  식품등수입판매업
-- ============================================================

CREATE TABLE IF NOT EXISTS fss_businesses (
  id            BIGINT AUTO_INCREMENT PRIMARY KEY,
  api_source    VARCHAR(10)   NOT NULL COMMENT 'API 서비스ID (I1220, I2829 등)',
  lcns_no       VARCHAR(50)   NOT NULL COMMENT '인허가번호',
  bssh_nm       VARCHAR(200)  NOT NULL COMMENT '업소명',
  prsdnt_nm     VARCHAR(100)  DEFAULT NULL COMMENT '대표자명',
  induty_nm     VARCHAR(100)  DEFAULT NULL COMMENT '업종',
  prms_dt       VARCHAR(20)   DEFAULT NULL COMMENT '허가일자',
  telno         VARCHAR(50)   DEFAULT NULL COMMENT '전화번호',
  locp_addr     VARCHAR(500)  DEFAULT NULL COMMENT '주소(원본)',
  instt_nm      VARCHAR(100)  DEFAULT NULL COMMENT '기관명',
  clsbiz_dvs_nm VARCHAR(50)   DEFAULT NULL COMMENT '영업상태',

  -- 주소 파싱 결과 (지역 검색용)
  addr_sido     VARCHAR(20)   DEFAULT NULL COMMENT '시도',
  addr_sigungu  VARCHAR(30)   DEFAULT NULL COMMENT '시군구',
  addr_dong     VARCHAR(30)   DEFAULT NULL COMMENT '읍면동',

  collected_at  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '수집일시',
  updated_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  UNIQUE KEY uq_biz (api_source, lcns_no),
  INDEX idx_sido (addr_sido),
  INDEX idx_sigungu (addr_sido, addr_sigungu),
  INDEX idx_dong (addr_sido, addr_sigungu, addr_dong),
  INDEX idx_bssh_nm (bssh_nm),
  INDEX idx_induty (induty_nm),
  INDEX idx_api (api_source),
  INDEX idx_instt (instt_nm)
) ENGINE=InnoDB COMMENT='업소 인허가 대장 (9개 API 통합)';


-- ============================================================
-- 2. 품목 제조 보고 (3개 API 통합)
-- ============================================================
-- I1250  식품(첨가물)품목제조보고
-- I1310  축산물 품목제조정보
-- C003   건강기능식품 품목제조신고(원재료) → 여기는 원재료 포함
-- ============================================================

CREATE TABLE IF NOT EXISTS fss_products (
  id                BIGINT AUTO_INCREMENT PRIMARY KEY,
  api_source        VARCHAR(10)   NOT NULL COMMENT 'API 서비스ID',
  lcns_no           VARCHAR(50)   NOT NULL COMMENT '인허가번호',
  bssh_nm           VARCHAR(200)  DEFAULT NULL COMMENT '업소명',
  prdlst_report_no  VARCHAR(50)   DEFAULT NULL COMMENT '품목제조번호',
  prms_dt           VARCHAR(20)   DEFAULT NULL COMMENT '보고/허가일자',
  prdlst_nm         VARCHAR(500)  DEFAULT NULL COMMENT '제품명/품목명',
  prdlst_dcnm       VARCHAR(200)  DEFAULT NULL COMMENT '품목유형명',
  production        VARCHAR(10)   DEFAULT NULL COMMENT '생산종료여부',
  hieng_lntrt_dvs_nm VARCHAR(10)  DEFAULT NULL COMMENT '고열량저영양식품여부',
  child_crtfc_yn    VARCHAR(10)   DEFAULT NULL COMMENT '어린이기호식품품질인증',
  pog_daycnt        VARCHAR(100)  DEFAULT NULL COMMENT '소비기한',
  induty_cd_nm      VARCHAR(100)  DEFAULT NULL COMMENT '업종',
  dispos            VARCHAR(200)  DEFAULT NULL COMMENT '성상/제품형태',
  shap              VARCHAR(100)  DEFAULT NULL COMMENT '형태',
  stdr_stnd         TEXT          DEFAULT NULL COMMENT '기준규격',
  ntk_mthd          TEXT          DEFAULT NULL COMMENT '섭취방법',
  primary_fnclty    TEXT          DEFAULT NULL COMMENT '주된기능성',
  iftkn_atnt_matr_cn TEXT         DEFAULT NULL COMMENT '섭취시주의사항',
  cstdy_mthd        VARCHAR(200)  DEFAULT NULL COMMENT '보관방법',
  prdt_shap_cd_nm   VARCHAR(50)   DEFAULT NULL COMMENT '제품형태코드명',
  usage_info        TEXT          DEFAULT NULL COMMENT '용법',
  prpos             TEXT          DEFAULT NULL COMMENT '용도',
  frmlc_mtrqlt      VARCHAR(200)  DEFAULT NULL COMMENT '포장재질',
  qlity_mntnc       VARCHAR(100)  DEFAULT NULL COMMENT '품질유지기한일수',
  etqty_xport       VARCHAR(10)   DEFAULT NULL COMMENT '내수/겸용구분',
  last_updt_dtm     VARCHAR(30)   DEFAULT NULL COMMENT '최종수정일시',

  collected_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at        DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  UNIQUE KEY uq_prd (api_source, prdlst_report_no),
  INDEX idx_prd_lcns (lcns_no),
  INDEX idx_prd_bssh (bssh_nm),
  INDEX idx_prd_nm (prdlst_nm(100)),
  INDEX idx_prd_type (prdlst_dcnm),
  INDEX idx_prd_api (api_source)
) ENGINE=InnoDB COMMENT='품목 제조 보고 (3개 API 통합)';


-- ============================================================
-- 3. 원재료 정보 (3개 API 통합)
-- ============================================================
-- C002   식품(첨가물)품목제조보고(원재료)
-- C003   건강기능식품 품목제조신고(원재료)
-- C006   축산물품목제조보고(원재료)
-- ============================================================

CREATE TABLE IF NOT EXISTS fss_materials (
  id                BIGINT AUTO_INCREMENT PRIMARY KEY,
  api_source        VARCHAR(10)   NOT NULL COMMENT 'API 서비스ID',
  lcns_no           VARCHAR(50)   DEFAULT NULL COMMENT '인허가번호',
  bssh_nm           VARCHAR(200)  DEFAULT NULL COMMENT '업소명',
  prdlst_report_no  VARCHAR(50)   DEFAULT NULL COMMENT '품목제조번호',
  prms_dt           VARCHAR(20)   DEFAULT NULL COMMENT '보고일자',
  prdlst_nm         VARCHAR(500)  DEFAULT NULL COMMENT '품목명',
  prdlst_dcnm       VARCHAR(200)  DEFAULT NULL COMMENT '품목유형명',
  rawmtrl_nm        TEXT          DEFAULT NULL COMMENT '원재료명',
  rawmtrl_ordno     VARCHAR(10)   DEFAULT NULL COMMENT '원재료표시순서',
  chng_dt           VARCHAR(20)   DEFAULT NULL COMMENT '변경일자',
  etqty_xport       VARCHAR(10)   DEFAULT NULL COMMENT '내수/겸용구분',

  collected_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,

  UNIQUE KEY uq_mat (api_source, prdlst_report_no, rawmtrl_ordno),
  INDEX idx_mat_lcns (lcns_no),
  INDEX idx_mat_prd (prdlst_report_no),
  INDEX idx_mat_bssh (bssh_nm),
  INDEX idx_mat_raw (rawmtrl_nm(100))
) ENGINE=InnoDB COMMENT='원재료 정보 (3개 API 통합)';


-- ============================================================
-- 4. 인허가 변경 이력 (2개 API 통합)
-- ============================================================
-- I2859  식품업소 인허가 변경 정보
-- I2860  건강기능식품업소 인허가 변경 정보
-- ============================================================

CREATE TABLE IF NOT EXISTS fss_changes (
  id            BIGINT AUTO_INCREMENT PRIMARY KEY,
  api_source    VARCHAR(10)   NOT NULL COMMENT 'API 서비스ID',
  lcns_no       VARCHAR(50)   NOT NULL COMMENT '인허가번호',
  bssh_nm       VARCHAR(200)  DEFAULT NULL COMMENT '업소명',
  induty_cd_nm  VARCHAR(100)  DEFAULT NULL COMMENT '업종명',
  telno         VARCHAR(50)   DEFAULT NULL COMMENT '전화번호',
  site_addr     VARCHAR(500)  DEFAULT NULL COMMENT '주소',
  chng_dt       VARCHAR(20)   DEFAULT NULL COMMENT '변경일자',
  chng_bf_cn    TEXT          DEFAULT NULL COMMENT '변경전내용',
  chng_af_cn    TEXT          DEFAULT NULL COMMENT '변경후내용',
  chng_prvns    TEXT          DEFAULT NULL COMMENT '변경사유',

  collected_at  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,

  INDEX idx_chg_lcns (lcns_no),
  INDEX idx_chg_bssh (bssh_nm),
  INDEX idx_chg_dt (chng_dt),
  INDEX idx_chg_api (api_source)
) ENGINE=InnoDB COMMENT='인허가 변경 이력 (2개 API 통합)';


-- ============================================================
-- 5. 수집 로그
-- ============================================================

CREATE TABLE IF NOT EXISTS fss_collect_log (
  id            BIGINT AUTO_INCREMENT PRIMARY KEY,
  api_source    VARCHAR(10)   NOT NULL,
  api_name      VARCHAR(100)  DEFAULT NULL COMMENT 'API 이름',
  collect_type  VARCHAR(20)   NOT NULL COMMENT 'full / incremental',
  total_count   INT           DEFAULT 0 COMMENT 'API 총 건수',
  fetched_count INT           DEFAULT 0 COMMENT '수집 건수',
  inserted_count INT          DEFAULT 0 COMMENT '신규 입력',
  updated_count INT           DEFAULT 0 COMMENT '업데이트',
  error_count   INT           DEFAULT 0 COMMENT '오류 건수',
  error_msg     TEXT          DEFAULT NULL,
  started_at    DATETIME      NOT NULL,
  finished_at   DATETIME      DEFAULT NULL,
  duration_sec  INT           DEFAULT NULL COMMENT '소요시간(초)',

  INDEX idx_log_api (api_source),
  INDEX idx_log_date (started_at)
) ENGINE=InnoDB COMMENT='수집 이력 로그';


-- ============================================================
-- 6. 수집 설정 (관리자 메뉴용)
-- ============================================================

CREATE TABLE IF NOT EXISTS fss_api_config (
  api_source    VARCHAR(10)   PRIMARY KEY COMMENT 'API 서비스ID',
  api_name      VARCHAR(100)  NOT NULL COMMENT 'API 이름',
  category      VARCHAR(20)   NOT NULL COMMENT '카테고리 (업소인허가/품목제조/원재료/변경이력)',
  is_enabled    TINYINT(1)    NOT NULL DEFAULT 1 COMMENT '수집 여부 (0=비활성, 1=활성)',
  enabled_fields TEXT         DEFAULT NULL COMMENT '수집할 필드 목록 (JSON 배열)',
  all_fields    TEXT          DEFAULT NULL COMMENT '전체 필드 목록 (JSON 배열 [{key,label}])',
  total_count   INT           DEFAULT 0 COMMENT '최근 API 총 건수',
  last_collected DATETIME    DEFAULT NULL COMMENT '최근 수집 일시',
  memo          VARCHAR(500)  DEFAULT NULL COMMENT '관리자 메모',
  updated_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='API 수집 설정';


CREATE TABLE IF NOT EXISTS fss_schedule_config (
  id            INT           PRIMARY KEY DEFAULT 1,
  collect_hour  INT           NOT NULL DEFAULT 3 COMMENT '수집 시각 (KST 0-23시)',
  collect_minute INT          NOT NULL DEFAULT 0 COMMENT '수집 분 (0-59)',
  collect_mode  VARCHAR(20)   NOT NULL DEFAULT 'incremental' COMMENT '수집 모드 (full/incremental)',
  is_active     TINYINT(1)    NOT NULL DEFAULT 1 COMMENT '자동 수집 활성화',
  api_key       VARCHAR(100)  NOT NULL DEFAULT 'e5a1d9f07d6c4424a757' COMMENT '식약처 API 키',
  batch_size    INT           NOT NULL DEFAULT 100 COMMENT '1회 요청 건수',
  request_delay DECIMAL(3,1)  NOT NULL DEFAULT 0.3 COMMENT 'API 요청 간격(초)',
  updated_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  updated_by    VARCHAR(50)   DEFAULT NULL
) ENGINE=InnoDB COMMENT='수집 스케줄 설정';

INSERT IGNORE INTO fss_schedule_config (id) VALUES (1);


-- ============================================================
-- 7. 뷰: 업소+품목 통합 조회용
-- ============================================================

CREATE OR REPLACE VIEW v_business_summary AS
SELECT
  b.api_source,
  CASE b.api_source
    WHEN 'I1220'  THEN '식품제조가공업'
    WHEN 'I2829'  THEN '즉석판매제조가공업'
    WHEN 'I-0020' THEN '건강기능식품제조업'
    WHEN 'I1300'  THEN '축산물가공업'
    WHEN 'I1320'  THEN '축산물식육포장처리업'
    WHEN 'I2835'  THEN '식육즉석판매가공업'
    WHEN 'I2831'  THEN '식품소분업'
    WHEN 'C001'   THEN '수입식품등영업신고'
    WHEN 'I1260'  THEN '식품등수입판매업'
    ELSE b.api_source
  END AS api_name,
  b.lcns_no,
  b.bssh_nm,
  b.prsdnt_nm,
  b.induty_nm,
  b.prms_dt,
  b.telno,
  b.locp_addr,
  b.instt_nm,
  b.addr_sido,
  b.addr_sigungu,
  b.addr_dong,
  (SELECT COUNT(*) FROM fss_products p WHERE p.lcns_no = b.lcns_no) AS product_count,
  (SELECT COUNT(*) FROM fss_changes c WHERE c.lcns_no = b.lcns_no) AS change_count
FROM fss_businesses b;
