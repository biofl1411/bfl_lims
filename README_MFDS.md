# 식약처 통합LIMS WEB API 연동

> 메인 문서: [README.md](README.md)

---

## 🔴 식약처 통합LIMS WEB API 연동 (진행 중 — 2026-03-01 갱신)

> **이 섹션은 프롬프트 재시작 시 이어서 작업할 수 있도록 진행 상황을 기록합니다.**
> **실패가 2회 이상 발생하면, `mfds_integration/` 폴더의 전체 내용(PDF 가이드, Sample 소스, 코드매핑 Excel 등)을 정밀히 확인하여 해결하세요.**

### 개요
- 식품 분야만 연동 (의약품/의료기기 제외)
- 업무분야코드: `IM36000001` (식품)
- 아키텍처: `BFL LIMS (HTML+JS)` → `nginx 프록시` → `중간모듈 (Java WAR/Tomcat)` → `식약처 통합LIMS API`
- 문서/샘플 위치: `mfds_integration/` 폴더
- 테스트URL: https://wslims.mfds.go.kr
- 테스트 페이지(식약처): https://wslims.mfds.go.kr/ApiClient/ (시나리오별 수동 테스트 가능)
- 테스트 페이지(자체): https://192.168.0.96:8443/mfdsTest.html (연결 + 전체 API 테스트)

### 서버 환경 (192.168.0.96)
- **Java**: OpenJDK 17.0.18 (설치 완료)
- **Tomcat**: 9.0.98 → `/home/biofl/tomcat` (포트 8080, 수동 설치)
- **WAR 배포**: `/home/biofl/tomcat/webapps/LMS_CLIENT_API` (배포 완료, Spring MVC 정상 로드)
- **인증서**: `/home/biofl/mfds_certs/O000170.jks` (테스트), `O000026.jks` (운영)
- **파일 저장**: `/home/biofl/mfds_files/`
- **Tomcat 시작/종료**: `/home/biofl/tomcat/bin/startup.sh` / `shutdown.sh`
- **setenv.sh**: `JAVA_HOME`, `CATALINA_HOME`, `CATALINA_PID` 설정 완료
- **서버 시간**: UTC (NTP 동기화 활성), 타임존은 인증에 영향 없음 (epoch ms 사용)
- **네트워크**: enp4s0 (MAC: `00:24:54:91:d8:12`, UP 상태)

### application.properties (현재 설정 — 2개 파일)

**1) ResourceBundle용 (실제 인증에 사용됨):**
```properties
# 위치: /home/biofl/tomcat/webapps/LMS_CLIENT_API/WEB-INF/classes/application.properties
keyStore.keyStoreLoc=/home/biofl/mfds_certs/O000170.jks
KeyStore.keyPassWord=mfds2015
keyStore.keyAlias=O000170
fileDownloadPath=/home/biofl/mfds_files
wslimsUrl=https://wslims.mfds.go.kr
keyStore.clientEthName=enp4s0
```

**2) Spring config용 (동일 내용 유지):**
```properties
# 위치: /home/biofl/tomcat/webapps/LMS_CLIENT_API/WEB-INF/config/application.properties
keyStore.keyStoreLoc=/home/biofl/mfds_certs/O000170.jks
KeyStore.keyPassWord=mfds2015
keyStore.keyAlias=o000170
fileDownloadPath=/home/biofl/mfds_files
wslimsUrl=https://wslims.mfds.go.kr
keyStore.clientEthName=enp4s0
```

> **주의**: `ResourceBundle.getBundle("application")`는 `WEB-INF/classes/`에서 읽음.
> `WEB-INF/config/`는 Spring의 `<util:properties>`에서 읽음.
> 두 파일 모두 수정해야 설정이 제대로 반영됨.

### 서버 설정 변경 이력 (WAR 내부 수정 — git 미추적)
| 파일 | 변경 내용 | 날짜 |
|------|----------|------|
| `WEB-INF/spring/appServlet/servlet-context.xml` | `StringHttpMessageConverter` UTF-8 추가 (한글 깨짐 해결) | 2026-02-26 |
| `WEB-INF/web.xml` | `CharacterEncodingFilter` `forceEncoding=true` 추가 | 2026-02-26 |
| `conf/server.xml` (Tomcat) | Connector에 `URIEncoding="UTF-8"` 추가 | 2026-02-26 |
| `WebApiController.class` | 5파라미터 생성자 사용 (clientEthName) | 2026-02-25 |

> **⚠️ 주의**: 이 파일들은 서버의 `/home/biofl/tomcat/` 아래에 있으며, git으로 추적되지 않음.
> WAR를 재배포하면 이 설정이 초기화되므로 반드시 다시 적용해야 함.
> 원본 백업: `WebApiController.class.bak`

### 인증서 정보
| 파일 | alias | 비밀번호 | 용도 | CN | 유효기간 |
|------|-------|----------|------|-----|----------|
| `O000170.jks` | `o000170` | `mfds2015` | 테스트(공용) | CN=O000170 | 2025-12-18 ~ 2029-12-18 |
| `O000026.jks` | `o000026` | `mfds2015` | 운영(바이오푸드랩) | CN=O000026 | 2026-02-25 ~ 2030-02-25 |

> 두 JKS 모두 `alias "1"`에 `*.mfds.go.kr` trustedCertEntry 포함 (mTLS용)
> MD5: O000170.jks = `9dd0538f54c56a6d6d63077fc803824c` (서버/로컬 동일 확인)

