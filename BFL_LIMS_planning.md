# BFL LIMS 프로그램 기획서

**BioFoodLab Laboratory Information Management System**

---

## 📋 문서 정보

- **프로젝트명**: BFL LIMS (BioFoodLab 실험실 정보 관리 시스템)
- **작성일**: 2026년 2월 16일
- **버전**: v2.0
- **최종 업데이트**: 2026년 2월 19일
- **작성자**: BioFoodLab
- **목적**: 식품 검사 실험실의 업무 효율화 및 데이터 관리 체계화

---

## 📌 목차

1. [프로젝트 개요](#1-프로젝트-개요)
2. [시스템 아키텍처](#2-시스템-아키텍처)
3. [페이지 구성 및 연결 구조](#3-페이지-구성-및-연결-구조)
4. [공통 모듈: 통합 사이드바](#4-공통-모듈-통합-사이드바)
5. [각 페이지 상세 기능](#5-각-페이지-상세-기능)
6. [데이터 저장소 구조](#6-데이터-저장소-구조)
7. [모듈 간 독립성 및 간섭 방지 규칙](#7-모듈-간-독립성-및-간섭-방지-규칙)
8. [조직 구조](#8-조직-구조)
9. [기술 스택](#9-기술-스택)
10. [배포 환경](#10-배포-환경)
11. [개발 시 주의사항](#11-개발-시-주의사항)
12. [향후 계획](#12-향후-계획)
13. [부록](#13-부록)

---

## 1. 프로젝트 개요

### 1.1 배경

식품축산분석실은 연간 **69만건 이상**의 식품 검사를 수행하며, 다음과 같은 과제를 안고 있습니다:

- 33명의 담당자에 대한 **검사항목 배정 자동화** 필요
- 8,439개 식품유형-검사항목 조합에 대한 **수수료 관리**
- 식품안전나라 API를 통한 **실시간 데이터 수집**
- 검사 현황 및 통계의 **시각화**

### 1.2 목표

- 검사항목 자동 배정 시스템 구축
- 실시간 검사 현황 대시보드
- 식품안전나라 데이터 자동 수집
- 업무 효율성 30% 향상
- 데이터 관리 체계화

### 1.3 기대 효과

- **업무 효율화**: 수작업 항목 배정 자동화로 시간 절감
- **정확성 향상**: 데이터 기반 자동 배정으로 오류 최소화
- **투명성 확보**: 실시간 현황 공유
- **의사결정 지원**: 통계 데이터 기반 분석

---

## 2. 시스템 아키텍처

### 2.1 전체 구조

```
┌──────────────────────────────────────────────────────────────┐
│                     사용자 (브라우저)                            │
└────────────────────┬─────────────────────────────────────────┘
                     │ HTTPS / file://
┌────────────────────▼─────────────────────────────────────────┐
│              프론트엔드 (6개 HTML + 공통 JS)                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  js/sidebar.js  (Single Source of Truth — 사이드바)      │   │
│  │  → 모든 HTML 페이지가 이 파일 하나를 참조                      │   │
│  │  → 메뉴 추가/수정 시 이 파일만 수정하면 전체 반영                  │   │
│  └──────────────────────────────────────────────────────┘   │
│  index.html | salesMgmt.html | inspectionMgmt.html          │
│  sampleReceipt.html | itemAssign.html | userMgmt.html       │
└───────────┬──────────────────┬───────────────────────────────┘
            │ API (port 5001)  │ API (port 5060)
┌───────────▼──────┐  ┌───────▼───────────────────────────────┐
│ receipt_api_final │  │     bioflsever (14.7.14.31)           │
│  .py (로컬 Flask) │  │     Flask API (메인 서버)                │
│  port 5001       │  │  - 검사 데이터 CRUD                       │
│  - 접수번호 할당   │  │  - 담당자 배정 로직                        │
│  - 업체/항목 검색  │  │  - 통계 생성                              │
└──────────────────┘  └───────────┬───────────────────────────┘
                                  │ SQL
                      ┌───────────▼───────────────────────────┐
                      │        MariaDB Database (Ubuntu 24)     │
                      │  - foodlab DB: 사용자 관리 (56명)          │
                      │  - fss_data DB: 식품안전나라 데이터          │
                      │  - 검사 데이터: 2025년 692,061건           │
                      └─────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│           식품안전나라 API (16개 엔드포인트)                        │
│  - 업소정보, 제품정보, 원료정보, 변경이력                             │
│  - 자동 수집: 일일 증분 업데이트                                    │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 시스템 컴포넌트

| 컴포넌트 | 기술 스택 | 역할 | 포트 |
|---------|----------|------|------|
| **프론트엔드** | HTML/CSS/JS | 사용자 인터페이스 | — |
| **공통 사이드바** | `js/sidebar.js` | 전체 네비게이션 (SSOT) | — |
| **접수 API** | Flask (Python) | 시료접수 데이터 처리 | 5001 |
| **메인 API** | Flask (Python) | 비즈니스 로직 처리 | 5060 |
| **데이터베이스** | MariaDB | 데이터 저장 | 3306 |
| **배포** | GitHub Pages | 정적 파일 호스팅 | — |
| **서버** | Ubuntu 24 (bioflsever) | API 서버 | — |

---

## 3. 페이지 구성 및 연결 구조

### 3.1 전체 페이지 맵

```
BFL LIMS
├── index.html ─────────────────── 대시보드 (메인)
├── salesMgmt.html ─────────────── 영업 관리 (12개 내부 탭)
├── inspectionMgmt.html ────────── 검사 관리 (6개 탭) ⭐ 독자 사이드바
├── sampleReceipt.html ─────────── 시료 접수 등록
├── itemAssign.html ────────────── 항목 배정 ⭐ 핵심 기능
├── userMgmt.html ──────────────── 사용자 관리
└── js/
    ├── sidebar.js ─────────────── 🔑 통합 사이드바 (SSOT)
    ├── food_item_fee_mapping.js ── 수수료 데이터 (9,237건)
    └── ref_nonstandard_data.js ── 참고용 항목그룹 (3,374건)
```

### 3.2 사이드바 메뉴 ↔ 페이지 연결표

| 메뉴 그룹 | 하위 메뉴 | 연결 페이지 | 상태 |
|----------|----------|-----------|------|
| 📊 대시보드 | — | `index.html` | ✅ 활성 |
| 💼 영업 관리 | 고객사 관리 | `salesMgmt.html` | ✅ 활성 |
| | 업무일지 | `salesMgmt.html#daily` | ✅ 활성 |
| | 차량일지 | `salesMgmt.html#vehicle` | ✅ 활성 |
| | 미수금 활동 내역 | `salesMgmt.html#collection` | ✅ 활성 |
| | 거래명세표 관리 | `salesMgmt.html#trade` | ✅ 활성 |
| | 계산서 발행 승인 | `salesMgmt.html#invoice` | ✅ 활성 |
| | 업체조회 | `salesMgmt.html#bizSearch` | ✅ 활성 |
| | 긴급 협조 | `salesMgmt.html#urgent` | ✅ 활성 |
| | 세금계산서미발행 | `salesMgmt.html#arManage` | ✅ 활성 |
| | 영업통계 | — | 🔒 미구현 |
| | 영업 설정 | — | 🔒 미구현 |
| | API 설정 | `salesMgmt.html#apiSettings` | ✅ 활성 |
| 📋 접수 관리 | 업체등록·수정 | — | 🔒 미구현 |
| | 검사목적 관리 | `inspectionMgmt.html` | ✅ 활성 |
| | 접수 등록 | `sampleReceipt.html` | ✅ 활성 |
| | 접수 현황 | — | 🔒 미구현 |
| | 접수대장 | — | 🔒 미구현 |
| | 접수 조회/수정 | — | 🔒 미구현 |
| | 접수 통계 | — | 🔒 미구현 |
| 🔬 시험 결재 | 항목배정 | `itemAssign.html` | ✅ 활성 |
| | 시험 진행 현황 | — | 🔒 미구현 |
| | 결과 입력 | — | 🔒 미구현 |
| | 결재 승인 | — | 🔒 미구현 |
| | 시험 이력 조회 | — | 🔒 미구현 |
| | 일정관리 | — | 🔒 미구현 |
| | 지부관리 | — | 🔒 미구현 |
| | 실적보고 | — | 🔒 미구현 |
| | LIMS 연동 | — | 🔒 미구현 |
| 📄 성적 관리 | — | — | 🔒 미구현 |
| 💰 재무 관리 | — | — | 🔒 미구현 |
| 📈 통계 분석 | — | — | 🔒 미구현 |
| 📁 문서 관리 | — | — | 🔒 미구현 |
| 🧪 재고/시약 관리 | — | — | 🔒 미구현 |
| 📢 공지 | — | — | 🔒 미구현 |
| ⚙️ 사용자 설정 | — | — | 🔒 미구현 |
| 🔧 관리자 | 사용자 관리 | `userMgmt.html` | ✅ 활성 |
| | 부서 관리 | — | 🔒 미구현 |
| | 권한 설정 | — | 🔒 미구현 |
| | 대시보드 권한 | — | 🔒 미구현 |
| | 알림 설정 | — | 🔒 미구현 |
| | 시스템 로그 | — | 🔒 미구현 |
| | 미수금 관리 설정 | — | 🔒 미구현 |

### 3.3 페이지 간 이동 흐름

```
                    ┌─────────────┐
                    │  index.html │ ← 진입점
                    │  (대시보드)   │
                    └──────┬──────┘
            ┌──────────────┼──────────────┬──────────────────┐
            ▼              ▼              ▼                  ▼
    ┌───────────┐  ┌──────────────┐  ┌──────────┐  ┌──────────────┐
    │salesMgmt  │  │inspectionMgmt│  │sampleRcpt│  │ itemAssign   │
    │(영업관리)  │  │(검사관리)     │  │(시료접수) │  │ (항목배정)    │
    │ 12탭 내부  │  │ 6탭 내부     │  │ 폼 입력   │  │ 배정 테이블   │
    │ showPage() │  │ 독자 사이드바 │  │ API 연동  │  │ 자동 배정     │
    └───────────┘  └──────────────┘  └──────────┘  └──────────────┘
                                          │
                                          ▼
                                 ┌──────────────────┐
                                 │receipt_api_final  │
                                 │.py (port 5001)    │
                                 │ 폴백 모드 지원       │
                                 └──────────────────┘
```

---

## 4. 공통 모듈: 통합 사이드바

### 4.1 왜 통합했는가 (문제 → 해결)

| 이전 (문제) | 이후 (해결) |
|-----------|-----------|
| 6개 HTML 파일에 사이드바 HTML **복붙** | `js/sidebar.js` **하나**에서 생성 |
| 메뉴 추가 시 6개 파일 수동 수정 | sidebar.js 1곳만 수정 |
| 파일 간 메뉴 불일치 빈발 | 구조적으로 불일치 불가능 |
| 복사 원본이 어떤 파일인지 기준 없음 | **SIDEBAR_MENU 배열**이 유일한 정의 |

### 4.2 sidebar.js 구조

```
js/sidebar.js (Single Source of Truth)
├── 0. CSS 자동 주입 — injectSidebarCSS()
│   └── <style id="sidebar-unified-css"> 동적 삽입 (중복 방지)
├── 1. 메뉴 데이터 — SIDEBAR_MENU 배열 (유일한 정의 장소)
│   ├── 12개 메뉴 그룹 (dashboard~admin)
│   └── 총 37개 하위 메뉴 항목
├── 2. HTML 렌더링 — renderSidebar()
│   ├── 현재 페이지 파일명 자동 감지
│   ├── showPage() 존재 여부 체크 (salesMgmt.html 대응)
│   ├── active / expanded 자동 설정
│   └── internalPage 속성으로 내부 탭 전환 자동 분기
├── 3. 토글 메뉴 — toggleMenu() (아코디언)
└── 4. 초기화 — DOMContentLoaded에서 renderSidebar() 실행
```

### 4.3 각 HTML에서의 사용법

```html
<!-- 1) <body> 안에 빈 aside 추가 -->
<aside class="sidebar" id="sidebar"></aside>
<script src="js/sidebar.js"></script>

<!-- 2) sidebar.js가 DOMContentLoaded 시점에 자동으로:
     - CSS를 <head>에 주입
     - 로고 + 메뉴 HTML을 aside#sidebar 안에 생성
     - 현재 페이지에 해당하는 메뉴를 active/expanded
-->
```

### 4.4 메뉴 추가/수정 규칙

1. **`js/sidebar.js`의 `SIDEBAR_MENU` 배열만 수정**
2. 어떤 HTML 파일도 직접 수정하지 않음
3. 새 페이지 추가 시: `{ label: '새 메뉴', href: 'new.html', page: 'new-page' }`
4. 미구현 메뉴: `{ label: '메뉴명', disabled: true }`
5. salesMgmt.html 내부 탭: `internalPage` 속성 추가

### 4.5 적용 파일 현황

| 파일 | sidebar.js 사용 | 비고 |
|------|:---:|------|
| `index.html` | ✅ | |
| `salesMgmt.html` | ✅ | showPage() 내부 탭 전환 자동 처리 |
| `sampleReceipt.html` | ✅ | |
| `itemAssign.html` | ✅ | |
| `userMgmt.html` | ✅ | |
| `inspectionMgmt.html` | ❌ | 독자 사이드바 (beautiful-mclean 디자인). 향후 통합 검토 |

### 4.6 inspectionMgmt.html 독자 사이드바

inspectionMgmt.html은 완전히 다른 CSS 디자인("beautiful-mclean" 스타일)의 사이드바를 가집니다.
- 단일 레벨 flat 메뉴 (아코디언 없음)
- "접수 관리" 라벨 아래 10개 메뉴
- sidebar.js 미사용 — 자체 인라인 HTML
- **주의**: 메뉴 항목 변경 시 `inspectionMgmt.html`은 별도 수동 수정 필요

---

## 5. 각 페이지 상세 기능

### 5.1 대시보드 (index.html)

- **역할**: LIMS 메인 진입점. 실시간 검사 현황 통계.
- **사이드바**: `js/sidebar.js` (통합)
- **API 의존**: bioflsever (port 5060) — 통계 데이터
- **주요 데이터**: 하드코딩 샘플 (추후 API 교체)
- **CSS 클래스 네임스페이스**: 일반 (`.stat-card`, `.stat-value` 등)

#### 주요 지표
- 금월 매출, 이번 달 접수, 진행률
- 팀별 업무량
- 차트 (Chart.js)

---

### 5.2 영업 관리 (salesMgmt.html)

- **역할**: 고객사/업체 관리, 업무일지, 미수금, 업체조회
- **사이드바**: `js/sidebar.js` (통합) + `showPage()` 내부 탭 전환
- **API 의존**: 식품안전나라 API (업체조회), Kakao Maps API, VWORLD
- **내부 탭 전환**: `showPage(id)` 함수 — 12개 탭을 단일 HTML에서 전환
- **해시 라우팅**: `salesMgmt.html#daily` → `showPage('daily')` 자동 호출
- **CSS 클래스 네임스페이스**: `.page-container`, `.topbar`, `.tab-*`

#### 12개 서브메뉴 (내부 탭)
| # | 서브메뉴 | data-page ID | 설명 |
|---|---------|-------------|------|
| 1 | 고객사 관리 | customerList | 고객사 목록/등록/수정 |
| 2 | 업무일지 | daily | 일일 업무 기록 |
| 3 | 차량일지 | vehicle | 차량 운행 기록 |
| 4 | 미수금 활동 내역 | collection | 미수금 관리 |
| 5 | 거래명세표 관리 | trade | 거래 명세서 발행 |
| 6 | 계산서 발행 승인 | invoice | 세금계산서 발행 |
| 7 | 업체조회 | bizSearch | 식약처 DB 업체 검색 |
| 8 | 긴급 협조 | urgent | 긴급 협조 요청 |
| 9 | 세금계산서미발행 | arManage | 미발행 세금계산서 관리 |
| 10 | 영업통계 | — | 미구현 |
| 11 | 영업 설정 | — | 미구현 |
| 12 | API 설정 | apiSettings | 식품안전나라 API 설정 |

#### 지도 기능 (업체조회)
- **3단계 드릴다운**: 시도 → 시군구 → 읍면동
- VWORLD 타일 서버 (지도 배경)
- Leaflet.js (지도 렌더링 + GeoJSON 경계)
- Kakao Maps API (주소검색, 길찾기)
- GeoJSON 데이터: `data/sido.json`, `data/sigungu.json`, `data/dong.json`

---

### 5.3 검사 관리 (inspectionMgmt.html) ⭐ 주력 기능

- **역할**: 검사목적, 식품유형, 항목, 항목그룹, 수수료를 통합 관리
- **사이드바**: 독자 사이드바 (beautiful-mclean 디자인) — `sidebar.js` 미사용
- **API 의존**: 없음 (인라인 데이터 + 외부 JS)
- **CSS 클래스 네임스페이스**: 자체 CSS 변수 (`--pri`, `--bdr`, `--card` 등)
- **데이터 로드**: 인라인 + `js/food_item_fee_mapping.js` + `js/ref_nonstandard_data.js`

#### 6탭 구조
| 탭 | 설명 | 데이터 건수 |
|----|------|-----------|
| 검사분야 | 식품/축산 자동분류 | getDivision() 기반 |
| 검사목적 | 16개 검사목적 관리 | P 배열 29개 |
| 식품유형 | 검체유형별 항목 카드 | 3,062건 (894카드, 220 검체유형) |
| 검사항목 | 전체 검사항목 조회 | 8,757건 |
| 항목그룹 | 검사목적별 항목 그룹 | 5,695건 (14개 카테고리) |
| 수수료 | 검사목적별 수수료 관리 | 7,481건 (16개 카테고리) |

#### 식품유형 탭 (완료)
- 시료명 경계 기반 그룹핑 → 894카드, 3,062항목
- MANAGER_MAP 92개 매핑 (itemAssign.html 기반 실데이터)
- 상세 패널: 수정, 라벨 태그, 좌우 이동(◀▶), 변경 감지(민트색)
- 카드 기능: 선택 삭제, 8가지 정렬

#### 수수료 탭 (완료)
- 좌측 검사목적 메뉴 + 우측 카드/리스트 뷰
- `food_item_fee_mapping.js` 9,237건에서 종 통합 + 중복 제거 → 7,481건
- 검사목적 메뉴 CRUD: 추가(+)/수정/삭제
- 수수료 변경 감지 + dirty 추적 + 저장바
- 기초데이터(검체유형/규격/시험법근거/항목명) readOnly, 항목단위 편집 가능

#### 항목그룹 탭 (완료)
- 14개 검사목적 카테고리 (5,695건)
- 항생물질/잔류농약: 검체유형별 2단 서브그룹 유지
- 나머지 12개 카테고리: flat 리스트
- 카테고리 CRUD: rename / 삭제 (하위 전체)
- 항목 CRUD: inline 수정/삭제 + 상세패널 + 추가
- 필터 칩 동적 생성 (14개 카테고리 + 건수)

---

### 5.4 시료 접수 등록 (sampleReceipt.html)

- **역할**: 시료 접수를 등록하는 폼 페이지
- **사이드바**: `js/sidebar.js` (통합)
- **API 의존**: `receipt_api_final.py` (port 5001) — 폴백 모드 지원
- **CSS 클래스 네임스페이스**: `.btn-receipt` (사이드바 `.btn`과 충돌 방지)
- **데이터 로드**: API fetch + FALLBACK_* 상수 (API 실패 시)

#### 주요 기능
- **API 연동**: `receipt_api_final.py` Flask 서버(port 5001)와 fetch 호출
- **폴백 모드**: API 서버 미실행 시 내장 FALLBACK_* 데이터로 동작
- **서버 상태 인디케이터**: 🟢 연결됨 / 🔴 오프라인 (30초 주기, AbortSignal.timeout 3초)
- **6개 아코디언 섹션**: 접수 기본정보, 업체정보, 시료정보, 검사정보, 의뢰인 정보, 팀별 메모
- **접수번호 할당**: 서버 측 스레드 안전 할당 (POST `/api/receipt-no/allocate`)
- **업체 검색**: 디바운스(300ms) + API 자동완성
- **식품유형 자동완성**: 검색어 하이라이트 + autocomplete
- **팀별 메모 권한**: 현재 팀만 편집 가능, 나머지 읽기 전용
- **임시저장**: localStorage 기반

#### API 엔드포인트 (receipt_api_final.py, port 5001)

| 엔드포인트 | 메서드 | 설명 | 폴백 |
|-----------|--------|------|------|
| `/api/health` | GET | 서버 상태 확인 | 오프라인 표시 |
| `/api/test-purposes?field=` | GET | 검사목적 조회 | FALLBACK_TEST_PURPOSE_MAPPING |
| `/api/food-types?field=&purpose=` | GET | 검체유형 조회 | FALLBACK_FOOD_TYPE_MAPPING |
| `/api/receipt-no/allocate` | POST | 접수번호 할당 | 클라이언트측 임시번호 |
| `/api/companies/search?q=` | GET | 업체 검색 | FALLBACK_COMPANIES |
| `/api/items/search?q=&purpose=` | GET | 검사항목 검색 | FALLBACK_ITEMS |

#### 데이터 흐름
```
사용자 → sampleReceipt.html
              ↓ fetch() (apiOnline 체크)
         receipt_api_final.py (port 5001)
              ↓ parse at startup
         js/food_item_fee_mapping.js (9,237건)

         ※ API 오프라인 시 → FALLBACK_* 상수 사용
```

---

### 5.5 항목 배정 (itemAssign.html) ⭐ 핵심 기능

- **역할**: 검사항목을 담당자에게 자동으로 배정
- **사이드바**: `js/sidebar.js` (통합)
- **API 의존**: 없음 (인라인 JS 데이터)
- **CSS 클래스 네임스페이스**: 일반 (`.main-container`, `.breadcrumb` 등)
- **데이터 로드**: 인라인 JS (managers, mappings)

#### 배정 로직
```
1. 식품유형 선택
   ↓
2. 괄호 패턴 추출
   예: "잔류농약(463종)" → "463종"
   ↓
3. 검사항목 목록 표시
   ↓
4. 자동 담당자 배정 (3단계 우선순위)
   - 우선순위 1: bracket_item_manager_mapping (괄호+항목)
   - 우선순위 2: food_item_manager_mapping (식품유형+항목)
   - 우선순위 3: item_manager_mapping (항목만)
   ↓
5. 수수료 자동 표시
   - food_item_fee_mapping에서 조회
   ↓
6. 담당자 수동 변경 가능
   - 33명 중 선택
```

#### 데이터 소스
| 데이터 | 파일/위치 | 건수 | 역할 |
|--------|----------|------|------|
| managers_final.js | 인라인 | 33명 | 담당자 목록 |
| food_item_fee_mapping.js | 외부 JS | 9,237개 | 수수료 조회 |
| bracket_item_manager_mapping.js | 인라인 | 1,438개 | 괄호+항목 → 담당자 |
| food_item_manager_mapping | 인라인 | — | 식품유형+항목 → 담당자 |
| item_manager_mapping | 인라인 | — | 항목만 → 담당자 |

---

### 5.6 사용자 관리 (userMgmt.html)

- **역할**: 담당자 정보 관리, 팀별 구성원 조회
- **사이드바**: `js/sidebar.js` (통합)
- **API 의존**: bioflsever (추후)
- **CSS 클래스 네임스페이스**: 일반
- **데이터 로드**: 인라인 JS

#### 기능
- 담당자 정보 관리 (이름, 직급, 팀, 전문 분야)
- 팀별 구성원 조회
- 권한 관리
- 접속 이력

---

## 6. 데이터 저장소 구조

### 6.1 데이터 저장소 전체 맵

```
데이터 저장소
├── 📁 인라인 데이터 (HTML 내장)
│   ├── inspectionMgmt.html
│   │   ├── P (검사목적 29개) ─────── 라인 1045-1074
│   │   ├── FULL_FOOD_TYPES (3,062개) ─ 라인 1241-4304
│   │   ├── FULL_ITEM_GROUPS (~2,321개) ─ 라인 4306-32158
│   │   ├── MANAGER_MAP (92개) ────── 라인 1146-1239
│   │   └── getDivision() + 축산_검체유형 (54개) ── 라인 1128-1134
│   │
│   ├── itemAssign.html
│   │   ├── managers_final (33명)
│   │   ├── bracket_item_manager_mapping (1,438개)
│   │   └── food_item_manager_mapping
│   │
│   └── sampleReceipt.html
│       ├── FALLBACK_TEST_PURPOSE_MAPPING
│       ├── FALLBACK_FOOD_TYPE_MAPPING
│       ├── FALLBACK_COMPANIES
│       └── FALLBACK_ITEMS
│
├── 📁 외부 JS 파일
│   ├── js/sidebar.js ─────────── 사이드바 메뉴 데이터 (SIDEBAR_MENU)
│   ├── js/food_item_fee_mapping.js ── 수수료 9,237건 (FOOD_ITEM_FEE_MAPPING)
│   └── js/ref_nonstandard_data.js ── 참고용 항목그룹 3,374건 (REF_NONSTANDARD_ITEM_GROUPS)
│
├── 📁 GeoJSON 파일
│   ├── data/sido.json ────────── 시도 경계
│   ├── data/sigungu.json ─────── 시군구 경계
│   └── data/dong.json ────────── 읍면동 경계
│
├── 📁 API 서버 (receipt_api_final.py, port 5001)
│   └── js/food_item_fee_mapping.js를 파싱하여 메모리에 로드
│
├── 📁 MariaDB (bioflsever, port 3306)
│   ├── foodlab DB ─────────── 사용자 관리 (56명)
│   ├── fss_data DB ────────── 식품안전나라 데이터
│   └── inspection_data DB ── 검사 데이터 (2025년 692,061건)
│
└── 📁 브라우저 localStorage
    └── sampleReceipt 임시저장 데이터
```

### 6.2 데이터 연결 구조 (inspectionMgmt.html 기준)

```
P (검사목적 29개)
  ↓ 검사목적별 필터링
FULL_FOOD_TYPES (3,062개) ← 식품유형 탭 (자가품질위탁검사용만)
  ↓
FULL_ITEM_GROUPS (5,695개) ← 항목그룹 탭 (14개 카테고리)
  = 기본 2,321개 + REF_NONSTANDARD_ITEM_GROUPS 3,374개 병합
  ↓
FOOD_ITEM_FEE_MAPPING (9,237개) → 종 통합 + 중복제거 → feeData 7,481개
  ↓ 수수료 → 식품유형/항목그룹 자동 매칭
MANAGER_MAP (92개) → findManager(검체유형, 항목명) 담당자 자동 배정
getDivision() → 검체유형 54개 축산 목록 기준 식품/축산 분류
```

### 6.3 검사 데이터 통계 (2025년)

| 항목 | 값 |
|------|-----|
| 총 검사 건수 | 692,061건 |
| 수집 기간 | 2025년 1~11월 (6월 제외) |
| 고유 식품유형 | 214개 |
| 검사항목 | 934개 |
| 식품유형-항목 조합 | 9,237개 (16개 검사목적) |

### 6.4 외부 JS 데이터 파일 상세

| 파일명 | 변수명 | 건수 | 사용 페이지 | 설명 |
|--------|--------|------|-----------|------|
| `js/sidebar.js` | `SIDEBAR_MENU` | 12그룹, 37항목 | 5개 HTML | 통합 사이드바 메뉴 정의 |
| `js/food_item_fee_mapping.js` | `FOOD_ITEM_FEE_MAPPING` | 9,237건 | inspectionMgmt, receipt_api | 수수료 데이터 |
| `js/ref_nonstandard_data.js` | `REF_NONSTANDARD_ITEM_GROUPS` | 3,374건 | inspectionMgmt | 참고용(기준규격외) 항목그룹 |

### 6.5 주요 테이블 (MariaDB)

#### users (사용자)
```sql
CREATE TABLE users (
    id INT PRIMARY KEY,
    username VARCHAR(50),
    name VARCHAR(50),
    department VARCHAR(100),
    position VARCHAR(50),
    email VARCHAR(100),
    phone VARCHAR(20),
    permissions TEXT
);
```

#### inspections (검사)
```sql
CREATE TABLE inspections (
    접수번호 VARCHAR(50) PRIMARY KEY,
    접수일자 DATE,
    검체유형 VARCHAR(100),
    항목명 VARCHAR(200),
    항목담당자 VARCHAR(50),
    항목수수료 INT,
    상태 VARCHAR(20),
    업체명 VARCHAR(200)
    -- ... 38개 컬럼
);
```

---

## 7. 모듈 간 독립성 및 간섭 방지 규칙

### 7.1 핵심 원칙

> **각 페이지는 자신의 영역 안에서만 동작하고, 다른 페이지의 데이터·스타일·함수에 영향을 주지 않는다.**

### 7.2 CSS 네임스페이스 분리 규칙

| 페이지 | CSS 접두사/전략 | 사이드바 `.btn` 충돌 방지 |
|--------|---------------|----------------------|
| `index.html` | `.stat-card`, `.stat-value` | 충돌 없음 |
| `salesMgmt.html` | `.page-container`, `.topbar` | 충돌 없음 |
| `inspectionMgmt.html` | CSS 변수 (`--pri`, `--bdr`) | 독자 사이드바이므로 해당없음 |
| `sampleReceipt.html` | **`.btn-receipt`** (`.btn` 대신) | ✅ 명시적 분리 |
| `itemAssign.html` | `.main-container`, `.breadcrumb` | 충돌 없음 |
| `userMgmt.html` | `.main-container`, `.breadcrumb` | 충돌 없음 |
| `js/sidebar.js` | `.sidebar`, `.nav-parent`, `.nav-sub-item` | — (자체 영역) |

**규칙**: 새 페이지에서 `.btn` 클래스를 사용하면 사이드바의 `.btn`과 충돌할 수 있으므로, 반드시 `.btn-{페이지명}` 형태로 네임스페이스를 부여할 것.

### 7.3 JavaScript 전역 변수 분리 규칙

| 전역 변수/함수 | 소속 | 범위 |
|-------------|------|------|
| `SIDEBAR_MENU` | sidebar.js | 모든 페이지 |
| `renderSidebar()` | sidebar.js | 모든 페이지 |
| `toggleMenu()` | sidebar.js | 모든 페이지 |
| `showPage()` | salesMgmt.html | salesMgmt.html만 |
| `API_BASE`, `apiOnline` | sampleReceipt.html | sampleReceipt.html만 |
| `FOOD_ITEM_FEE_MAPPING` | food_item_fee_mapping.js | inspectionMgmt, itemAssign, receipt_api |
| `P`, `FULL_FOOD_TYPES`, `FULL_ITEM_GROUPS` | inspectionMgmt.html | inspectionMgmt.html만 |

**규칙**:
- sidebar.js의 전역 변수(`SIDEBAR_MENU`, `toggleMenu`)는 모든 페이지에서 사용되므로 이름 변경 금지
- 각 페이지의 전역 변수는 해당 페이지 내에서만 유효
- 같은 이름의 전역 변수를 다른 페이지에서 사용하지 않도록 주의

### 7.4 API 포트 분리

| API 서버 | 포트 | 사용 페이지 | 용도 |
|---------|------|-----------|------|
| `receipt_api_final.py` | **5001** | sampleReceipt.html | 시료접수 전용 |
| Flask 메인 API | **5060** | index.html, etc. | 검사 데이터, 통계 |
| MariaDB | **3306** | API 서버들 | 데이터 저장 |

**규칙**: API 포트를 변경할 때는 해당 API를 사용하는 모든 프론트엔드 파일의 `API_BASE` 상수도 함께 변경할 것.

### 7.5 데이터 소유권

| 데이터 | 소유 페이지 | 읽기 허용 | 쓰기 허용 |
|--------|-----------|----------|----------|
| `SIDEBAR_MENU` | sidebar.js | 모든 HTML | sidebar.js만 |
| `FOOD_ITEM_FEE_MAPPING` | food_item_fee_mapping.js | inspectionMgmt, itemAssign, receipt_api | 파일 직접 수정 |
| `P` (검사목적) | inspectionMgmt.html | inspectionMgmt만 | inspectionMgmt만 |
| `FULL_FOOD_TYPES` | inspectionMgmt.html | inspectionMgmt만 | inspectionMgmt만 |
| 접수번호 시퀀스 | receipt_api_final.py | sampleReceipt만 | receipt_api만 (스레드 안전) |
| localStorage 임시저장 | sampleReceipt.html | sampleReceipt만 | sampleReceipt만 |

### 7.6 신규 페이지 추가 체크리스트

새 HTML 페이지를 추가할 때 반드시 확인할 항목:

- [ ] `<aside class="sidebar" id="sidebar"></aside>` 추가
- [ ] `<script src="js/sidebar.js"></script>` 추가 (aside 바로 뒤)
- [ ] `js/sidebar.js`의 `SIDEBAR_MENU`에 해당 메뉴 항목 추가
- [ ] CSS 클래스명이 sidebar.js의 클래스와 충돌하지 않는지 확인
- [ ] 전역 변수명이 다른 페이지와 충돌하지 않는지 확인
- [ ] `inspectionMgmt.html`의 독자 사이드바에도 해당 메뉴 링크 추가 (해당 시)
- [ ] `.main-container`에 `margin-left:250px` 적용 (사이드바 너비)
- [ ] 반응형: `@media(max-width:768px)` 사이드바 숨김 처리

---

## 8. 조직 구조

### 8.1 식품축산분석실 (33명)

| 팀명 | 인원 | 주요 업무 |
|------|------|----------|
| **미생물 1팀** | 5명 | 세균수, 대장균, 대장균군 검사 |
| **미생물 2팀** | 5명 | 살모넬라, 바실루스 검사 |
| **이화학 1팀** | 5명 | 산가, 과산화물가, 산도 검사 |
| **이화학 2팀** | 6명 | 납, 카드뮴, 타르색소 검사 |
| **이화학 3팀** | 6명 | 보존료, 영양성분 검사 |
| **잔류농약팀** | 4명 | 잔류농약 463종/510종 검사 |
| **분석실** | 2명 | 전체 총괄 관리 |

### 8.2 직급별 분포

부장 1명, 차장 2명, 과장 7명, 대리 6명, 주임 5명, 사원 10명, 미지정 2명

### 8.3 핵심 담당자

| 이름 | 팀 | 직급 | 주요 업무 | 2025년 건수 |
|------|-----|------|-----------|------------|
| **백지연** | 잔류농약 | 주임 | 잔류농약 검사 (728개 항목) | 81,900건 |
| 김지영 | 이화학 2팀 | 과장 | 이화학 검사 | 4,491건 |
| 진미정 | 미생물 2팀 | 사원 | 미생물 검사 | 4,153건 |
| 서진영 | 이화학 2팀 | 사원 | 이화학 검사 | 2,290건 |
| 신경석 | 미생물 1팀 | 대리 | 미생물 검사 | 2,267건 |

---

## 9. 기술 스택

### 9.1 프론트엔드

```
HTML5 / CSS3 / JavaScript (ES6+)
├── 공통 모듈
│   └── js/sidebar.js (사이드바 SSOT)
├── UI 라이브러리
│   ├── Chart.js (통계 차트)
│   ├── Leaflet.js (지도 렌더링)
│   └── Kakao Maps API (주소검색/길찾기)
├── 패턴
│   ├── Fetch API + async/await (서버 통신)
│   ├── localStorage (임시 데이터 저장)
│   ├── CSS Variables (테마)
│   ├── Flexbox / Grid (레이아웃)
│   └── AbortSignal.timeout (API 타임아웃)
└── 특수 처리
    ├── showPage() 내부 탭 전환 (salesMgmt.html)
    ├── 디바운스 (sampleReceipt.html 업체검색)
    └── GeoJSON 드릴다운 (salesMgmt.html 지도)
```

### 9.2 백엔드

```
Python 3.12
├── Flask
│   ├── receipt_api_final.py (port 5001) — 시료접수 전용
│   └── 메인 API (port 5060) — 검사 데이터 CRUD
│
MariaDB
├── InnoDB 엔진
├── UTF-8mb4 인코딩
└── 인덱스 최적화

Libraries
├── openpyxl (Excel 처리)
├── requests (API 호출)
├── pandas (데이터 분석)
└── mysql-connector-python
```

### 9.3 데이터 수집

```
식품안전나라 API (16개)
├── 업소정보 (4개 API)
├── 제품정보 (4개 API)
├── 원료정보 (4개 API)
└── 변경이력 (4개 API)

자동 수집 시스템
├── 일일 증분 업데이트
├── 실패 시 자동 재시도
├── 진행률 실시간 표시
└── 로그 기록
```

---

## 10. 배포 환경

### 10.1 프론트엔드 배포

**GitHub Pages**
- URL: https://biofl1411.github.io/bfl_lims
- 저장소: biofl1411/bfl_lims
- 자동 배포: Git Push 시 자동 반영
- CDN: GitHub 글로벌 CDN 활용

### 10.2 백엔드 서버

**bioflsever (14.7.14.31)**
```
OS: Ubuntu 24.04 LTS

Services:
├── MariaDB (포트: 3306)
├── Flask 메인 API (포트: 5060)
├── receipt_api_final.py (포트: 5001) — 시료접수 전용
└── SSH (포트: 2222)

Databases:
├── foodlab (사용자 관리)
├── fss_data (식품안전나라 데이터)
└── inspection_data (검사 데이터)

환경변수:
├── FSS_DB_HOST, FSS_DB_PORT, FSS_DB_USER, FSS_DB_PASS
├── FSS_DB_NAME, FSS_API_KEY, FSS_API_PORT
```

### 10.3 보안

- HTTPS 통신 (GitHub Pages)
- 비밀번호 암호화 (MySQL)
- API 키 환경변수 관리
- SSH 키 인증 (서버 접속)
- 포트 제한 (방화벽)
- CORS 설정 (Flask API)

---

## 11. 개발 시 주의사항

### 11.1 사이드바 관련

| # | 규칙 | 이유 |
|---|------|------|
| 1 | **메뉴 변경은 `js/sidebar.js`만 수정** | SSOT 원칙. HTML 직접 수정 금지 |
| 2 | **inspectionMgmt.html은 별도 수정** | 독자 사이드바이므로 sidebar.js 변경 시 수동 동기화 필요 |
| 3 | **sidebar.js의 전역 변수명 변경 금지** | `SIDEBAR_MENU`, `toggleMenu`, `renderSidebar`는 5개 HTML이 의존 |
| 4 | **`<aside id="sidebar">` ID 변경 금지** | sidebar.js가 `getElementById('sidebar')`로 접근 |

### 11.2 CSS 관련

| # | 규칙 | 이유 |
|---|------|------|
| 1 | **새 페이지에서 `.btn` 사용 금지** | sidebar.js가 주입하는 CSS와 충돌. `.btn-{페이지명}` 사용 |
| 2 | **`.sidebar`, `.nav-*` 클래스 사용 금지** | sidebar.js 전용 클래스 |
| 3 | **`.main-container`에 `margin-left:250px`** | 사이드바 너비(250px)만큼 본문 밀어내기 |
| 4 | **인라인 CSS에 사이드바 CSS 남겨도 됨** | sidebar.js도 주입하므로 중복되지만 FOUC 방지에 유리 |

### 11.3 JavaScript 관련

| # | 규칙 | 이유 |
|---|------|------|
| 1 | **showPage()는 salesMgmt.html 전용** | sidebar.js가 자동 감지하여 내부 탭 전환으로 분기 |
| 2 | **API_BASE 상수는 각 페이지에서 독립 정의** | 포트 변경 시 해당 페이지만 수정 |
| 3 | **폴백 데이터(FALLBACK_*)는 sampleReceipt.html 전용** | 다른 페이지에서 참조하지 않음 |
| 4 | **`DOMContentLoaded` 이후에 DOM 조작** | sidebar.js가 이 시점에 사이드바를 생성하므로, 사이드바 요소 접근은 이후에 |

### 11.4 데이터 관련

| # | 규칙 | 이유 |
|---|------|------|
| 1 | **food_item_fee_mapping.js 수정 시 receipt_api 재시작 필요** | 서버가 시작 시 파싱하므로 |
| 2 | **검사목적(P 배열) 변경 시 inspectionMgmt.html만 수정** | 다른 페이지에서 참조하지 않음 |
| 3 | **localStorage 키 충돌 주의** | 각 페이지별 고유 prefix 권장 (예: `sampleReceipt_`) |

### 11.5 Git 커밋 관련

| # | 규칙 | 이유 |
|---|------|------|
| 1 | **sidebar.js 변경 시 커밋 메시지에 명시** | 5개 HTML에 영향. 예: "sidebar: 접수현황 메뉴 활성화" |
| 2 | **여러 HTML 동시 수정 시 sidebar.js 우선 확인** | sidebar.js로 해결 가능한지 먼저 판단 |

---

## 12. 향후 계획

### 12.1 단기 목표 (1~3개월)

**Phase 1: 핵심 기능 완성**
- [x] 담당자 관리 시스템
- [x] 검사항목 매핑 데이터
- [x] 수수료 전체 재추출 (16개 검사목적, 9,237건 → 7,481건)
- [x] 수수료 탭 구현 (좌측 메뉴 + CRUD + 변경 감지)
- [x] 수수료 → 식품유형/항목그룹 자동 매칭
- [x] 항목그룹 구조 변경 (그룹형/flat형 분리)
- [x] 항목그룹 CRUD (카테고리 수정/삭제 + 항목 추가/수정/삭제)
- [x] 시료접수 등록 페이지 (sampleReceipt.html + receipt_api_final.py)
- [x] 통합 사이드바 (js/sidebar.js SSOT)
- [ ] 항목배정 페이지 완성
- [ ] inspectionMgmt.html 사이드바 통합 검토

**Phase 2: 데이터 통합**
- [x] 2025년 전체 데이터 수집
- [ ] MySQL DB 구축
- [ ] Flask API 개발
- [ ] 프론트엔드-백엔드 연동

### 12.2 중기 목표 (3~6개월)

- 월별/팀별 검사 현황 대시보드
- 담당자별 업무량 분석
- 모바일 최적화 (반응형 + PWA)
- 알림 시스템 (검사 완료, 마감일 임박)

### 12.3 장기 목표 (6개월 이상)

- AI/ML 검사 결과 예측 및 이상 감지
- ERP/전자결재 시스템 연동
- AWS/GCP 클라우드 전환
- 자동 백업 + 부하 분산

---

## 13. 부록

### 13.1 파일 목록 전체

| 파일 | 역할 | 사이드바 | 비고 |
|------|------|---------|------|
| `index.html` | 대시보드 | sidebar.js | 메인 진입점 |
| `salesMgmt.html` | 영업 관리 | sidebar.js | showPage() 내부 탭 |
| `inspectionMgmt.html` | 검사 관리 | 독자 사이드바 | 6탭, 주력 기능 |
| `sampleReceipt.html` | 시료 접수 | sidebar.js | API+폴백 |
| `itemAssign.html` | 항목 배정 | sidebar.js | 핵심 기능 |
| `userMgmt.html` | 사용자 관리 | sidebar.js | |
| `js/sidebar.js` | 통합 사이드바 | — | SSOT |
| `js/food_item_fee_mapping.js` | 수수료 데이터 | — | 9,237건 |
| `js/ref_nonstandard_data.js` | 참고용 항목그룹 | — | 3,374건 |
| `receipt_api_final.py` | 시료접수 API | — | Flask, port 5001 |
| `SETUP_GUIDE.md` | 설치 가이드 | — | |
| `README.md` | 프로젝트 README | — | |
| `BFL_LIMS_planning.md` | 이 기획서 | — | |

### 13.2 주요 식품유형

| 식품유형 | 검사 건수 | 주요 검사항목 |
|---------|----------|-------------|
| 잔류농약(463종) | 73,312건 | Abamectin, Acephate, Acetamiprid 등 464개 |
| 잔류농약(510종) | 3,066건 | 510개 잔류농약 항목 |
| 항생물질(156종) | 157건 | 156개 항생물질 항목 |
| 소스 | 822건 | 이물, 대장균, 타르색소 |
| 양념육 | 269건 | 세균수, 대장균, 보존료 |

### 13.3 괄호 패턴 목록

| 괄호 내용 | 건수 | 항목 수 | 설명 |
|----------|------|--------|------|
| 463종 | 73,312건 | 464개 | 잔류농약 463종 검사 |
| 510종 | 3,066건 | 511개 | 잔류농약 510종 검사 |
| 156종 | 157건 | 157개 | 항생물질 156종 검사 |
| 99종 | 630건 | 105개 | 항생물질 99종 검사 |
| 60종 | 183건 | 61개 | 항생물질 60종 검사 |
| 살균제품 | 103건 | 29개 | 살균 처리된 제품 |
| 조미김 또는 구운김 | 60건 | 19개 | 김 제품 |
| 축산물즉석판매제품 | 56건 | 12개 | 즉석 판매 축산물 |

### 13.4 참고 자료

- 식품안전나라 API: https://www.foodsafetykorea.go.kr/api
- GitHub 저장소: https://github.com/biofl1411/bfl_lims
- 내부 문서: Google Drive > food_item > food_item_2025

---

## 14. 연락처

**프로젝트 관리자**
- 회사: BioFoodLab Co., Ltd.
- 이메일: biofl1411@gmail.com
- 서버: bioflsever (14.7.14.31:2222)

**기술 지원**
- GitHub Issues: https://github.com/biofl1411/bfl_lims/issues

---

*본 문서는 2026년 2월 19일 기준으로 최종 업데이트되었으며, 프로젝트 진행에 따라 업데이트됩니다.*

**Version History**
- v1.0 (2026-02-16): 초안 작성
- v1.1 (2026-02-18): 검사관리 완료 사항 반영 — 수수료 탭(16개 목적, 7,481건), 항목그룹 탭(그룹형/flat형 분리, CRUD), 수수료 데이터 재추출(9,237건), 참고용(기준규격외) 병합(3,374건)
- v1.2 (2026-02-19): 한글 파일명 영문 전환 반영, 데이터 저장 위치 섹션 추가, 영업관리 섹션 현행화, 기술 스택(MariaDB/Leaflet/Kakao) 수정
- v1.3 (2026-02-19): 시료접수 등록(sampleReceipt.html) 섹션 추가 — API 연동(receipt_api_final.py, port 5001), 폴백 모드, 서버 상태 인디케이터
- **v2.0 (2026-02-19): 전면 재구성**
  - 통합 사이드바(`js/sidebar.js`) SSOT 아키텍처 반영
  - 페이지 구성 및 연결 구조 맵 추가 (섹션 3)
  - 공통 모듈 상세 문서화 (섹션 4)
  - 데이터 저장소 전체 맵 추가 (섹션 6)
  - 모듈 간 독립성 및 간섭 방지 규칙 추가 (섹션 7)
  - 개발 시 주의사항 체크리스트 추가 (섹션 11)
  - 신규 페이지 추가 체크리스트 추가
  - 사이드바 메뉴 ↔ 페이지 연결표 (37개 전체 항목)
  - CSS/JS/API/데이터 소유권 분리 규칙 명문화
