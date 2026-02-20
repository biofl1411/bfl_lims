/**
 * BFL LIMS - Firestore 헬퍼 모듈
 * 모든 HTML에서 공통으로 사용하는 Firestore CRUD 함수
 *
 * 의존성: firebase-init.js (db, auth, storage 전역 변수)
 */

// ============================================================
// 0. 업체 데이터 정규화 (companyRegForm_v2 ↔ companyMgmt 호환)
// ============================================================

/**
 * 업체 데이터를 표준 형식(companyMgmt.html 기준)으로 정규화한다.
 * companyRegForm_v2.html에서 저장된 레거시 필드명을 표준 필드명으로 매핑.
 *
 * 표준 필드: company, bizNo, repName, zipcode/addr1/addr2(flat),
 *           licenses[{licField,licBizForm,licRepName,licNo,licBizName,...}],
 *           contacts[{name,phone,email,role,salesRep,licNums}],
 *           taxName, taxPhone, taxEmail, memo, regDate, changeLog
 *
 * @param {Object} data - Firestore에서 읽은 원본 업체 데이터
 * @returns {Object} 정규화된 업체 데이터
 */
function normalizeCompany(data) {
  if (!data) return data;
  var d = Object.assign({}, data);

  // --- 기본 필드 매핑 ---
  // name → company
  if (d.name && !d.company) {
    d.company = d.name;
  }
  // businessNo → bizNo
  if (d.businessNo && !d.bizNo) {
    d.bizNo = d.businessNo;
  }
  // ceo → repName
  if (d.ceo && !d.repName) {
    d.repName = d.ceo;
  }
  // note → memo
  if (d.note !== undefined && d.memo === undefined) {
    d.memo = d.note;
  }

  // --- 주소: addresses[] → flat zipcode/addr1/addr2 ---
  if (Array.isArray(d.addresses) && d.addresses.length > 0 && !d.addr1) {
    var firstAddr = d.addresses[0];
    d.zipcode = firstAddr.zipcode || '';
    d.addr1 = firstAddr.addr1 || '';
    d.addr2 = firstAddr.addr2 || '';
  }

  // --- 인허가: 레거시 field names → 표준 lic-prefixed names ---
  if (Array.isArray(d.licenses)) {
    d.licenses = d.licenses.map(function(lic) {
      var normalized = Object.assign({}, lic);
      // field → licField
      if (lic.field !== undefined && normalized.licField === undefined) {
        normalized.licField = lic.field;
        delete normalized.field;
      }
      // bizForm → licBizForm
      if (lic.bizForm !== undefined && normalized.licBizForm === undefined) {
        normalized.licBizForm = lic.bizForm;
        delete normalized.bizForm;
      }
      // repName → licRepName (인허가 내의 repName)
      if (lic.repName !== undefined && normalized.licRepName === undefined) {
        normalized.licRepName = lic.repName;
        delete normalized.repName;
      }
      // licenseNo → licNo
      if (lic.licenseNo !== undefined && normalized.licNo === undefined) {
        normalized.licNo = lic.licenseNo;
        delete normalized.licenseNo;
      }
      // bizName → licBizName
      if (lic.bizName !== undefined && normalized.licBizName === undefined) {
        normalized.licBizName = lic.bizName;
        delete normalized.bizName;
      }
      return normalized;
    });
  }

  // --- 담당자: contacts[] 표준화 + flat contactName/contactPhone/contactEmail ---
  if (Array.isArray(d.contacts) && d.contacts.length > 0) {
    // contacts 배열의 각 항목에 role/licNums 기본값 보장
    d.contacts = d.contacts.map(function(ct) {
      return {
        name: ct.name || '',
        phone: ct.phone || '',
        email: ct.email || '',
        role: ct.role || '',
        salesRep: ct.salesRep || ct.salesTeam || '',
        licNums: ct.licNums || []
      };
    });
    // flat 필드 설정 (첫 번째 담당자 기준)
    if (!d.contactName) d.contactName = d.contacts[0].name || '';
    if (!d.contactPhone) d.contactPhone = d.contacts[0].phone || '';
    if (!d.contactEmail) d.contactEmail = d.contacts[0].email || '';
    if (!d.salesRep) d.salesRep = d.contacts[0].salesRep || '';
  }

  // --- 세금계산서: taxInfo{} → flat taxName/taxPhone/taxEmail ---
  if (d.taxInfo && typeof d.taxInfo === 'object') {
    if (!d.taxName) d.taxName = d.taxInfo.name || '';
    if (!d.taxPhone) d.taxPhone = d.taxInfo.phone || '';
    if (!d.taxEmail) d.taxEmail = d.taxInfo.email || '';
  }

  // --- 기본값 보장 ---
  if (!d.regDate) d.regDate = '';
  if (!d.changeLog) d.changeLog = [];

  return d;
}


