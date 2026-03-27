import firebase_admin
from firebase_admin import credentials, firestore
cred = credentials.Certificate("/home/biofl/bfl_lims/serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# 1) refFeeMapping
ref_doc = db.collection("settings").document("refFeeMapping").get()
ref_map = {}
if ref_doc.exists:
    for m in ref_doc.to_dict().get("items", []):
        code = m.get("testItemCode", "")
        if code:
            ref_map[code] = m.get("fee", 0)
print("refFeeMapping: %d건" % len(ref_map))

# 2) mfdsFeeMapping
mfds_doc = db.collection("settings").document("mfdsFeeMapping").get()
mfds_map = {}
if mfds_doc.exists:
    for m in mfds_doc.to_dict().get("items", []):
        code = m.get("mfdsCode", "")
        if code:
            mfds_map[code] = m.get("fee", 0)
print("mfdsFeeMapping: %d건" % len(mfds_map))

# 3) 전체 분석
test_snap = db.collection("mfds_test_items").get()
total = 0
no_ref = 0
no_mfds = 0
no_both = 0
categories = {}
no_both_items = {}

for d in test_snap:
    data = d.to_dict()
    code = data.get("시험항목코드", "")
    name = data.get("한글명", "")
    cat = code[0] if code else "?"
    if cat not in categories:
        categories[cat] = {"total": 0, "no_ref": 0, "no_mfds": 0, "no_both": 0}
        no_both_items[cat] = []
    categories[cat]["total"] += 1
    total += 1

    has_ref = code in ref_map and ref_map[code] > 0
    has_mfds = code in mfds_map and mfds_map[code] > 0

    if not has_ref:
        no_ref += 1
        categories[cat]["no_ref"] += 1
    if not has_mfds:
        no_mfds += 1
        categories[cat]["no_mfds"] += 1
    if not has_ref and not has_mfds:
        no_both += 1
        categories[cat]["no_both"] += 1
        if len(no_both_items[cat]) < 3:
            no_both_items[cat].append("%s %s" % (code, name))

print("\n전체 시험항목: %d건" % total)
print("refFeeMapping 미매핑: %d건" % no_ref)
print("mfdsFeeMapping 미매핑: %d건" % no_mfds)
print("둘다없음: %d건" % no_both)

print("\n=== 카테고리별 현황 ===")
for cat in sorted(categories.keys()):
    c = categories[cat]
    print("  %s: 전체=%d ref없음=%d mfds없음=%d 둘다없음=%d" % (cat, c["total"], c["no_ref"], c["no_mfds"], c["no_both"]))

print("\n=== 둘다 없는 항목 샘플 ===")
for cat in sorted(no_both_items.keys()):
    for item in no_both_items[cat]:
        print("  %s" % item)

# 4) JS mfds-fee-mapping.js 파일의 항목과 비교
import json, os
js_path = "/home/biofl/bfl_lims/js/mfds-fee-mapping.js"
js_codes = set()
if os.path.exists(js_path):
    with open(js_path, "r", encoding="utf-8") as f:
        content = f.read()
    import re
    for m in re.finditer(r'mfdsCode:\s*"([^"]+)"', content):
        js_codes.add(m.group(1))
print("\nJS mfds-fee-mapping.js: %d건" % len(js_codes))

# JS에는 있지만 refFeeMapping/mfdsFeeMapping 모두에 없는 항목
js_only = js_codes - set(ref_map.keys()) - set(mfds_map.keys())
print("JS에만 있는 항목: %d건" % len(js_only))
for c in sorted(js_only)[:10]:
    print("  %s" % c)
