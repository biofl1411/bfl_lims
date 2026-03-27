import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.0.96', port=22, username='biofl', password='bphsk*1411**')
sftp = ssh.open_sftp()
with sftp.open('/tmp/deep_check.py', 'w') as f:
    f.write("""import firebase_admin
from firebase_admin import credentials, firestore
cred = credentials.Certificate("serviceAccountKey.json")
app = firebase_admin.initialize_app(cred)
db = firestore.client()

print("=== 1. refFeeMapping 문서 ===")
doc = db.collection("settings").document("refFeeMapping").get()
if doc.exists:
    data = doc.to_dict()
    keys = list(data.keys())
    print("  문서 필드:", keys)
    items = data.get("items", [])
    pa_items = [i for i in items if str(i.get("testItemCode","")).startswith("PA")]
    pb_items = [i for i in items if str(i.get("testItemCode","")).startswith("PB")]
    p_items = [i for i in items if str(i.get("testItemCode","")).startswith("P") and not str(i.get("testItemCode","")).startswith("PA") and not str(i.get("testItemCode","")).startswith("PB")]
    print("  items: total=%d, P=%d, PA=%d, PB=%d" % (len(items), len(p_items), len(pa_items), len(pb_items)))
    mapping = data.get("mapping", {})
    pa_map = len([k for k in mapping if k.startswith("PA")])
    pb_map = len([k for k in mapping if k.startswith("PB")])
    p_map = len([k for k in mapping if k.startswith("P") and not k.startswith("PA") and not k.startswith("PB")])
    print("  mapping: total=%d, P=%d, PA=%d, PB=%d" % (len(mapping), p_map, pa_map, pb_map))

print()
print("=== 2. mfds_test_items 컬렉션 ===")
all_docs = db.collection("mfds_test_items").get()
p_cnt = pa_cnt = pb_cnt = other_cnt = 0
for d in all_docs:
    did = d.id
    if did.startswith("PA"): pa_cnt += 1
    elif did.startswith("PB"): pb_cnt += 1
    elif did.startswith("P"): p_cnt += 1
    else: other_cnt += 1
print("  total=%d, P=%d, PA=%d, PB=%d, other=%d" % (len(all_docs), p_cnt, pa_cnt, pb_cnt, other_cnt))
if pa_cnt > 0:
    pa_sample = [d for d in all_docs if d.id.startswith("PA")][:3]
    for d in pa_sample:
        data = d.to_dict()
        print("    %s: %s (fee=%s)" % (d.id, data.get("\\ud55c\\uae00\\uba85",""), data.get("\\uc218\\uc218\\ub8cc","")))

print()
print("=== 3. settings/subCategories ===")
doc2 = db.collection("settings").document("subCategories").get()
if doc2.exists:
    data2 = doc2.to_dict()
    pa_keys = [k for k in data2 if k.startswith("PA")]
    pb_keys = [k for k in data2 if k.startswith("PB")]
    p_keys = [k for k in data2 if k.startswith("P") and not k.startswith("PA") and not k.startswith("PB")]
    print("  P keys:", p_keys)
    print("  PA keys:", pa_keys)
    print("  PB keys:", pb_keys)

print()
print("=== 4. REF_CODE_CATEGORIES 관련 확인 ===")
# inspectionPurposes에서 PA/PB chipFilters 확인
doc3 = db.collection("settings").document("inspectionPurposes").get()
if doc3.exists:
    purposes = doc3.to_dict().get("purposes", [])
    for p in purposes:
        name = p.get("n", "")
        chips = p.get("chipFilters", [])
        if chips:
            chip_names = [c.get("label","") for c in chips if c.get("label","").startswith("P")]
            if chip_names:
                print("  %s: %s" % (name, chip_names))
""")
sftp.close()
i,o,e = ssh.exec_command('cd /home/biofl/fss_collector && PYTHONIOENCODING=utf-8 python3 -X utf8 /tmp/deep_check.py')
print(o.read().decode('utf-8', errors='replace'))
err = e.read().decode('utf-8', errors='replace')
if err and 'UserWarning' not in err and len(err.strip()) > 5:
    print('ERR:', err[:500])
ssh.close()