// ============================================================
// 1. 업체 (companies) CRUD
// ============================================================

/**
 * 전체 업체 목록 조회
 * @param {Object} opts - { status, grade, orderBy, limit }
 * @returns {Promise<Array>}
 */
async function fsGetCompanies(opts) {
  opts = opts || {};
  var ref = db.collection('companies');
  if (opts.status) ref = ref.where('status', '==', opts.status);
  if (opts.grade) ref = ref.where('grade', '==', opts.grade);
  ref = ref.orderBy(opts.orderBy || 'createdAt', 'desc');
  if (opts.limit) ref = ref.limit(opts.limit);
  var snap = await ref.get();
  return snap.docs.map(function(d) { return normalizeCompany(Object.assign({ id: d.id }, d.data())); });
}

/**
 * 업체 ID로 조회
 * @param {string} id
 * @returns {Promise<Object|null>}
 */
async function fsGetCompanyById(id) {
  var doc = await db.collection('companies').doc(id).get();
  return doc.exists ? normalizeCompany(Object.assign({ id: doc.id }, doc.data())) : null;
}

/**
 * 업체 저장 (신규 or 수정)
 * @param {Object} data - 업체 데이터 (id가 있으면 수정, 없으면 신규)
 * @returns {Promise<string>} 저장된 문서 ID
 */
async function fsSaveCompany(data) {
  var now = firebase.firestore.FieldValue.serverTimestamp();
  if (data.id) {
    // 수정
    var id = data.id;
    delete data.id;
    data.updatedAt = now;
    await db.collection('companies').doc(id).update(data);
    return id;
  } else {
    // 신규
    data.createdAt = now;
    data.updatedAt = now;
    var ref = await db.collection('companies').add(data);
    return ref.id;
  }
}

/**
 * 업체 삭제
 * @param {string} id
 */
async function fsDeleteCompany(id) {
  await db.collection('companies').doc(id).delete();
}

/**
 * 업체 검색 (회사명 or 사업자번호)
 * @param {string} query
 * @param {number} limit
 * @returns {Promise<Array>}
 */
async function fsSearchCompanies(query, limit) {
  limit = limit || 20;
  if (!query || query.trim() === '') return fsGetCompanies({ limit: limit });

  var q = query.trim();
  var results = [];

  // 회사명 검색: 표준 필드(company) + 레거시 필드(name) 모두 검색
  var snap1 = await db.collection('companies')
    .where('company', '>=', q)
    .where('company', '<=', q + '\uf8ff')
    .limit(limit)
    .get();
  snap1.docs.forEach(function(d) {
    results.push(Object.assign({ id: d.id }, d.data()));
  });

  if (results.length < limit) {
    var snap1b = await db.collection('companies')
      .where('name', '>=', q)
      .where('name', '<=', q + '\uf8ff')
      .limit(limit - results.length)
      .get();
    snap1b.docs.forEach(function(d) {
      if (!results.find(function(r) { return r.id === d.id; })) {
        results.push(Object.assign({ id: d.id }, d.data()));
      }
    });
  }

  // 사업자번호 검색: 표준 필드(bizNo) + 레거시 필드(businessNo) 모두 검색
  if (results.length < limit) {
    var snap2 = await db.collection('companies')
      .where('bizNo', '>=', q)
      .where('bizNo', '<=', q + '\uf8ff')
      .limit(limit - results.length)
      .get();
    snap2.docs.forEach(function(d) {
      if (!results.find(function(r) { return r.id === d.id; })) {
        results.push(Object.assign({ id: d.id }, d.data()));
      }
    });
  }

  if (results.length < limit) {
    var snap2b = await db.collection('companies')
      .where('businessNo', '>=', q)
      .where('businessNo', '<=', q + '\uf8ff')
      .limit(limit - results.length)
      .get();
    snap2b.docs.forEach(function(d) {
      if (!results.find(function(r) { return r.id === d.id; })) {
        results.push(Object.assign({ id: d.id }, d.data()));
      }
    });
  }

  return results.map(function(r) { return normalizeCompany(r); });
}

/**
 * 사업자번호 중복 체크
 * @param {string} businessNo
 * @param {string} excludeId - 수정 시 자기 자신 제외
 * @returns {Promise<boolean>} true = 중복 있음
 */
