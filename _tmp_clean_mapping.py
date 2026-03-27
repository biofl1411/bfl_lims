import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.0.96', port=22, username='biofl', password='bphsk*1411**')
sftp = ssh.open_sftp()
with sftp.open('/tmp/clean_mapping.py', 'w') as f:
    f.write("""import firebase_admin
from firebase_admin import credentials, firestore
cred = credentials.Certificate("serviceAccountKey.json")
app = firebase_admin.initialize_app(cred)
db = firestore.client()

doc = db.collection("settings").document("refFeeMapping").get()
if doc.exists:
    mapping = doc.to_dict().get("mapping", {})
    pa_keys = [k for k in mapping if k.startswith("PA")]
    pb_keys = [k for k in mapping if k.startswith("PB")]
    for k in pa_keys + pb_keys:
        del mapping[k]
    db.collection("settings").document("refFeeMapping").update({"mapping": mapping})
    print("mapping PA %d + PB %d = %d removed" % (len(pa_keys), len(pb_keys), len(pa_keys)+len(pb_keys)))

    # 검증
    doc2 = db.collection("settings").document("refFeeMapping").get()
    m2 = doc2.to_dict().get("mapping", {})
    pa2 = len([k for k in m2 if k.startswith("PA")])
    pb2 = len([k for k in m2 if k.startswith("PB")])
    print("verify: PA=%d PB=%d" % (pa2, pb2))
""")
sftp.close()
i,o,e = ssh.exec_command('cd /home/biofl/fss_collector && PYTHONIOENCODING=utf-8 python3 -X utf8 /tmp/clean_mapping.py')
print(o.read().decode('utf-8', errors='replace'))
err = e.read().decode('utf-8', errors='replace')
if err and 'UserWarning' not in err and len(err.strip()) > 5:
    print('ERR:', err[:500])
ssh.close()
