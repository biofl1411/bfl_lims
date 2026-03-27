import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.0.96', port=22, username='biofl', password='bphsk*1411**')
sftp = ssh.open_sftp()
with sftp.open('/tmp/cleanup_papb.py', 'w') as f:
    f.write("""import firebase_admin
from firebase_admin import credentials, firestore
cred = credentials.Certificate("serviceAccountKey.json")
app = firebase_admin.initialize_app(cred)
db = firestore.client()

# 1. refFeeMapping.mapping에서 PA/PB 제거
doc = db.collection("settings").document("refFeeMapping").get()
if doc.exists:
    data = doc.to_dict()
    mapping = data.get("mapping", {})
    pa_keys = [k for k in mapping if k.startswith("PA")]
    pb_keys = [k for k in mapping if k.startswith("PB")]
    for k in pa_keys + pb_keys:
        del mapping[k]
    db.collection("settings").document("refFeeMapping").update({"mapping": mapping})
    print("refFeeMapping.mapping: PA %d + PB %d = %d keys removed" % (len(pa_keys), len(pb_keys), len(pa_keys)+len(pb_keys)))

# 2. mfds_test_items에서 PA/PB 문서 삭제
all_docs = db.collection("mfds_test_items").get()
pa_docs = [d for d in all_docs if d.id.startswith("PA")]
pb_docs = [d for d in all_docs if d.id.startswith("PB")]
print("mfds_test_items PA=%d PB=%d to delete" % (len(pa_docs), len(pb_docs)))

batch = db.batch()
cnt = 0
for d in pa_docs + pb_docs:
    batch.delete(db.collection("mfds_test_items").document(d.id))
    cnt += 1
    if cnt % 400 == 0:
        batch.commit()
        batch = db.batch()
        print("  committed %d..." % cnt)
if cnt % 400 != 0:
    batch.commit()
print("mfds_test_items: %d documents deleted" % cnt)
""")
sftp.close()
i,o,e = ssh.exec_command('cd /home/biofl/fss_collector && PYTHONIOENCODING=utf-8 python3 -X utf8 /tmp/cleanup_papb.py')
print(o.read().decode('utf-8', errors='replace'))
err = e.read().decode('utf-8', errors='replace')
if err and 'UserWarning' not in err and len(err.strip()) > 5:
    print('ERR:', err[:500])
ssh.close()
