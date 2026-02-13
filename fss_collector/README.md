# 식약처 인허가 데이터 수집 시스템

BioFoodLab 업체조회 기능을 위한 식약처 공공데이터 자동 수집 시스템

## 시스템 구조

```
[식약처 API 16개] → [collector.py] → [MariaDB] → [api_server.py] → [업체조회 UI]
                     매일 3시 KST       fss_data     포트 5050         Leaflet 지도
```

## 수집 대상 API (16개)

### 업소 인허가 대장 (9개)
| 서비스ID | API명 | 예상 건수 |
|----------|-------|-----------|
| I1220 | 식품제조가공업 | ~30,000 |
| I2829 | 즉석판매제조가공업 | ~98,000 |
| I-0020 | 건강기능식품 전문/벤처제조업 | ~550 |
| I1300 | 축산물 가공업 | ~4,200 |
| I1320 | 축산물 식육포장처리업 | 확인필요 |
| I2835 | 식육즉석판매가공업 | 확인필요 |
| I2831 | 식품소분업 | 확인필요 |
| C001 | 수입식품등영업신고 | 확인필요 |
| I1260 | 식품등수입판매업 | 확인필요 |

### 품목 제조 보고 (2개)
| 서비스ID | API명 | 예상 건수 |
|----------|-------|-----------|
| I1250 | 식품(첨가물)품목제조보고 | ~1,040,000 |
| I1310 | 축산물 품목제조정보 | 확인필요 |

### 원재료 정보 (3개)
| 서비스ID | API명 | 예상 건수 |
|----------|-------|-----------|
| C002 | 식품(첨가물)품목제조보고(원재료) | 확인필요 |
| C003 | 건강기능식품 품목제조신고(원재료) | ~44,000 |
| C006 | 축산물품목제조보고(원재료) | 확인필요 |

### 변경 이력 (2개)
| 서비스ID | API명 |
|----------|-------|
| I2859 | 식품업소 인허가 변경 정보 |
| I2860 | 건강기능식품업소 인허가 변경 정보 |

## DB 테이블 구조

| 테이블 | 용도 | 핵심 인덱스 |
|--------|------|-------------|
| fss_businesses | 업소 인허가 (9개 API 통합) | 시도/시군구/읍면동, 업소명, 업종 |
| fss_products | 품목 제조 보고 | 인허가번호, 제품명, 품목유형 |
| fss_materials | 원재료 정보 | 원재료명, 품목번호 |
| fss_changes | 변경 이력 | 인허가번호, 변경일자 |
| fss_collect_log | 수집 로그 | 수집일시 |

## 설치 (bioflsever)

```bash
# 1. 파일 복사
scp -r fss_collector/ biofl@bioflsever:~/

# 2. 설치 실행
cd ~/fss_collector
chmod +x setup.sh
./setup.sh

# 3. 최초 전체 수집 (30~60분)
source .env
python3 collector.py --full
```

## 사용법

```bash
# 증분 수집 (매일 cron 자동 실행)
python3 collector.py

# 전체 재수집
python3 collector.py --full

# 특정 API만
python3 collector.py --full I1220 I2829

# 현황 확인
python3 collector.py --status
```

## API 엔드포인트

### 업소 검색
```
GET /api/businesses?sido=경기도&sigungu=파주시&dong=문산읍
GET /api/businesses?keyword=바이오&induty=식품제조가공업
GET /api/businesses?api_source=I1220&page=1&size=50
```

### 지역 통계
```
GET /api/region/stats?level=sido
GET /api/region/stats?level=sigungu&sido=경기도
GET /api/region/stats?level=dong&sido=경기도&sigungu=파주시
```

### 제품 검색
```
GET /api/products?keyword=김치&prdlst_dcnm=절임류
GET /api/products?lcns_no=2023012345
```

### 원재료 검색
```
GET /api/materials?keyword=대두
GET /api/materials?prdlst_report_no=2023012345
```

### 변경 이력
```
GET /api/changes?lcns_no=2023012345
GET /api/changes?bssh_nm=바이오푸드
```

### 수집 현황
```
GET /api/status
GET /api/industries
```

## 파일 구성

```
fss_collector/
├── schema.sql       # MariaDB 테이블 생성
├── collector.py     # 데이터 수집 스크립트 (cron)
├── api_server.py    # Flask API 서버
├── setup.sh         # 설치 스크립트
├── README.md        # 이 문서
└── logs/            # 수집 로그
```

## 수집 흐름

### 최초 수집 (--full)
1. 각 API의 총 건수 확인
2. 100건씩 페이지네이션으로 전체 수집
3. 주소 파싱 → 시도/시군구/읍면동 컬럼 저장
4. UPSERT (인허가번호 기준 중복 시 업데이트)

### 일일 증분 수집 (cron)
1. CHNG_DT=어제날짜 파라미터로 변경분만 요청
2. 변경된 레코드만 UPDATE
3. 신규 레코드 INSERT
4. 수집 로그 기록

## 주소 파싱 규칙

```
"경기도 파주시 문산읍 ..." 
  → addr_sido="경기도", addr_sigungu="파주시", addr_dong="문산읍"

"서울특별시 강남구 역삼동 ..."
  → addr_sido="서울특별시", addr_sigungu="강남구", addr_dong="역삼동"
```

## 업체조회 UI 연동

현재: 카카오맵 + 식약처 실시간 API (CORS 프록시)
변경: DB에서 직접 조회 (빠르고 안정적)

프론트엔드에서 api_server.py 호출:
```javascript
// 지도 드릴다운으로 경기도 > 파주시 > 문산읍 선택 시
fetch('http://bioflsever:5050/api/businesses?sido=경기도&sigungu=파주시&dong=문산읍')
  .then(r => r.json())
  .then(data => {
    // data.total = 해당 읍면동 전체 업소 수
    // data.data = 업소 목록
  });
```
