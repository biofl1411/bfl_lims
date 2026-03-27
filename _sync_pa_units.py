import firebase_admin
from firebase_admin import credentials, firestore
import json

cred = credentials.Certificate("/home/biofl/bfl_lims/serviceAccountKey.json")
app = firebase_admin.initialize_app(cred)
db = firestore.client()

with open("/tmp/pa_unit_map.json", "r") as f:
    unit_map = json.load(f)

print(f"Unit map: {len(unit_map)} items")

all_docs = list(db.collection("mfds_test_items").stream())
print(f"Total docs: {len(all_docs)}")

pa_docs = []
code_field = None
unit_field = None

for d in all_docs:
    dd = d.to_dict()
    for k, v in dd.items():
        if isinstance(v, str) and v.startswith("PA0") and len(v) == 6:
            if not code_field:
                code_field = k
                for kk in dd.keys():
                    encoded = kk.encode('utf-8')
                    if encoded == b'\xeb\x8b\xa8\xec\x9c\x84':
                        unit_field = kk
                        break
                print(f"Code field: {repr(code_field)}")
                print(f"Unit field: {repr(unit_field)}")
            pa_docs.append((d, v))
            break

print(f"PA docs: {len(pa_docs)}")

batch = db.batch()
bc = 0
updated = 0
for d, code in pa_docs:
    new_unit = unit_map.get(code, "")
    dd = d.to_dict()
    current = dd.get(unit_field, "") if unit_field else ""
    if new_unit and new_unit != current:
        update_field = unit_field if unit_field else "\ub2e8\uc704"
        batch.update(d.reference, {update_field: new_unit})
        updated += 1
        bc += 1
        if bc >= 400:
            batch.commit()
            batch = db.batch()
            bc = 0
            print(f"  committed {updated}")

if bc > 0:
    batch.commit()
print(f"Updated: {updated}")