### 인증 흐름 (개발가이드 2.4절, 3.2절 기반)

```
검사기관 시스템                    JAVA 중간 모듈                     통합LIMS WEB API
─────────────                   ─────────────                    ────────────────
기관코드/기관ID    ──────→    # 인증값 생성                        기관 전송 데이터 수신
시나리오별 JSON 데이터            - Server MAC 취득
                              - 서버시간(Timestamp)               # 기관 인증 값 수신
                              - 검사기관 인증서(JKS)              # 서버측 인증 값 생성
                              + 기관코드/기관ID                      (서버용/기관코드)
                              + 시나리오별 JSON 데이터
                              ─── SSL 통신 ──────→              기관 인증 값 vs 서버 인증 값 비교
                                                                  │
                                                                  ├→ MAC Address 검증 (1순위)
                                                                  ├→ 인증서 검증 (2순위)
                                                                  └→ 유효성 체크 (3순위)
                                                                  │
서비스 결과 수신    ←─────────── 서비스 결과 수신 ←──────── 결과 전송 / 오류 처리
```

**인증값 생성 과정 (AuthenticateCert.setCertCode):**
1. `data = timestamp + macAddr` (예: `177207770551500-24-54-91-D8-12`)
2. `sign = SHA256withRSA(data, privateKey)` — JKS 개인키로 RSA 서명
3. `certCryp = SHA-256(sign)` — 서명의 해시값
4. `time = RSA_Encrypt(timestamp, publicKey)` — 타임스탬프만 RSA 암호화
5. `certValue = {mfdsLimsId, psitnInsttCode, ..., certCryp, time}` — JSON 조립

**서버측 검증 과정 (추정):**
1. mTLS로 클라이언트 인증서의 CN 확인 → 기관코드 식별
2. `time` 복호화 → 타임스탬프 추출
3. DB에서 해당 기관의 **등록된 MAC 주소** 조회
4. `data = timestamp + 등록된MAC`으로 인증값 재계산
5. 클라이언트가 보낸 `certCryp`와 비교 → 일치하면 인증 성공

> **핵심**: certValue JSON에 macAddr 필드는 없음! 서버는 DB에 등록된 MAC으로 인증값을 재계산하여 비교함.
> **따라서 MAC이 서버에 정확히 등록되지 않으면 인증은 절대 통과할 수 없음.**

### 중간모듈 WAR 구조 (LMS_CLIENT_API)

**배포된 컨트롤러** (`WebApiController.class` — 수정됨):
| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `POST /LMS_CLIENT_API/selectUnitTest` | `selectUnitTest(String)` | REST/SOAP API 호출 (JSON) |
| `POST /LMS_CLIENT_API/selectUnitTestFile` | `selectUnitTest(MultipartHttpServletRequest)` | 파일 포함 API 호출 |
| `GET/POST /LMS_CLIENT_API/unitTestFileDownLoad` | `unitTestFileDownLoad(Model)` | 파일 다운로드 |

> **수정사항**: `keyStore.clientEthName` 설정이 있으면 5파라미터 생성자
> `new AuthenticateCert(keyStoreLoc, alias, passWord, clientEthName, context)` 사용.
> 원본 백업: `WebApiController.class.bak`

**요청 JSON 형식** (`selectUnitTest` — REST 방식):
```json
{
  "type": "rest",
  "url": "https://wslims.mfds.go.kr/webService/rest/selectListCmmnCode",
  "param": {"mfdsLimsId": "apitest01", "psitnInsttCode": "O000170", "classCode": "IM36"}
}
```
- `type`: `"rest"` 또는 `"soap"`
- `url`: REST는 `https://wslims.mfds.go.kr/webService/rest/` + 서비스명
- `param`: JSON 객체 (필수 필드: `mfdsLimsId`, `psitnInsttCode`는 반드시 **최상위 레벨**에 포함)

**요청 JSON 형식** (`selectUnitTest` — SOAP 방식):
```json
{
  "type": "soap",
  "url": "/selectListCmmnCode",
  "param": {"mfdsLimsId": "apitest01", "psitnInsttCode": "O000170", "classCode": "IM36"}
}
```
- SOAP에서 `url`은 도메인 없이 서비스명만 (예: `/selectListCmmnCode`)

### 테스트 계정 정보 (O000170 공용 테스트 기관)
- 계정: `apitest01` ~ `apitest20` (기관관리자 권한)
- 웹 로그인 비밀번호: `ODSxcBii` (임시, 마이페이지에서 변경)
- 기관코드: `O000170` (psitnInsttCode)
- 테스트 페이지: https://wslims.mfds.go.kr/ApiClient/
- **주의**: O000170은 여러 기관이 공유하는 테스트 기관. 다른 기관의 테스트 데이터를 수정하지 않도록 주의

### 완료된 작업 ✅
1. ✅ Java 17 설치 확인
2. ✅ Tomcat 9.0.98 설치 (`/home/biofl/tomcat`)
3. ✅ LMS_CLIENT_API.war 배포 (Spring MVC 정상 로드)
4. ✅ 인증서 배치 (`/home/biofl/mfds_certs/`)
5. ✅ application.properties 설정 (테스트 환경, 2개 파일 모두)
6. ✅ `javax.activation-1.2.0.jar` 추가 (Java 17 호환성 해결)
7. ✅ setenv.sh 환경변수 설정
8. ✅ MAC 주소 감지 문제 해결 (clientEthName=enp4s0 설정)
9. ✅ WebApiController 수정 — 5파라미터 생성자로 MAC 명시적 전달
10. ✅ Tomcat 로그로 MAC 포함 확인 (`data:177207770551500-24-54-91-D8-12`)

