import firebase_admin
from firebase_admin import credentials, firestore
cred = credentials.Certificate("/home/biofl/bfl_lims/serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# itemGroups Allergen 전체 필드 확인
ig_snap = db.collection("itemGroups").get()
print("=== itemGroups Allergen(ELISA) 전체 구조 ===")
for d in ig_snap:
    data = d.to_dict()
    if data.get("검사목적","") == "Allergen(ELISA)":
        print("\n  doc_id: %s" % d.id)
        for k, v in data.items():
            print("    %s: %s" % (k, v))

print("\n=== itemGroups Allergen(RT-PCR) 샘플 3건 ===")
count = 0
for d in ig_snap:
    data = d.to_dict()
    if data.get("검사목적","") == "Allergen(RT-PCR)" and count < 3:
        print("\n  doc_id: %s" % d.id)
        for k, v in data.items():
            print("    %s: %s" % (k, v))
        count += 1

# mfds_test_items에서 X30* 확인
print("\n=== mfds_test_items X30* ===")
test_snap = db.collection("mfds_test_items").get()
for d in test_snap:
    data = d.to_dict()
    code = data.get("시험항목코드","")
    if code.startswith("X300"):
        print("  %s %s %s" % (code, data.get("한글명",""), data.get("영문명","")))

# 어떤 검체유형으로 로드되는지 확인
print("\n=== itemGroups Allergen(ELISA) 검체유형 목록 ===")
types = set()
for d in ig_snap:
    data = d.to_dict()
    if data.get("검사목적","") == "Allergen(ELISA)":
        types.add(data.get("검체유형",""))
for t in sorted(types):
    print("  %s" % t)