async function fsCheckDuplicateBusinessNo(businessNo, excludeId) {
  // 표준 필드(bizNo)로 검색
  var snap = await db.collection('companies')
    .where('bizNo', '==', businessNo)
    .limit(2)
    .get();

  // 레거시 필드(businessNo)로도 검색
  var snap2 = await db.collection('companies')
    .where('businessNo', '==', businessNo)
    .limit(2)
    .get();

  // 두 결과를 합치되 중복 제거
  var allDocs = [];
  snap.docs.forEach(function(d) { allDocs.push(d); });
  snap2.docs.forEach(function(d) {
    if (!allDocs.find(function(existing) { return existing.id === d.id; })) {
      allDocs.push(d);
    }
  });

  if (allDocs.length === 0) return false;
  if (excludeId) {
    return allDocs.some(function(d) { return d.id !== excludeId; });
  }
  return true;
}

/**
 * 업체 실시간 리스너 등록
 * @param {Function} callback - (companies[]) => void
 * @returns {Function} unsubscribe 함수
 */
function fsListenCompanies(callback) {
  return db.collection('companies').orderBy('createdAt', 'desc').onSnapshot(function(snap) {
    var list = snap.docs.map(function(d) { return normalizeCompany(Object.assign({ id: d.id }, d.data())); });
    callback(list);
  });
}


// ============================================================
// 2. 접수 (receipts) CRUD
// ============================================================

/**
 * 접수 목록 조회
 */
async function fsGetReceipts(opts) {
  opts = opts || {};
  var ref = db.collection('receipts').orderBy('createdAt', 'desc');
  if (opts.limit) ref = ref.limit(opts.limit);
  var snap = await ref.get();
  return snap.docs.map(function(d) { return Object.assign({ id: d.id }, d.data()); });
}

/**
 * 접수 저장
 */
async function fsSaveReceipt(data) {
  var now = firebase.firestore.FieldValue.serverTimestamp();
  if (data.id) {
    var id = data.id;
    delete data.id;
    data.updatedAt = now;
    await db.collection('receipts').doc(id).update(data);
    return id;
  } else {
    data.createdAt = now;
    data.updatedAt = now;
    var ref = await db.collection('receipts').add(data);
    return ref.id;
  }
}

/**
 * 접수번호 할당 (Firestore 트랜잭션 — 원자적 증가)
 * @param {string} testField - '식품' or '축산'
 * @param {string} testPurpose
 * @returns {Promise<string>} 할당된 접수번호 (예: "260220FQ001-001")
 */
async function fsAllocateReceiptNo(testField, testPurpose) {
  var counterRef = db.collection('counters').doc('receiptNo');
  var receiptNo = await db.runTransaction(async function(tx) {
    var doc = await tx.get(counterRef);
    var now = new Date();
    var yy = String(now.getFullYear()).slice(-2);
    var mm = String(now.getMonth() + 1).padStart(2, '0');
    var dd = String(now.getDate()).padStart(2, '0');
    var dateStr = yy + mm + dd;
    var fieldCode = testField === '축산' ? 'LQ' : 'FQ';

    var current = 1;
    var lastDate = '';
    if (doc.exists) {
      var data = doc.data();
      lastDate = data.lastDate || '';
      current = (lastDate === dateStr) ? (data.current || 0) + 1 : 1;
    }
    var seqStr = String(current).padStart(3, '0');
    var no = dateStr + fieldCode + seqStr + '-001';
    tx.set(counterRef, { current: current, lastDate: dateStr, lastNo: no });
    return no;
  });
  return receiptNo;
}


// ============================================================
// 3. 사용자 (users)
// ============================================================

/**
 * 전체 사용자 목록
 */
async function fsGetUsers() {
  var snap = await db.collection('users').orderBy('name').get();
  return snap.docs.map(function(d) { return Object.assign({ id: d.id }, d.data()); });
}

/**
 * 사용자 저장
 */
async function fsSaveUser(data) {
  var now = firebase.firestore.FieldValue.serverTimestamp();
  if (data.id) {
    var id = data.id;
    delete data.id;
    data.updatedAt = now;
    await db.collection('users').doc(id).update(data);
    return id;
  } else {
    data.createdAt = now;
    data.updatedAt = now;
    var ref = await db.collection('users').add(data);
    return ref.id;
  }
}

/**
 * 사용자 삭제
 */
async function fsDeleteUser(id) {
  await db.collection('users').doc(id).delete();
}


// ============================================================
// 4. 설정 (settings)
// ============================================================

