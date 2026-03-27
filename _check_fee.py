import firebase_admin
from firebase_admin import credentials, firestore
cred = credentials.Certificate("/home/biofl/bfl_lims/serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# 1) mfdsTemplates에서 X30012 확인
tmpl_snap = db.collection("mfdsTemplates").get()
print("=== mfdsTemplates X30012 ===")
for d in tmpl_snap:
    data = d.to_dict()
    for ti in data.get("testItems", []):
        if ti.get("testItemCode") == "X30012":
            print("  doc=%s name=%s fee=%s" % (d.id, data.get("templateName",""), ti.get("fee",0)))

# 2) mfdsFeeMapping에서 X300* 확인
doc = db.collection("settings").document("mfdsFeeMapping").get()
print("\n=== mfdsFeeMapping X300* ===")
if doc.exists:
    for m in doc.to_dict().get("items", []):
        if m.get("mfdsCode","").startswith("X300"):
            print("  %s %s fee=%s" % (m["mfdsCode"], m.get("itemName",""), m.get("fee",0)))

# 3) Allergen 관련 템플릿 전체
print("\n=== Allergen 관련 템플릿 (X30 코드 포함) ===")
for d in tmpl_snap:
    data = d.to_dict()
    name = data.get("templateName","") or data.get("foodTypeName","") or d.id
    items = data.get("testItems", [])
    codes = [ti.get("testItemCode","") for ti in items]
    has_x30 = any(c.startswith("X30") for c in codes if c)
    if has_x30:
        print("\n  [%s] %s" % (d.id, name))
        for ti in items:
            print("    %s %s fee=%s" % (ti.get("testItemCode",""), ti.get("testItemName",""), ti.get("fee",0)))

# 4) itemGroups에서 X30* 확인
ig_snap = db.collection("itemGroups").get()
print("\n=== itemGroups X30* ===")
x30_ig = []
for d in ig_snap:
    data = d.to_dict()
    code = data.get("testItemCode","") or data.get("시험항목코드","")
    if code and code.startswith("X30"):
        x30_ig.append((code, data.get("항목명",""), data.get("항목수수료",0), data.get("검사목적",""), data.get("검체유형","")))
if x30_ig:
    for x in x30_ig:
        print("  %s %s fee=%s 목적=%s 유형=%s" % x)
else:
    print("  없음")

# 5) 어떤 경로로 시험항목이 로드되는지 확인 - Allergen(ELISA) 검사목적 확인
print("\n=== _currentItemSource 결정 로직 확인 ===")
print("  itemGroups 전체 건수: %d" % len(list(ig_snap)))
allergen_ig = [d.to_dict() for d in ig_snap if d.to_dict().get("검사목적","") in ["Allergen(ELISA)", "Allergen(RT-PCR)"]]
print("  itemGroups Allergen 건수: %d" % len(allergen_ig))
if allergen_ig:
    for a in allergen_ig[:5]:
        print("    %s %s fee=%s 유형=%s" % (a.get("testItemCode","") or a.get("시험항목코드",""), a.get("항목명",""), a.get("항목수수료",0), a.get("검체유형","")))
