import firebase_admin, json, sys
sys.stdout.reconfigure(encoding="utf-8")
from firebase_admin import credentials, firestore
cred = credentials.Certificate("/home/biofl/bfl_lims/serviceAccountKey.json")
app = firebase_admin.initialize_app(cred)
db = firestore.client()
docs = list(db.collection("formTemplates").stream())
for doc in docs:
    d = doc.to_dict()
    print("=== All top-level fields ===")
    for k in sorted(d.keys()):
        if k == "analyzed":
            continue
        val = json.dumps(d[k], ensure_ascii=False, default=str)
        print("  %s: %s" % (k, val[:300]))
    print("\n=== analyzed fields ===")
    if "analyzed" in d and isinstance(d["analyzed"], dict):
        a = d["analyzed"]
        for k in sorted(a.keys()):
            if k == "sections":
                for sec in a[k]:
                    for f in sec.get("fields", []):
                        fid = f.get("id", "")
                        flabel = f.get("label", "")
                        if "sample" in fid.lower() or "food" in fid.lower() or "type" in flabel.lower():
                            print("  section[%s] -> %s" % (sec["title"], json.dumps(f, ensure_ascii=False)))
            else:
                val = json.dumps(a[k], ensure_ascii=False, default=str)
                print("  %s: %s" % (k, val[:300]))