/**
 * 설정 조회
 * @param {string} key - 'gradeRules', 'signalRules', 'holidays', 'apiConfig'
 * @returns {Promise<Object|null>}
 */
async function fsGetSettings(key) {
  var doc = await db.collection('settings').doc(key).get();
  return doc.exists ? doc.data() : null;
}

/**
 * 설정 저장
 * @param {string} key
 * @param {Object} data
 */
async function fsSaveSettings(key, data) {
  data.updatedAt = firebase.firestore.FieldValue.serverTimestamp();
  await db.collection('settings').doc(key).set(data, { merge: true });
}


// ============================================================
// 5. 수수료 매핑 (feeMapping) — receipt_api_final.py 대체
// ============================================================

/**
 * 시험분야별 검사목적 목록
 * @param {string} field - '식품' or '축산'
 * @returns {Promise<string[]>}
 */
async function fsGetTestPurposes(field) {
  // feeMapping에서 해당 field의 고유 purpose 목록
  var snap = await db.collection('feeMapping')
    .where('field', '==', field)
    .get();
  var purposes = {};
  snap.docs.forEach(function(d) {
    var p = d.data().purpose;
    if (p) purposes[p] = true;
  });
  return Object.keys(purposes).sort();
}

/**
 * 검사목적별 식품유형 목록
 * @param {string} field
 * @param {string} purpose
 * @returns {Promise<string[]>}
 */
async function fsGetFoodTypes(field, purpose) {
  var snap = await db.collection('feeMapping')
    .where('field', '==', field)
    .where('purpose', '==', purpose)
    .get();
  var types = {};
  snap.docs.forEach(function(d) {
    var t = d.data().foodType;
    if (t) types[t] = true;
  });
  return Object.keys(types).sort();
}

/**
 * 검사항목 검색
 * @param {string} query
 * @param {Object} opts - { purpose, foodType, limit }
 * @returns {Promise<Array>}
 */
async function fsSearchFeeItems(query, opts) {
  opts = opts || {};
  var limit = opts.limit || 50;
  var ref = db.collection('feeMapping');
  if (opts.purpose) ref = ref.where('purpose', '==', opts.purpose);
  if (opts.foodType) ref = ref.where('foodType', '==', opts.foodType);
  ref = ref.limit(limit);
  var snap = await ref.get();
  var items = snap.docs.map(function(d) { return d.data(); });

  // 클라이언트 사이드 텍스트 필터링
  if (query && query.trim()) {
    var q = query.trim().toLowerCase();
    items = items.filter(function(it) {
      return (it.item && it.item.toLowerCase().includes(q)) ||
             (it.foodType && it.foodType.toLowerCase().includes(q));
    });
  }
  return items;
}


// ============================================================
// 6. 파일 업로드/다운로드 (Firebase Storage)
// ============================================================

/**
 * 파일 업로드 → Firebase Storage
 * @param {File} file - 브라우저 File 객체
 * @param {string} path - Storage 경로 (예: "companies/abc123/biz-license.jpg")
 * @param {Function} onProgress - (percent) => void
 * @returns {Promise<string>} 다운로드 URL
 */
async function fsUploadFile(file, path, onProgress) {
  var ref = storage.ref(path);
  var task = ref.put(file);

  return new Promise(function(resolve, reject) {
    task.on('state_changed',
      function(snapshot) {
        var pct = Math.round((snapshot.bytesTransferred / snapshot.totalBytes) * 100);
        if (onProgress) onProgress(pct);
      },
      function(err) { reject(err); },
      function() {
        task.snapshot.ref.getDownloadURL().then(resolve).catch(reject);
      }
    );
  });
}

/**
 * 파일 삭제
 * @param {string} path - Storage 경로
 */
async function fsDeleteFile(path) {
  try {
    await storage.ref(path).delete();
  } catch (e) {
    console.warn('[Storage] 파일 삭제 실패:', path, e.message);
  }
}

/**
 * 업체에 사업자등록증 업로드
 * @param {string} companyId
 * @param {File} file
 * @param {Function} onProgress
 * @returns {Promise<string>} 다운로드 URL
 */
async function fsUploadBizLicense(companyId, file, onProgress) {
  var ext = file.name.split('.').pop().toLowerCase();
  var path = 'companies/' + companyId + '/biz-license.' + ext;
  var url = await fsUploadFile(file, path, onProgress);

  // Firestore에 URL 저장
  await db.collection('companies').doc(companyId).update({
    'files.bizLicenseUrl': url,
    'files.bizLicensePath': path,
    updatedAt: firebase.firestore.FieldValue.serverTimestamp()
  });
  return url;
}