### ✅ 인증 이슈 해결 완료 (2026-02-26)

**이전 이슈:** "유효하지 않는 인증정보입니다" → **해결됨!**

**원인 2가지:**
1. **MAC 주소 등록 형식 오류**: 식약처 DB에 MAC이 `:` 구분자로 등록되었으나, 실제로는 `-` 구분자가 필요했음
   - 이누리 대리(통합림스)가 2026-02-26 09:30경 MAC 재등록 완료
2. **`webApi: "Y"` 미전송 (가이드 미수록 필수 파라미터)**: 모든 API 호출에 `"webApi":"Y"`를 포함해야 함
   - 이누리 대리가 이메일로 직접 안내한 파라미터 (공식 가이드에 없음!)
   - `mfds-api.js`의 `callApi()`, `testConnection()` 모두 수정 완료

**추가 해결: 한글 깨짐 (인코딩)**
- 증상: API 응답의 한글이 `??` 또는 `-`로 표시됨
- 해결: Spring MVC `servlet-context.xml`에 `StringHttpMessageConverter` UTF-8 추가
  ```xml
  <mvc:annotation-driven>
    <mvc:message-converters>
      <bean class="org.springframework.http.converter.StringHttpMessageConverter">
        <constructor-arg value="UTF-8"/>
      </bean>
    </mvc:message-converters>
  </mvc:annotation-driven>
  ```
- `CharacterEncodingFilter`의 `forceEncoding=true`만으로는 부족, `URIEncoding="UTF-8"`도 불충분

**연결 테스트 결과 (2026-02-26 전체 통과):**
| 테스트 | API | 결과 | 데이터 |
|--------|-----|------|--------|
| 1 | `selectListCmmnCode` (공통코드) | ✅ 성공 | 9건 |
| 2 | `selectListInspctReqest` (의뢰목록) | ✅ 성공 | 236건 |
| 3 | `selectListDept` (부서목록) | ✅ 성공 | 28건 (바이오푸드랩 D003194 포함) |
| 4 | `selectListEmp` (직원목록) | ✅ 성공 | 1건 — API테스터34(apitest34) / L0330159 |
| 5 | `selectListPrdlstLclas` (품목분류대분류) | ✅ 성공 | 18건 |

> 테스트 페이지: `https://192.168.0.96:8443/mfdsTest.html` (연결 테스트 + 전체 API 테스트)

### API 필드명 주의사항 ⚠️

식약처 API 응답 필드명이 직관적이지 않으므로 주의 필요:

| API | 예상했던 필드명 | **실제 필드명** | 비고 |
|-----|---------------|----------------|------|
| `selectListDept` | deptCode, deptName | **codeNo, codeName** | 부서 목록 |
| `selectListEmp` | empCode, empName | **codeNo, codeName** | 직원 목록, `deptCode` 필수 파라미터 |
| `selectListPrdlstLclas` | - | **codeNo, codeName** | `jobRealmCode` 필수 파라미터 |
| `selectListCmmnCode` | - | **codeNo, codeName** | 공통코드 |

> **규칙**: 대부분의 조회 API가 `codeNo` / `codeName` 형태로 응답함.
> 서비스별 필수 파라미터가 다르므로, 호출 전 반드시 서비스별 가이드 PDF 확인 필요.
> 존재하지 않는 서비스명(예: `selectListUser`)은 빈 응답(HTTP 200, body 없음)을 반환하므로 주의.

### 완료된 작업 ✅ (2026-02-26 전체)

**인프라:**
1. ✅ Java 17 설치 확인
2. ✅ Tomcat 9.0.98 설치 (`/home/biofl/tomcat`)
3. ✅ LMS_CLIENT_API.war 배포 (Spring MVC 정상 로드)
4. ✅ 인증서 배치 (`/home/biofl/mfds_certs/`)
5. ✅ application.properties 설정 (테스트 환경, 2개 파일 모두)
6. ✅ `javax.activation-1.2.0.jar` 추가 (Java 17 호환성 해결)
7. ✅ setenv.sh 환경변수 설정
8. ✅ MAC 주소 감지 문제 해결 (clientEthName=enp4s0 설정)
9. ✅ WebApiController 수정 — 5파라미터 생성자로 MAC 명시적 전달
10. ✅ MAC 주소 재등록 (`-` 구분자로 수정, 이누리 대리 확인)
11. ✅ `webApi: "Y"` 필수 파라미터 추가
12. ✅ UTF-8 인코딩 수정 (StringHttpMessageConverter)
13. ✅ nginx 프록시 설정 (`/mfds/` → Tomcat 8080 LMS_CLIENT_API)

**프론트엔드 JS 모듈:**
14. ✅ `js/mfds-api.js` — 식약처 API 호출 모듈
    - `MFDS.callApi(serviceName, params)` → nginx → Tomcat → 식약처 API
    - 래퍼 함수: 의뢰(01xx), 시험(02xx), 성적서(03xx), 진행상황(04xx), 기관(06xx), 공통(08xx)
    - Firestore 캐시 기능 (`mfds_cache` 컬렉션)
    - `selectListEmp`에 `deptCode` 필수 검증 추가
