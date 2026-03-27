import firebase_admin
from firebase_admin import credentials, firestore
import json

cred = credentials.Certificate("/home/biofl/bfl_lims/serviceAccountKey.json")
app = firebase_admin.initialize_app(cred)
db = firestore.client()

with open("/tmp/pa_fee_map.json") as f:
    fee_map = json.load(f)
with open("/tmp/pa_unit_map.json") as f:
    unit_map = json.load(f)

# Get PA item names from mfds_test_items
all_docs = list(db.collection("mfds_test_items").stream())
pa_items = {}
for d in all_docs:
    dd = d.to_dict()
    code_val = None
    name_val = ""
    eng_val = ""
    for k, v in dd.items():
        if isinstance(v, str) and v.startswith("PA0") and len(v) == 6:
            code_val = v
        if k == "\ud55c\uae00\uba85":
            name_val = v
        if k == "\uc601\ubb38\uba85":
            eng_val = v
    if code_val:
        pa_items[code_val] = {"name": name_val, "eng": eng_val}

print(f"PA items from mfds: {len(pa_items)}")

# Load current refFeeMapping
doc_ref = db.document("settings/refFeeMapping")
doc = doc_ref.get()
data = doc.to_dict()
items = data.get("items", [])

# Remove existing PA items
items = [i for i in items if not (i.get("testItemCode", "").startswith("PA"))]
print(f"After removing PA: {len(items)}")

# Add PA items
added = 0
for code in sorted(pa_items.keys()):
    info = pa_items[code]
    items.append({
        "testItemCode": code,
        "itemName": info["name"],
        "engName": info["eng"],
        "unit": unit_map.get(code, ""),
        "fee": fee_map.get(code, 0),
        "enabled": True,
        "note": ""
    })
    added += 1

doc_ref.update({"items": items, "totalItems": len(items)})
print(f"Total: {len(items)}, PA added: {added}")
