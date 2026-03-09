/**
 * 엑셀 업로드 → Firestore reagents 컬렉션
 * SheetJS(XLSX) 라이브러리 사용
 * 컬럼 매핑: A=사용처, B=구분, E=코드, F=제품명, H=규격, I=CatNo, J=CasNo, K=제조사, L=단가, M=유통기한, N=구매처
 */
async function handleExcelUpload(input) {
  var file = input.files[0];
  if (!file) return;

  if (typeof db === 'undefined' || !db) {
    showToast('Firebase가 아직 연결되지 않았습니다', 'warning');
    input.value = '';
    return;
  }

  showToast('엑셀 파일 읽는 중...', 'info', 3000);

  try {
    var data = await file.arrayBuffer();
    var wb = XLSX.read(data, { type: 'array' });

    // 시트 선택: '2026년' 포함 시트 또는 첫 번째 시트
    var sheetName = wb.SheetNames.find(function(n) { return n.indexOf('2026') >= 0; });
    if (!sheetName) sheetName = wb.SheetNames[0];
    var ws = wb.Sheets[sheetName];

    var range = XLSX.utils.decode_range(ws['!ref']);
    var reagents = [];

    for (var r = 4; r <= range.e.r; r++) {
      var cellStr = function(col) {
        var addr = XLSX.utils.encode_cell({ r: r, c: col });
        var c = ws[addr];
        return c ? String(c.v || '').trim() : '';
      };
      var cellNum = function(col) {
        var addr = XLSX.utils.encode_cell({ r: r, c: col });
        var c = ws[addr];
        if (!c || c.v == null) return 0;
        if (typeof c.v === 'number') return Math.round(c.v);
        var s = String(c.v).trim().replace(/,/g, '');
        if (!s || s === '-' || s.charAt(0) === '=') return 0;
        var n = parseFloat(s);
        return isNaN(n) ? 0 : Math.round(n);
      };

      var code = cellStr(4);
      if (!code) continue;

      reagents.push({
        code: code,
        dept: cellStr(0),
        cat: cellStr(1),
        name: cellStr(5),
        spec: cellStr(7),
        catNo: cellStr(8),
        casNo: cellStr(9),
        mfr: cellStr(10),
        unitPrice: cellNum(11),
        expiryRef: cellStr(12),
        supplier: cellStr(13),
        stockQty: 0,
        minQty: 1,
        barcodeVal: 'BFL-' + code,
        createdAt: firebase.firestore.FieldValue.serverTimestamp(),
        updatedAt: firebase.firestore.FieldValue.serverTimestamp()
      });
    }

    if (reagents.length === 0) {
      showToast('업로드할 데이터가 없습니다', 'warning');
      input.value = '';
      return;
    }

    // 기존 데이터 존재 여부 확인
    var existingSnap = await db.collection('reagents').limit(1).get();
    if (!existingSnap.empty) {
      var msg = '기존 reagents 데이터가 존재합니다.\n';
      msg += '기존 데이터를 모두 삭제하고 새로 업로드할까요?\n\n';
      msg += '[확인] = 기존 삭제 후 새 업로드\n';
      msg += '[취소] = 기존 데이터에 추가';
      var doOverwrite = confirm(msg);

      if (doOverwrite) {
        showToast('기존 데이터 삭제 중...', 'info', 5000);
        var allDocs = await db.collection('reagents').get();
        var delBatch = db.batch();
        var delCount = 0;
        for (var d = 0; d < allDocs.docs.length; d++) {
          delBatch.delete(allDocs.docs[d].ref);
          delCount++;
          if (delCount % 500 === 0) {
            await delBatch.commit();
            delBatch = db.batch();
          }
        }
        if (delCount % 500 !== 0) await delBatch.commit();
        showToast('기존 ' + allDocs.size + '건 삭제 완료', 'success', 2000);
      }
    }

    // Firestore 배치 업로드
    showToast(reagents.length + '건 업로드 시작...', 'info', 10000);
    var BATCH_SIZE = 500;
    var batch = db.batch();
    var batchCount = 0;
    var uploaded = 0;

    for (var i = 0; i < reagents.length; i++) {
      var ref = db.collection('reagents').doc();
      batch.set(ref, reagents[i]);
      batchCount++;

      if (batchCount >= BATCH_SIZE || i === reagents.length - 1) {
        await batch.commit();
        uploaded += batchCount;
        var pct = Math.round(uploaded * 100 / reagents.length);
        showToast('업로드 중... ' + uploaded + '/' + reagents.length + ' (' + pct + '%)', 'info', 5000);
        batch = db.batch();
        batchCount = 0;
      }
    }

    showToast(reagents.length + '건 업로드 완료!', 'success', 5000);

    // 데이터 새로 로드
    await loadReagents();
    updateKPI();

  } catch(err) {
    console.error('엑셀 업로드 실패:', err);
    showToast('엑셀 업로드 실패: ' + err.message, 'warning', 5000);
  }

  input.value = '';
}