15. ✅ `js/mfds-codes.js` — 코드매핑 데이터 로딩/캐싱/검색 공통 모듈 (522줄)
    - 품목코드 8,404건 / 시험항목 2,940건 / 단위 106건 / 공통코드 383건 Firestore 로드
    - 품목코드 3단 계층 트리 (대분류→중분류→소분류) 빌드
    - 캐스케이딩 드롭다운 + 텍스트 검색 렌더링 (`renderProductPicker`)
    - BFL↔식약처 항목 매핑 CRUD (`mfds_item_mappings` 컬렉션)

**페이지 연동:**
16. ✅ `sampleReceipt.html` — 식약처 품목코드 선택 UI 추가
    - 시료정보 섹션에 3단 캐스케이딩 드롭다운 + 검색 필드
    - 연한 파란색 배경으로 식약처 영역 구분
    - 멀티 시료 전환 시 선택값 복원, 접수 저장 시 `mfdsProductCode`/`mfdsProductName` 포함
    - 접수 이력 불러오기에서 품목코드 복원
17. ✅ `inspectionMgmt.html` — 시험항목 브라우저 + 매핑 모달 추가
    - Panel 3: 시험항목 2,940건 검색/테이블/페이지네이션 (50건/페이지)
    - 매핑 모달: 식약처 시험항목 ↔ BFL 항목명 연결 + 단위코드 선택
    - Panel 4: 항목그룹 4개 렌더링 위치 모두에 매핑 뱃지(✅/⚠) + 🔗 버튼
    - Excel 매핑 내보내기 기능
18. ✅ `mfdsTest.html` — 식약처 API 연결 테스트 페이지
    - 연결 테스트 (5항목 체크리스트) + 전체 API 테스트 (5개 API)
19. ✅ Firestore 코드매핑 데이터 업로드 완료
    - `mfds_common_codes` 383건, `mfds_product_codes` 8,404건
    - `mfds_test_items` 2,940건, `mfds_units` 106건

**추가 완료 (2026-02-27~28):**

20. ✅ `js/mfds_templates.js` — 식약처 시험항목 템플릿 데이터 (74,903줄)
    - 식약처 코드매핑 `mfdsTemplates` XLS → JS 변환 (646 템플릿, 2,657개 시험항목)
    - Firestore `mfdsTemplates` 컬렉션 임포트 기능
    - 접수등록에서 식품유형 선택 시 시험항목 자동 로드에 활용
21. ✅ `js/mfds_result_rules.js` — 식약처 결과값 처리 규칙 모듈 (157줄)
    - `applyValidCphr(value, precision)` — 유효자리수 반올림
    - `applyFdqntLimit(value, item)` — 정량한계 미만 시 불검출 처리
    - `generateMarkValue(value, item)` — 표기값 생성 (유효자리수 + 정량한계 통합)
    - `mapJdgmntFomCode(type)` — IM15 판정형식 코드 매핑 (최대/최소→01, 적/부→02 등)
    - `mapJdgmntWordCode(result)` — IM35 판정용어 코드 매핑 (적합→IM35000001 등)
    - `mapMaxValueSeCode/mapMinValueSeCode` — IM16/IM17 이하/미만/이상/초과 구분
    - `processResultValue(raw, item, judgment)` — 전체 처리 통합 함수
22. ✅ `js/mfds-fee-mapping.js` — 수수료 매핑 데이터 (178줄)
    - 식약처 수수료 체계 기반 검사목적별 수수료 매핑
23. ✅ `js/food_types_qc.js` — 식품유형 품질관리 모듈 (1,031줄)
    - 식품유형 데이터 무결성 검증, 중복 체크
24. ✅ `testResultInput.html` — 검사결과 입력 페이지 전면 신규 구현 (2,010줄)
    - 접수현황에서 접수건 선택 → 시료별 시험항목 렌더링
    - 측정값 입력 → MFDS_RULES 자동 적용 (유효자리수, 정량한계, 표기값)
    - 자동판정 (적합/부적합/검출/불검출) — 최대값/최소값 기준 비교
    - Firestore 저장/복원 (`testResults` 컬렉션)
    - 식약처 전송 기능: 시험일지 등록(0209) + 결과 전송(0216) 2단계
    - 전송 전 확인 모달 (항목별 측정값/표기값/판정 테이블 미리보기)
25. ✅ `js/mfds_diary_form.js` — 시험일지 양식 뷰어 모듈 (198줄)
    - API 체인: exprIemCode → 0241(selectListExprMth) → exprMthSn → 0242(selectListExprDiaryForm) → codename2(HTML)
    - 사용범위코드 3단계 조회: 개인(SY05000003) → 부서(SY05000002) → 기관(SY05000001)
    - `renderInteractive(html, container)` — 빈 `<td>` 셀을 contenteditable로 변환
    - `collectFormHtml(container)` — 편집된 HTML 수집 (clean)
    - 결과 캐시 지원 (API 재호출 방지)
    - testResultInput.html에 [양식] 버튼으로 연동 — 항목별 시험일지 양식 조회/표시
    - **운영 서버 검증 완료**: 납(B10001) → 중금속_납_일지 [개인] 양식 정상 조회 확인

**페이지 연동 (2026-02-27~28):**

