import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.0.96', port=22, username='biofl', password='bphsk*1411**')
sftp = ssh.open_sftp()
with sftp.open('/tmp/check_papb3.py', 'w') as f:
    f.write("""import firebase_admin
from firebase_admin import credentials, firestore
cred = credentials.Certificate("serviceAccountKey.json")
app = firebase_admin.initialize_app(cred)
db = firestore.client()

# 1. refFeeMapping items
doc = db.collection("settings").document("refFeeMapping").get()
if doc.exists:
    data = doc.to_dict()
    items = data.get("items", [])
    pa = [i for i in items if str(i.get("testItemCode","")).startswith("PA")]
    pb = [i for i in items if str(i.get("testItemCode","")).startswith("PB")]
    print("refFeeMapping items: total=%d PA=%d PB=%d" % (len(items), len(pa), len(pb)))
    mapping = data.get("mapping", {})
    pa_m = len([k for k in mapping if k.startswith("PA")])
    pb_m = len([k for k in mapping if k.startswith("PB")])
    print("refFeeMapping mapping: PA=%d PB=%d" % (pa_m, pb_m))

# 2. mfds_test_items PA/PB by document ID prefix
pa_cnt = 0
pb_cnt = 0
all_docs = db.collection("mfds_test_items").get()
for d in all_docs:
    did = d.id
    if did.startswith("PA"): pa_cnt += 1
    elif did.startswith("PB"): pb_cnt += 1
print("mfds_test_items docs: PA=%d PB=%d (total=%d)" % (pa_cnt, pb_cnt, len(all_docs)))
""")
sftp.close()
i,o,e = ssh.exec_command('cd /home/biofl/fss_collector && PYTHONIOENCODING=utf-8 python3 -X utf8 /tmp/check_papb3.py')
print(o.read().decode('utf-8', errors='replace'))
err = e.read().decode('utf-8', errors='replace')
if err and 'UserWarning' not in err and len(err.strip()) > 5:
    print('ERR:', err[:500])
ssh.close()