/**
 * 업체에 인허가서류 업로드
 * @param {string} companyId
 * @param {File} file
 * @param {Function} onProgress
 * @returns {Promise<Object>} { name, url, path, uploadedAt }
 */
async function fsUploadPermitDoc(companyId, file, onProgress) {
  var ts = Date.now();
  var ext = file.name.split('.').pop().toLowerCase();
  var safeName = file.name.replace(/[^a-zA-Z0-9가-힣._-]/g, '_');
  var path = 'companies/' + companyId + '/permits/' + ts + '_' + safeName;
  var url = await fsUploadFile(file, path, onProgress);

  var docInfo = {
    name: file.name,
    url: url,
    path: path,
    uploadedAt: new Date().toISOString()
  };

  // Firestore에 배열에 추가
  await db.collection('companies').doc(companyId).update({
    'files.permitDocs': firebase.firestore.FieldValue.arrayUnion(docInfo),
    updatedAt: firebase.firestore.FieldValue.serverTimestamp()
  });
  return docInfo;
}

/**
 * 업체의 첨부파일 목록 조회
 * @param {string} companyId
 * @returns {Promise<Object>} { bizLicenseUrl, permitDocs[] }
 */
async function fsGetCompanyFiles(companyId) {
  var doc = await db.collection('companies').doc(companyId).get();
  if (!doc.exists) return { bizLicenseUrl: null, permitDocs: [] };
  var data = doc.data();
  return {
    bizLicenseUrl: (data.files && data.files.bizLicenseUrl) || null,
    bizLicensePath: (data.files && data.files.bizLicensePath) || null,
    permitDocs: (data.files && data.files.permitDocs) || []
  };
}


// ============================================================
// 7. localStorage 마이그레이션 유틸
// ============================================================

/**
 * localStorage 데이터를 Firestore로 일괄 마이그레이션
 * (1회성 실행용)
 */
async function fsMigrateFromLocalStorage() {
  var migrated = { companies: 0, users: 0, settings: 0 };

  // 업체 데이터
  try {
    var raw = localStorage.getItem('bfl_customers');
    if (raw) {
      var customers = JSON.parse(raw);
      if (Array.isArray(customers)) {
        var batch = db.batch();
        customers.forEach(function(c) {
          var id = c.id ? String(c.id) : db.collection('companies').doc().id;
          delete c.id;
          c.createdAt = firebase.firestore.FieldValue.serverTimestamp();
          c.updatedAt = firebase.firestore.FieldValue.serverTimestamp();
          batch.set(db.collection('companies').doc(id), c);
          migrated.companies++;
        });
        await batch.commit();
      }
    }
  } catch (e) { console.error('[Migration] companies 오류:', e); }

  // 사용자 데이터
  try {
    var raw2 = localStorage.getItem('bfl_users_data');
    if (raw2) {
      var users = JSON.parse(raw2);
      if (Array.isArray(users)) {
        var batch2 = db.batch();
        users.forEach(function(u) {
          var id = u.id ? String(u.id) : db.collection('users').doc().id;
          delete u.id;
          u.createdAt = firebase.firestore.FieldValue.serverTimestamp();
          u.updatedAt = firebase.firestore.FieldValue.serverTimestamp();
          batch2.set(db.collection('users').doc(id), u);
          migrated.users++;
        });
        await batch2.commit();
      }
    }
  } catch (e) { console.error('[Migration] users 오류:', e); }

  // 설정 데이터
  try {
    var gradeRules = localStorage.getItem('bfl_grade_rules');
    if (gradeRules) {
      await fsSaveSettings('gradeRules', { rules: JSON.parse(gradeRules) });
      migrated.settings++;
    }
    var signalRules = localStorage.getItem('bfl_signal_rules');
    if (signalRules) {
      await fsSaveSettings('signalRules', { rules: JSON.parse(signalRules) });
      migrated.settings++;
    }
    var holidays = localStorage.getItem('bfl_holidays');
    if (holidays) {
      await fsSaveSettings('holidays', { dates: JSON.parse(holidays) });
      migrated.settings++;
    }
    var holidayData = localStorage.getItem('bfl_holiday_data');
    if (holidayData) {
      await fsSaveSettings('holidayData', { data: JSON.parse(holidayData) });
      migrated.settings++;
    }
  } catch (e) { console.error('[Migration] settings 오류:', e); }

  console.log('[Migration] 완료:', migrated);
  return migrated;
}
