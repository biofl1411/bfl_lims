import firebase_admin, json, sys
sys.stdout.reconfigure(encoding="utf-8")
from firebase_admin import credentials, firestore

cred = credentials.Certificate("/home/biofl/bfl_lims/serviceAccountKey.json")
app = firebase_admin.initialize_app(cred)
db = firestore.client()

doc = db.collection("settings").document("inspectionPurposes").get()
if not doc.exists:
    print("inspectionPurposes 문서 없음")
    sys.exit(1)

data = doc.to_dict()
purposes = data.get("purposes", [])
cleaned = 0

for p in purposes:
    if not p.get("fieldUse") and ("fieldCodes" in p or "fieldMode" in p):
        name = p.get("n", "?")
        old_codes = p.get("fieldCodes", {})
        old_mode = p.get("fieldMode", "")
        if "fieldCodes" in p:
            del p["fieldCodes"]
        if "fieldMode" in p:
            del p["fieldMode"]
        cleaned += 1
        print("정리: %s — fieldCodes=%s, fieldMode=%s 삭제" % (name, json.dumps(old_codes, ensure_ascii=False), old_mode))

if cleaned > 0:
    db.collection("settings").document("inspectionPurposes").update({"purposes": purposes})
    print("\n%d건 정리 완료, Firestore 저장됨" % cleaned)
else:
    print("정리할 잔존 데이터 없음")