26. ✅ `sampleReceipt.html` — 식약처 연동 확장
    - 검사목적별 UI 분기: 자가품질위탁검사용 → 식약처 연동 모드 활성화
    - 식품유형(mfdsTemplates) 선택 시 시험항목 자동 로드
    - 참고용(기준규격외) MFDS 시험항목 2,940건 검색/추가 기능
    - 수수료 계산: 참고용 + 자가품질위탁검사용 테이블 직접 합산
27. ✅ `inspectionMgmt.html` — 수수료 식약처 코드 매핑 서브탭 추가
28. ✅ `itemAssign.html` — 시험일지 관련 API 9개 래퍼 추가 + 일지 관리 UI 구현

### ✅ 31단계 테스트 시나리오 전체 통과 (2026-02-26)

식약처 테스트 시나리오 엑셀 기반, **의뢰→시료→결과→결재→성적서** 전체 흐름 검증 완료.

| 단계 | 서비스 | 설명 | 결과 | 핵심 데이터 |
|------|--------|------|------|-------------|
| 1 | `saveInspctReqest` | 의뢰등록 | ✅ | 임시번호: T0260100020 |
| 2 | `selectListInspctReqest` | 의뢰조회 | ✅ | 등록 확인 |
| 3 | `saveReqestSplore` | 시료등록 | ✅ | sploreSn=1, 3항목 |
| 4 | `selectListReqestSplore` | 시료조회 | ✅ | |
| 5 | `selectListReqestSploreExprIem` | 시험항목조회 | ✅ | 3건 (타르색소/대장균군/세균수) |
| 6 | `saveReqestSploreFee` | 수수료저장 | ✅ | 12,100원 |
| 7 | `saveInspctReqestRequst` | 의뢰요청 | ✅ | **정식번호: 260100059** |
| 10 | `saveSploreChargerAsign` | 접수배정 | ✅ | apitest34 배정 |
| 11 | `insertExprDiary` | 시험일지 | ✅ | exprDiarySn=24160551 |
| 16 | `saveSploreInspctResult` | 결과입력 | ✅ | 불검출/음성 |
| 21 | `saveSploreSanctnRecom` | 결재상신 | ✅ | |
| 28 | `saveSploreSanctn` | 최종결재 | ✅ | 1건 완료/총 1건 |
| 29 | `saveGrdcrtIssu` | 성적서발급 | ✅ | IM27000001/IM42000001 |
| 30 | `selectGrdcrtDmOutpt` | DM출력 | ✅ | DM_ADRESS_260100059.pdf (23KB) |
| 31 | `selectGrdcrtPdfOutpt` | PDF출력 | ⚠️ | 파일 다운로드 형식 (빈 JSON) |

**31단계 테스트 중 발견된 주요 사항:**

| 항목 | 내용 |
|------|------|
| `inspctInsttCntcValue` | 가이드 미수록 필수필드, reqestInfo에 포함 필요 (max 60자) |
| 품목코드 형식 | 2018년 `C01xxxxx` 형식 무효 → 현재 `A01xxxxx` 형식 사용 |
| `feeSeCode` | `IM26000004`(개별) 사용, `IM26000001`(그룹)은 feeGroupSn 필요 |
| `sploreChargerId` | `mfdsLimsId` 형식(apitest34) 사용, codeNo(L0330159) 불가 |
| `fdqntLimitApplcAt` | 결과입력 시 각 항목에 `"N"` 필수 |
| `jobSeCode` | 대부분의 write 서비스에 `"IM18000001"` 필수 |
| `prductNm` | 시료등록 시 제품명 필수 (가이드에 비중 낮게 표기됨) |

**미들웨어 URL 수정 (2026-02-26):**
- **문제**: `WebApiController.selectUnitTest()`가 서비스명만 AuthenticateCert에 전달 → `HttpPost("saveXxx")` → "Target host is not specified"
- **원인**: 원본 JSP 페이지에서는 `wslimsUrl + "/webService/rest/" + serviceName`으로 전체 URL 조합 후 전달했으나, `selectUnitTest`에는 이 로직이 없었음
- **해결**: `WebApiController.java`에 `buildRestUrl()` 메서드 추가, `url`이 `http`로 시작하지 않으면 자동으로 `wslimsUrl + "/webService/rest/"` 프리픽스 추가
- **파일**: `/home/biofl/tomcat/webapps/LMS_CLIENT_API/WEB-INF/classes/gov/mfds/lms_client/Controller/WebApiController.class` (Java 17 컴파일)

### ⏳ 다음 작업 (우선순위, 2026-03-01 갱신)

**1순위 — 관리자 > API 수집 검증:**
- `admin_api_settings.html` — API 수집 설정 페이지 검증
- `admin_collect_status.html` — 수집 현황 페이지 검증
- `api_server.py` (Flask port 5003) — 데이터 수집 서버 검증
- `collector.py` — 식약처 데이터 수집기 검증

**2순위 — 시험일지 양식 검토 (차주 예정):**
- 시험일지 양식 뷰어 (API 0241→0242) 실무 활용 검토
- 양식 편집 → 시험일지 등록(0209) 연동 완성
- 계산식(nomfrmCn) 구현: API에서 제공하는 계산식 데이터만 사용 (인터넷 검색 금지)

**3순위 — 접수등록 ↔ 식약처 의뢰 연동:**
- `sampleReceipt.html`에서 접수 저장 시 식약처 `saveInspctReqest` API 동시 호출
- 의뢰번호(`sploreReqestNo`) 발급받아 Firestore `receipts`에 저장
- 시료 정보도 `saveReqestSplore` API로 동시 전송
- 오류 시 식약처 연동만 실패하고 BFL 접수는 정상 저장되도록 독립 처리

