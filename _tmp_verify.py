import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.0.96', port=22, username='biofl', password='bphsk*1411**')
sftp = ssh.open_sftp()
with sftp.open('/tmp/verify_ppapb.py', 'w') as f:
    f.write("""import firebase_admin
from firebase_admin import credentials, firestore
cred = credentials.Certificate("serviceAccountKey.json")
app = firebase_admin.initialize_app(cred)
db = firestore.client()

# 1. mfds_test_items에서 P/PA/PB 문서 확인
all_docs = db.collection("mfds_test_items").get()
p_cnt = 0
pa_cnt = 0
pb_cnt = 0
for d in all_docs:
    did = d.id
    if did.startswith("PA"): pa_cnt += 1
    elif did.startswith("PB"): pb_cnt += 1
    elif did.startswith("P") and not did.startswith("PA") and not did.startswith("PB"): p_cnt += 1
print("=== mfds_test_items ===")
print("  P: %d, PA: %d, PB: %d" % (p_cnt, pa_cnt, pb_cnt))

# 2. refFeeMapping items에서 P/PA/PB
doc = db.collection("settings").document("refFeeMapping").get()
if doc.exists:
    items = doc.to_dict().get("items", [])
    p_items = [i for i in items if i.get("testItemCode","").startswith("P") and not i.get("testItemCode","").startswith("PA") and not i.get("testItemCode","").startswith("PB")]
    pa_items = [i for i in items if i.get("testItemCode","").startswith("PA")]
    pb_items = [i for i in items if i.get("testItemCode","").startswith("PB")]
    print("=== refFeeMapping.items ===")
    print("  P: %d, PA: %d, PB: %d, total: %d" % (len(p_items), len(pa_items), len(pb_items), len(items)))

# 3. refFeeMapping mapping에서 P/PA/PB
    mapping = doc.to_dict().get("mapping", {})
    p_map = len([k for k in mapping if k.startswith("P") and not k.startswith("PA") and not k.startswith("PB")])
    pa_map = len([k for k in mapping if k.startswith("PA")])
    pb_map = len([k for k in mapping if k.startswith("PB")])
    print("=== refFeeMapping.mapping ===")
    print("  P: %d, PA: %d, PB: %d" % (p_map, pa_map, pb_map))

# 4. subCategories에서 P/PA/PB 소분류 확인
doc2 = db.collection("settings").document("subCategories").get()
if doc2.exists:
    data = doc2.to_dict()
    print("=== subCategories ===")
    for k in sorted(data.keys()):
        if k.startswith("P"):
            print("  %s: %s" % (k, data[k]))
""")
sftp.close()
i,o,e = ssh.exec_command('cd /home/biofl/fss_collector && PYTHONIOENCODING=utf-8 python3 -X utf8 /tmp/verify_ppapb.py')
print(o.read().decode('utf-8', errors='replace'))
err = e.read().decode('utf-8', errors='replace')
if err and 'UserWarning' not in err and len(err.strip()) > 5:
    print('ERR:', err[:500])
ssh.close()
