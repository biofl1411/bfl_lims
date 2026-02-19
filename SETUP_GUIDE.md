# 🚀 실행 가이드 - 실제 데이터 연결 완료!

## ✅ 준비 완료!

다운로드한 파일:
- ✅ food_item_fee_mapping.js (9,237건)
- ✅ receipt_api_final.py (최종 API 서버)
- ✅ 시료접수.html (프론트엔드)

---

## 📁 폴더 구조 설정

```
C:\Users\user\Desktop\bfl_lims\
├── js\
│   └── food_item_fee_mapping.js   ← 여기 배치!
├── api\
│   └── receipt_api_final.py        ← 여기 배치!
└── 시료접수.html                    ← 여기 배치!
```

### 단계별 배치

```powershell
# 1. 프로젝트 폴더로 이동
cd C:\Users\user\Desktop\bfl_lims

# 2. 폴더 생성 (없으면)
mkdir js
mkdir api

# 3. 다운로드한 파일 이동
# Downloads 폴더에서:
move C:\Users\user\Downloads\food_item_fee_mapping.js js\
move C:\Users\user\Downloads\receipt_api_final.py api\
move C:\Users\user\Downloads\시료접수.html .\
```

---

## 🚀 API 서버 실행

### 1단계: Python 패키지 설치
```powershell
cd C:\Users\user\Desktop\bfl_lims

# Flask 설치
pip install flask flask-cors
```

### 2단계: API 서버 실행
```powershell
cd api
python receipt_api_final.py
```

### 3단계: 성공 확인 ⭐

**화면에 이렇게 표시되어야 합니다:**
```
====================================================================
🧪 BFL LIMS Receipt API Server
====================================================================
Server URL: http://127.0.0.1:5001
Health Check: http://127.0.0.1:5001/api/health
--------------------------------------------------------------------
Data Source: food_item_fee_mapping.js
Items Loaded: 9237  ← 이 숫자 확인!
====================================================================

✅ Parsed 9237 items from JS file  ← 이 메시지 확인!

API Endpoints:
  GET  /api/health
  GET  /api/test-purposes?field={식품|축산}
  GET  /api/food-types?field={}&purpose={}
  POST /api/receipt-no/allocate
  GET  /api/companies/search?q={}
  GET  /api/items/search?q={}&purpose={}
====================================================================

Press Ctrl+C to stop the server

 * Running on http://127.0.0.1:5001
```

**중요:** `Items Loaded: 9237` 이 숫자가 나와야 성공!

---

## 🧪 테스트

### 1. 브라우저에서 Health Check
```
http://127.0.0.1:5001/api/health
```

**기대 결과:**
```json
{
  "status": "ok",
  "message": "BFL LIMS Receipt API Server",
  "data_source": "food_item_fee_mapping.js",
  "items_loaded": 9237,  ← 확인!
  "timestamp": "2026-02-18T..."
}
```

### 2. 검사목적 조회 (실제 데이터!)
```
http://127.0.0.1:5001/api/test-purposes?field=식품
```

**기대 결과:**
```json
{
  "field": "식품",
  "purposes": [
    "Allergen(RT-PCR)",
    "Halal food(RT_PCR)",
    "Vegan food(RT-PCR)",
    "물질검사",
    "방사능(HPGe)",
    "연구용역",
    "자가품질위탁검사용",
    "잔류농약(참고용)",
    "접수취소",
    "참고용(기준규격외)",
    "참고용(소비기한설정)",
    "참고용(영양성분)",
    "참고용(외부의뢰)",
    "표시기준"
  ],
  "count": 14,
  "source": "food_item_fee_mapping.js"
}
```

### 3. 검체유형 조회
```
http://127.0.0.1:5001/api/food-types?field=식품&purpose=자가품질위탁검사용
```

### 4. 검사항목 검색
```
http://127.0.0.1:5001/api/items/search?q=대장균&purpose=자가품질위탁검사용
```

---

## 🎯 데이터 흐름 확인

```
food_item_fee_mapping.js (9,237건)
        ↓
receipt_api_final.py (파싱)
        ↓
✅ Items Loaded: 9237
        ↓
API 엔드포인트 제공
        ↓
시료접수.html (호출)
```

---

## ⚠️ 문제 해결

### 문제 1: Items Loaded: 0
```
⚠️  Warning: food_item_fee_mapping.js not found!
```

**원인:** JS 파일을 못 찾음

**해결:**
```powershell
# 파일 위치 확인
ls C:\Users\user\Desktop\bfl_lims\js\food_item_fee_mapping.js

# 없으면 다시 배치
move C:\Users\user\Downloads\food_item_fee_mapping.js C:\Users\user\Desktop\bfl_lims\js\
```

### 문제 2: 모듈 없음 (ModuleNotFoundError)
```
ModuleNotFoundError: No module named 'flask'
```

**해결:**
```powershell
pip install flask flask-cors
```

### 문제 3: 포트 사용 중
```
Address already in use
```

**해결:**
```powershell
# 다른 프로그램 종료 또는
# receipt_api_final.py 마지막 줄 수정:
# port=5001 → port=5002
```

---

## 📊 실제 데이터 통계

### food_item_fee_mapping.js 내용
```
총 건수: 9,237건

검사목적별 (16개):
- 참고용(기준규격외): 3,374건
- 참고용(영양성분): 2,521건
- 잔류농약(참고용): 1,442건
- 자가품질위탁검사용: 1,021건
- 항생물질(참고용): 348건
- 참고용(소비기한설정): 271건
- 연구용역: 71건
- Allergen(RT-PCR): 70건
- 방사능(HPGe): 51건
- Allergen(ELISA): 47건
- ... 나머지 6개
```

### 데이터 필드
```javascript
{
  purpose: '자가품질위탁검사용',  // 검사목적
  foodType: 'Sample',             // 검체유형
  bracket: '',                    // 괄호정보
  item: '대장균',                  // 항목명
  fee: 15000,                     // 수수료
  count: 1                        // 횟수
}
```

---

## 🎉 성공 체크리스트

- [ ] JS 파일 배치 완료
- [ ] API 서버 실행 성공
- [ ] `Items Loaded: 9237` 확인
- [ ] Health Check 통과
- [ ] 검사목적 14개 조회 성공
- [ ] 검체유형 조회 성공

---

## 🔜 다음 단계

### 1. HTML 파일 수정
시료접수.html의 API 주소를 변경:
```javascript
// 변경 전
const API_BASE = 'http://127.0.0.1:5000';

// 변경 후
const API_BASE = 'http://127.0.0.1:5001';
```

### 2. 브라우저에서 테스트
```
C:\Users\user\Desktop\bfl_lims\시료접수.html 더블클릭
```

---

## 💡 핵심 포인트

### ✅ 실제 데이터 활용
- 하드코딩 제거 ❌
- JS 파일 파싱 ✅
- 9,237건 실시간 로드 ✅

### ✅ 검사분야 자동 구분
```python
# 검체유형과 검사목적으로 식품/축산 구분
- 축산: 가공치즈, 소시지, 햄, 양념육 등
- 식품: 나머지
```

### ✅ 동적 추출
```python
# 매번 실시간으로 추출
extract_test_purposes()   # 검사목적 16개
extract_food_types()      # 검체유형 220개
```

---

**실행해보시고 결과 알려주세요!** 🚀

1. `Items Loaded: 9237` 나오나요?
2. Health Check 성공하나요?
3. 검사목적 조회되나요?

문제 있으면 에러 메시지 전체를 보내주세요!