**4순위 — 검사결과 입력 ↔ 식약처 연동 보강:**
- ✅ 시험일지 등록 (`insertExprDiary`) — 기본 구현 완료
- ✅ 검사결과 전송 (`saveSploreInspctResult`) — 기본 구현 완료
- ⏳ 계산식 결과 등록 (`insertExprDiaryCalcFrmlaResult`) — API 0210, 래퍼만 존재
- ⏳ 결재상신 (`saveSploreSanctnRecom`) — 미구현
- BFL 항목명 → 식약처 시험항목코드 매핑 활용 (`mfds_item_mappings`)

**5순위 — 성적서 발급 연동:**
- 성적서 발급 (`saveGrdcrtIssu`)
- 성적서 이력 조회 (`selectListGrdcrtIssuHist`)
- PDF 다운로드 연동

**6순위 — 운영 환경 전환:**
- 테스트(O000170) → 운영(O000026) 인증서/기관코드 전환
- `mfds-api.js`의 `DEFAULT_USER` 설정 변경
- application.properties 인증서 경로 변경
- 운영 MAC 등록 요청 (식약처)

### 식약처 연동 담당자 정보
| 구분 | 이름 | 연락처 | 비고 |
|------|------|--------|------|
| 통합LIMS 담당 | 이누리 대리 | - | MAC 재등록, webApi:Y 안내 |
| 운영·관리 | jhk0821@korea.kr | 043-234-3100 | 정보화도움터 |

### 트러블슈팅 기록
| 문제 | 원인 | 해결 | 상태 |
|------|------|------|------|
| `NoClassDefFoundError: javax.activation` | Java 17에서 모듈 제거됨 | `javax.activation-1.2.0.jar` 추가 | ✅ |
| Tomcat 포트 충돌 | 기존 Tomcat 이미 실행 중 | 중복 설치 삭제, 기존 인스턴스 활용 | ✅ |
| WAR에 JSP 없음 | 중간모듈 전용 빌드 | 정상 — API 호출만 제공 | ✅ |
| MAC 미감지 (`data`에 MAC 없음) | `/etc/hosts`가 hostname→127.0.1.1 매핑, `getLocalHost()`→loopback→NI null | `clientEthName=enp4s0` 설정 + WebApiController 5파라미터 생성자 | ✅ |
| `classes/` vs `config/` 혼동 | ResourceBundle은 `classes/`에서 읽음, Spring은 `config/`에서 읽음 | 두 파일 모두 설정 통일 | ✅ |
| **유효하지 않는 인증정보** | MAC 등록 형식 오류(`:` → `-`) + `webApi:"Y"` 미전송 | 이누리 대리 MAC 재등록 + `mfds-api.js`에 `webApi:"Y"` 추가 | ✅ |
| **한글 깨짐 (API 응답)** | Spring MVC 기본 인코딩이 ISO-8859-1 | `servlet-context.xml`에 `StringHttpMessageConverter` UTF-8 추가 | ✅ |
| **Test 3 부서목록 `-` 표시** | 필드명 불일치 (`deptCode`→`codeNo`, `deptName`→`codeName`) | `mfdsTest.html` 필드명 수정 | ✅ |
| **Test 4 직원목록 실패** | 서비스명 오류(`selectListUser`→`selectListEmp`) + `deptCode` 필수 누락 | 서비스명/파라미터 수정 | ✅ |
| **Test 5 품목분류 실패** | `jobRealmCode` 필수 파라미터 누락 | `jobRealmCode: 'IM36000001'` 추가 | ✅ |
| **Tomcat 재시작 실패** | shutdown.sh 후 기존 프로세스가 남아 8080 포트 점유 | 프로세스 완전 종료 대기 후 startup.sh | ✅ |
| **API 호출 빈 응답 (Content-Length:0)** | `selectUnitTest`가 서비스명만 전달 → `HttpPost("saveXxx")` 호스트 없음 | `WebApiController.buildRestUrl()` 추가, `wslimsUrl + "/webService/rest/"` 자동 프리픽스 | ✅ |
| **Step 3 시료등록 품목코드 오류** | 2018년 테스트코드(`C0113010000000`) 무효 | `A0100100000000` (쌀) 사용 | ✅ |
| **Step 10 접수배정 사용자ID 오류** | `codeNo`(L0330159) 대신 `mfdsLimsId`(apitest34) 사용해야 함 | ID 형식 변경 | ✅ |

### 식약처 연동 구현 현황 상세 (2026-03-01 기준)

#### JS 모듈 구성

| # | 파일 | 줄수 | 역할 | 의존성 |
|---|------|------|------|--------|
| 1 | `js/mfds-api.js` | 634 | API 호출 코어 (26개 래퍼 함수) | Firebase, nginx |
| 2 | `js/mfds-codes.js` | 652 | 코드매핑 로딩/캐싱/검색 | Firebase |
| 3 | `js/mfds_result_rules.js` | 157 | 결과값 처리 규칙 (유효자리수/정량한계/판정코드) | — |
| 4 | `js/mfds_templates.js` | 74,903 | 식약처 시험항목 템플릿 데이터 (646템플릿) | — |
| 5 | `js/mfds_diary_form.js` | 198 | 시험일지 양식 뷰어 (API 0241→0242) | mfds-api.js |
| 6 | `js/mfds-fee-mapping.js` | 178 | 수수료 매핑 데이터 | — |
| 7 | `js/food_types_qc.js` | 1,031 | 식품유형 품질관리 | — |
| 8 | `js/food_item_fee_mapping.js` | 9,261 | 식품항목-수수료 매핑 (9,237건) | — |

