"""testDiary.html 수정 스크립트
- 검사목적/검사항목 드롭다운 추가
- getRecItemInfo, onRecItemChange, onRecPurposeChange 함수 추가
- calcHeavyMetal 동적 기준값 사용
- generateDiaryCn 동적 항목/목적 사용
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('testDiary.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add dropdowns before 검사자 field in heavy metal form
old_form_start = (
    '  html += \'<div id="rec-form-heavymetal" style="display:none" class="rec-form">\';\n'
    '  html += \'<div class="rec-form-row">\';\n'
    '  html += \'<div><label>\uac80\uc0ac\uc790</label><input type="text" id="rec-tester" placeholder="\uac80\uc0ac\uc790\uba85" oninput="calcHeavyMetal()"></div>\';'
)

new_form_start = (
    '  html += \'<div id="rec-form-heavymetal" style="display:none" class="rec-form">\';\n'
    '  // 검사목적/검사항목 선택\n'
    '  html += \'<div class="rec-form-row" style="grid-template-columns:1fr 1fr">\';\n'
    '  html += \'<div><label>검사목적</label>\';\n'
    '  html += \'<select id="rec-purpose" style="width:100%;padding:6px 8px;border:1px solid #cbd5e1;border-radius:6px;font-size:12px" onchange="onRecPurposeChange()">\';\n'
    '  html += \'<option value="자가품질위탁검사용">자가품질위탁검사용</option>\';\n'
    '  html += \'<option value="참고용(기준규격외)">참고용(기준규격외)</option>\';\n'
    '  html += \'<option value="참고용(영양성분)">참고용(영양성분)</option>\';\n'
    '  html += \'<option value="참고용(소비기한설정)">참고용(소비기한설정)</option>\';\n'
    '  html += \'<option value="연구용역">연구용역</option>\';\n'
    '  html += \'<option value="잔류농약(참고용)">잔류농약(참고용)</option>\';\n'
    '  html += \'</select></div>\';\n'
    '  html += \'<div><label>검사항목</label>\';\n'
    '  html += \'<select id="rec-test-item" style="width:100%;padding:6px 8px;border:1px solid #cbd5e1;border-radius:6px;font-size:12px" onchange="onRecItemChange()">\';\n'
    '  html += \'<option value="납" data-symbol="Pb" data-limit="0.3" data-method="식품공전 제8. 일반시험법 9.1.2 납">납(Pb)</option>\';\n'
    '  html += \'<option value="카드뮴" data-symbol="Cd" data-limit="0.05" data-method="식품공전 제8. 일반시험법 9.1.3 카드뮴">카드뮴(Cd)</option>\';\n'
    '  html += \'<option value="비소" data-symbol="As" data-limit="0.1" data-method="식품공전 제8. 일반시험법 9.1.4 비소">비소(As)</option>\';\n'
    '  html += \'<option value="무기비소" data-symbol="iAs" data-limit="0.2" data-method="식품공전 제8. 일반시험법 9.1.5 무기 비소">무기비소(iAs)</option>\';\n'
    '  html += \'<option value="수은" data-symbol="Hg" data-limit="0.5" data-method="식품공전 제8. 일반시험법 9.1.6 수은">수은(Hg)</option>\';\n'
    '  html += \'<option value="메틸수은" data-symbol="MeHg" data-limit="1.0" data-method="식품공전 제8. 일반시험법 9.1.9 메틸수은">메틸수은(MeHg)</option>\';\n'
    '  html += \'</select></div>\';\n'
    '  html += \'</div>\';\n'
    '  html += \'<div id="rec-item-info" style="background:#eef2ff;padding:6px 10px;border-radius:6px;font-size:11px;color:#3730a3;margin-bottom:8px">\';\n'
    '  html += \'<strong>납(Pb)</strong> | 기준: 0.3 mg/kg 이하 | 시험법: 식품공전 제8. 일반시험법 9.1.2 납</div>\';\n'
    '  html += \'<div class="rec-form-row">\';\n'
    '  html += \'<div><label>검사자</label><input type="text" id="rec-tester" placeholder="검사자명" oninput="calcHeavyMetal()"></div>\';'
)

if old_form_start in content:
    content = content.replace(old_form_start, new_form_start)
    print('1. Dropdowns added to heavy metal form')
else:
    print('ERROR: Could not find form start section')
    # Debug
    idx = content.find('rec-form-heavymetal')
    if idx >= 0:
        print(f'  Found rec-form-heavymetal at char {idx}')
        print(f'  Context: {repr(content[idx-20:idx+200])}')

# 2. Add new functions after switchRecType
def find_function_end(text, func_name):
    start = text.find('function ' + func_name)
    if start < 0:
        return -1, -1
    brace_count = 0
    i = text.index('{', start)
    while i < len(text):
        if text[i] == '{':
            brace_count += 1
        elif text[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                return start, i + 1
        i += 1
    return start, -1

s, e = find_function_end(content, 'switchRecType(')
if s < 0:
    print('ERROR: switchRecType not found')
else:
    new_functions = '''

function getRecItemInfo() {
  var sel = document.getElementById('rec-test-item');
  if (!sel) return { name: '납', symbol: 'Pb', limit: 0.3, method: '' };
  var opt = sel.options[sel.selectedIndex];
  return {
    name: opt.value,
    symbol: opt.getAttribute('data-symbol') || '',
    limit: parseFloat(opt.getAttribute('data-limit')) || 0.3,
    method: opt.getAttribute('data-method') || ''
  };
}
function onRecItemChange() {
  var info = getRecItemInfo();
  var el = document.getElementById('rec-item-info');
  if (el) el.innerHTML = '<strong>' + info.name + '(' + info.symbol + ')</strong> | 기준: ' + info.limit + ' mg/kg 이하 | 시험법: ' + info.method;
  calcHeavyMetal();
}
function onRecPurposeChange() { /* 목적 변경 시 특별 처리 없음 — generateDiaryCn에서 반영 */ }'''

    content = content[:e] + new_functions + content[e:]
    print('2. Added getRecItemInfo, onRecItemChange, onRecPurposeChange functions')

# 3. Replace calcHeavyMetal function
s, e = find_function_end(content, 'calcHeavyMetal()')
if s < 0:
    print('ERROR: calcHeavyMetal not found')
else:
    old_calc = content[s:e]
    new_calc = """function calcHeavyMetal() {
  var sampleConc = parseFloat(document.getElementById('rec-sample-conc').value) || 0;
  var blankConc = parseFloat(document.getElementById('rec-blank-conc').value) || 0;
  var finalVolume = parseFloat(document.getElementById('rec-final-volume').value) || 50;
  var dilution = parseFloat(document.getElementById('rec-dilution').value) || 1;
  var sampleWeight = parseFloat(document.getElementById('rec-sample-weight').value) || 0;
  var drinkDilution = parseFloat(document.getElementById('rec-drink-dilution').value) || 1;
  if (sampleWeight <= 0) return;

  var result = (sampleConc - blankConc) * finalVolume * dilution / sampleWeight * (1/1000) / drinkDilution;
  result = Math.max(0, result);
  var resultStr = result < 0.01 ? '0.0' : result.toFixed(2);

  document.getElementById('rec-result-value').value = resultStr;

  var preview = '(' + sampleConc + ' - ' + blankConc + ') \u00d7 ' + finalVolume + ' \u00d7 ' + dilution + ' / ' + sampleWeight + ' \u00d7 1/1000 \u00f7 ' + drinkDilution;
  var previewEl = document.getElementById('rec-formula-preview');
  if (previewEl) previewEl.textContent = preview + ' = ' + resultStr + ' mg/kg';

  // 선택된 항목의 기준값 사용
  var itemInfo = getRecItemInfo();
  var maxVal = itemInfo.limit;
  var judgmentEl = document.getElementById('rec-judgment');
  if (judgmentEl) {
    judgmentEl.value = (result <= maxVal || resultStr === '0.0') ? '적합' : '부적합';
    judgmentEl.style.color = (result <= maxVal || resultStr === '0.0') ? '#10b981' : '#ef4444';
  }
}"""
    content = content.replace(old_calc, new_calc)
    print('3. calcHeavyMetal() updated with dynamic limit')

# 4. Replace generateDiaryCn function
s, e = find_function_end(content, 'generateDiaryCn()')
if s < 0:
    print('ERROR: generateDiaryCn not found')
else:
    old_gen = content[s:e]
    new_gen = """function generateDiaryCn() {
  var recType = document.querySelector('input[name="rec-type"]:checked');
  if (!recType || recType.value !== 'heavymetal') {
    var contentEl = document.getElementById('diary-content');
    return contentEl ? contentEl.innerText : '';
  }

  var r = currentSample || {};
  var tester = (document.getElementById('rec-tester') || {}).value || '';
  var startDate = (document.getElementById('rec-start-date') || {}).value || '';
  var endDate = (document.getElementById('rec-end-date') || {}).value || '';
  var stdDate = (document.getElementById('rec-std-date') || {}).value || '';
  var sampleWeight = (document.getElementById('rec-sample-weight') || {}).value || '';
  var sampleConc = (document.getElementById('rec-sample-conc') || {}).value || '';
  var blankConc = (document.getElementById('rec-blank-conc') || {}).value || '';
  var finalVolume = (document.getElementById('rec-final-volume') || {}).value || '50';
  var dilution = (document.getElementById('rec-dilution') || {}).value || '1';
  var drinkDilution = (document.getElementById('rec-drink-dilution') || {}).value || '1';
  var resultVal = (document.getElementById('rec-result-value') || {}).value || '';
  var judgment = (document.getElementById('rec-judgment') || {}).value || '';

  var stdVals = [];
  for (var i = 0; i <= 5; i++) {
    stdVals.push((document.getElementById('rec-std' + i) || {}).value || '');
  }

  // 선택된 검사항목/검사목적 가져오기
  var itemInfo = getRecItemInfo();
  var itemName = itemInfo.name;
  var itemSymbol = itemInfo.symbol;
  var itemLimit = itemInfo.limit;
  var itemMethod = itemInfo.method;
  var purposeSel = document.getElementById('rec-purpose');
  var purpose = purposeSel ? purposeSel.value : '자가품질위탁검사용';

  var sampleName = r.sploreNm || r.prductNm || '';
  var receiptNo = r.sploreRceptNo || r.sploreReqestNo || '';

  var html = '<div style="font-family:\\'Malgun Gothic\\',sans-serif;font-size:12px;max-width:800px">';
  html += '<h2 style="text-align:center;font-size:18px;margin-bottom:20px">시 험 검 사 기 록 서</h2>';
  html += '<h3>1. 시료정보</h3>';
  html += '<table border="1" style="width:100%;border-collapse:collapse;font-size:11px">';
  html += '<tr><td style="padding:4px 8px;background:#f0f0f0">검사항목</td><td style="padding:4px 8px">' + itemName + '</td>';
  html += '<td style="padding:4px 8px;background:#f0f0f0">검체번호</td><td style="padding:4px 8px">' + receiptNo + '</td></tr>';
  html += '<tr><td style="padding:4px 8px;background:#f0f0f0">검사자</td><td style="padding:4px 8px">' + tester + '</td>';
  html += '<td style="padding:4px 8px;background:#f0f0f0">시료명</td><td style="padding:4px 8px">' + sampleName + '</td></tr>';
  html += '<tr><td style="padding:4px 8px;background:#f0f0f0">검사목적</td><td colspan="3" style="padding:4px 8px">' + purpose + '</td></tr>';
  html += '<tr><td style="padding:4px 8px;background:#f0f0f0">시험법근거</td><td colspan="3" style="padding:4px 8px">' + itemMethod + '</td></tr>';
  html += '</table>';
  html += '<h3 style="margin-top:12px">2. 검사방법 (BFL-KQI-360 중금속류(유해물질) SOP)</h3>';
  html += '<div style="background:#f9f9f9;padding:8px;border:1px solid #ddd;font-size:11px">';
  html += 'Microwave 시료분해 \u2192 ICP-MS 분석 (BFL-KQI-360)</div>';
  html += '<h3 style="margin-top:12px">3. 검사결과</h3>';
  html += '<div style="background:#f9f9f9;padding:8px;border:1px solid #ddd;font-size:11px">';
  html += itemName + ' = (' + sampleConc + ' - ' + blankConc + ') \u00d7 ' + finalVolume + ' \u00d7 ' + dilution;
  html += ' / ' + sampleWeight + ' \u00d7 1/1000 \u00f7 ' + drinkDilution + ' = <strong>' + resultVal + ' mg/kg</strong></div>';
  html += '<table border="1" style="width:100%;border-collapse:collapse;font-size:11px;margin-top:8px">';
  html += '<tr style="background:#f0f0f0"><td>STD</td><td>STD1</td><td>STD2</td><td>STD3</td><td>STD4</td><td>STD5</td></tr>';
  html += '<tr><td>' + stdVals[0] + '</td><td>' + stdVals[1] + '</td><td>' + stdVals[2] + '</td><td>' + stdVals[3] + '</td><td>' + stdVals[4] + '</td><td>' + stdVals[5] + '</td></tr></table>';
  html += '<h3 style="margin-top:12px">4. 판정</h3>';
  html += '<table border="1" style="width:100%;border-collapse:collapse;font-size:11px">';
  html += '<tr style="background:#f0f0f0"><td>분석항목</td><td>기준(mg/kg)</td><td>결과(mg/kg)</td><td>판정</td></tr>';
  html += '<tr><td>' + itemName + '</td><td>' + itemLimit + ' 이하</td><td>' + resultVal + '</td>';
  html += '<td style="color:' + (judgment==='적합'?'green':'red') + '">' + judgment + '</td></tr></table>';
  html += '<p style="margin-top:8px;font-size:10px;color:#666">BFL-KQP-08-F02 (주)바이오푸드랩</p></div>';

  return html;
}"""
    content = content.replace(old_gen, new_gen)
    print('4. generateDiaryCn() updated with dynamic item values')

with open('testDiary.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('\ntestDiary.html updated successfully!')