#### API 래퍼 함수 현황 (`mfds-api.js`)

| 분류 | 서비스ID | 래퍼 함수 | 실제 호출 여부 |
|------|---------|----------|:---:|
| **의뢰관리** | 0101 | `selectListInspctReqest` | ✅ |
| | 0104 | `saveInspctReqest` | ✅ (31단계 테스트) |
| | 0105 | `saveInspctReqestRequst` | ✅ (31단계 테스트) |
| | 0106 | `selectListReqestSplore` | ✅ (31단계 테스트) |
| | 0107 | `saveReqestSplore` | ✅ (31단계 테스트) |
| | 0108 | `selectListReqestSploreExprIem` | ✅ (31단계 테스트) |
| | 0109 | `saveReqestSploreFee` | ✅ (31단계 테스트) |
| | 0115 | `saveSploreChargerAsign` | ✅ (31단계 테스트) |
| **시험/결과** | 0202 | `selectListExprDiaryByExprIemSn` | ⏳ 래퍼만 |
| | 0206 | `selectListExprDiary` | ⏳ 래퍼만 |
| | 0207 | `selectExprDiaryDtl` | ⏳ 래퍼만 |
| | 0208 | `deleteExprDiary` | ⏳ 래퍼만 |
| | 0209 | `insertExprDiaryNew` | ✅ (testResultInput) |
| | 0210 | `insertExprDiaryCalcFrmlaResult` | ⏳ 래퍼만 |
| | 0216 | `saveSploreInspctResult` | ✅ (testResultInput) |
| | 0219 | `saveSploreSanctnRecom` | ⏳ 래퍼만 |
| | 0221 | `saveSploreSanctn` | ✅ (31단계 테스트) |
| | 0241 | `selectListExprMth` | ✅ (양식뷰어) |
| | 0242 | `selectListExprDiaryForm` | ✅ (양식뷰어) |
| **성적서** | 0309 | `saveGrdcrtIssu` | ✅ (31단계 테스트) |
| | 0310 | `selectListGrdcrtIssuHist` | ⏳ 래퍼만 |
| | 0311 | `selectGrdcrtDmOutpt` | ✅ (31단계 테스트) |
| | 0312 | `selectGrdcrtPdfOutpt` | ✅ (31단계 테스트) |
| **기관/사용자** | 0601 | `selectListDept` | ✅ |
| | 0602 | `selectListEmp` | ✅ |
| **공통** | 0801 | `selectListCmmnCode` | ✅ |
| | 0818 | `selectListPrdlstLclas` | ✅ |

> **26개 래퍼 중 19개 실제 호출 확인**, 7개는 래퍼만 존재 (향후 UI 연동 예정)

#### Firestore 컬렉션 (식약처 관련)

| 컬렉션 | 건수 | 용도 | 출처 |
|--------|------|------|------|
| `mfds_common_codes` | 383 | 공통코드 (IM15, IM16, IM17, IM35, IM43 등) | 코드매핑 Excel |
| `mfds_product_codes` | 8,404 | 품목코드 3단 계층 (대→중→소분류) | 코드매핑 Excel |
| `mfds_test_items` | 2,940 | 시험항목 코드/명칭/단위 | 코드매핑 Excel |
| `mfds_units` | 106 | 단위코드 (mg/kg, g/100g 등) | 코드매핑 Excel |
| `mfds_item_mappings` | 가변 | BFL↔식약처 항목 매핑 | 사용자 설정 |
| `mfds_cache` | 가변 | API 응답 캐시 (24시간 TTL) | API 자동생성 |
| `mfdsTemplates` | 2,657 | 식품유형별 시험항목 템플릿 | 코드매핑 XLS |
| `testResults` | 가변 | 검사결과 데이터 (calcData 포함) | 사용자 입력 |

#### 데이터 흐름도

```
[접수등록 sampleReceipt.html]
  ├→ 식약처 품목코드 선택 (mfds_product_codes 3단 드롭다운)
  ├→ 식품유형 선택 → mfdsTemplates에서 시험항목 자동 로드
  ├→ BFL↔식약처 항목 매핑 (mfds_item_mappings)
  └→ Firestore receipts 저장 (mfdsProductCode 포함)

[검사결과 입력 testResultInput.html]
  ├→ receipts 로드 → 시료별 시험항목 렌더링
  ├→ 측정값 입력 → MFDS_RULES 자동 적용
  │   ├→ 유효자리수 (validCphr, precision별 toFixed)
  │   ├→ 정량한계 (fdqntLimit, 미만시 불검출)
  │   └→ 표기값 (markValue) 생성
  ├→ 자동판정 (적합/부적합, maxValue/minValue 기준)
  ├→ Firestore testResults 저장
  ├→ [양식] 버튼 → API 0241→0242 체인 → 시험일지 HTML 양식 표시
  └→ 식약처 전송
      ├→ Step 1: insertExprDiaryNew (0209) → exprDiarySn 발급
      └→ Step 2: saveSploreInspctResult (0216) → 결과 전송
```

### 포트 사용 현황
| 포트 | 서비스 | 비고 |
|------|--------|------|
| 8080 | Tomcat (중간모듈) | 내부 전용 |
| 8443 | nginx SSL (BFL LIMS) | 외부 접근 |
| 5001 | 시료접수 API | Flask |
| 5002 | OCR 프록시 | Flask |
| 5003 | 식약처 데이터 API | Flask |

**⛔ 사용 금지 포트**: `443, 2222, 5000, 5050, 6001, 6005, 6800, 7000, 8000, 8443, 8501, 63964`

### 식약처 통합LIMS 수령 파일 패키지 (mfds_integration/)

**수령일**: 2026-02-25
**출처**: 식약처 통합LIMS 운영팀 (정보화도움터 043-234-3100)
**목적**: 통합LIMS WEB API 연동 개발용 자료 일체
**비고**: Git 미추적 (로컬 전용, `.gitignore` 대상 아님 — 인증서 포함으로 커밋 금지)

#### 파일 목록 (2026-02-25 일괄 수령)

| # | 파일/폴더 | 설명 | 비고 |
|---|----------|------|------|
| 1 | `(먼저읽어주세요)_개발테스트절차 및 주의사항.pdf` | 개발테스트 신청양식, MAC 등록 절차 | |
| 2 | `통합LIMS_WEB_API_검사기관개발가이드_V1.1.pdf` | 핵심 개발가이드 (19p) | API 연동 필독 |
| 3 | `통합LIMS_WEB_API_검사기관개발가이드_개정이력.pdf` | 가이드 변경 이력 | |
| 4 | `통합LIMS_WEB_API_테스트시나리오.xls` | 31단계 테스트 시나리오 | ✅ 전체 통과 (2026-02-26) |
| 5 | `통합테스트시나리오_자체의뢰 일반배정 시료별 결재상신.xls` | 자체의뢰 흐름 시나리오 | |
| 6 | `검사기관별_테스트계정_20260225.xlsx` | 테스트 계정 목록 (apitest01~40) | 바이오푸드랩: **apitest34** |
| 7 | `식약처 안내 메일.txt` | MAC 등록 안내, 임시비밀번호 | |
| 8 | `O000170.jks` | 테스트 기관 인증서 (비밀번호: mfds2015) | ⚠️ 커밋 금지 |
| 9 | `O000026.jks` | 운영 기관 인증서 (바이오푸드랩) | ⚠️ 커밋 금지 |
| 10 | `Sample/` | 클라이언트 API 샘플 (Java 소스) | WebApiController, WebApiService |
| 11 | `Sample_중간모듈/` | 중간모듈 WAR (62MB) + 샘플 | LMS_CLIENT_API.war |
| 12 | `서비스별 가이드/` | 167개 API 서비스별 PDF 가이드 | I-LMS-0101 ~ I-LMS-0818 |
| 13 | `DirectApiTest.java` | 독립 API 테스트 (WAR 우회) | 2026-02-26 작성 |
| 14 | `MacTest.java` | MAC 주소 감지 테스트 | 2026-02-26 작성 |

#### 코드매핑자료 (13개 Excel, 2026-02-25 수령)

식약처가 제공하는 **식품 분야(IM36000001) 코드 레퍼런스 데이터**. 검사기관이 통합LIMS 연동 시 사용할 품목/시험항목/기준규격 등의 표준 코드 체계.

| # | 파일 | 건수 | JSON 변환 | Firestore 컬렉션 | 현재 활용 |
|---|------|------|:---------:|-----------------|----------|
| 1 | `공통코드.xlsx` | 383건 | ✅ `common_codes.json` | `mfds_common_codes` | 드롭다운 코드 |
| 2 | `품목코드.xlsx` | 8,404건 | ✅ `product_codes.json` | `mfds_product_codes` | 접수등록 품목 선택 |
| 3 | `시험항목.xlsx` | 2,940건 | ✅ `test_items.json` | `mfds_test_items` | 검사항목 매핑 |
| 4 | `단위.xlsx` | 106건 | ✅ `units.json` | `mfds_units` | 단위 선택 |
| 5 | `기준_개별기준규격.xlsx` | ~15,993건 | ❌ 미변환 | — | 미활용 |
| 6 | `기준_공통기준규격.xlsx` | ~33,739건 | ❌ 미변환 | — | 미활용 |
| 7 | `기준_공통기준규격종류.xlsx` | ~11건 | ❌ 미변환 | — | 미활용 |
| 8 | `기준_개별기준상세규격.xlsx` | — | ❌ 미변환 | — | 미활용 |
| 9 | `기준_공통기준상세규격.xlsx` | — | ❌ 미변환 | — | 미활용 |
| 10 | `기준_단서조항.xlsx` | — | ❌ 미변환 | — | 미활용 |
| 11 | `품목속성.xlsx` | — | ❌ 미변환 | — | 미활용 |
| 12 | `부서_사용자목록.xlsx` | 5부서 16명 | ❌ 미변환 | — | 미활용 (테스트용) |
| 13 | `의뢰업체담당자목록.xlsx` | — | ❌ 미변환 | — | 미활용 |

**JSON 변환 경로**: `data/mfds/*.json` (2026-02-26 변환, 커밋 `4b69594`)
**업로드 도구**: `mfdsCodeUpload.html` (브라우저에서 Firestore 배치 업로드)
