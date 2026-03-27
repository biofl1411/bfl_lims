import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.0.96', port=22, username='biofl', password='bphsk*1411**')
sftp = ssh.open_sftp()
with sftp.open('/tmp/vv.py', 'w') as f:
    f.write("""import firebase_admin
from firebase_admin import credentials, firestore
cred = credentials.Certificate("serviceAccountKey.json")
app = firebase_admin.initialize_app(cred)
db = firestore.client()

# 1. mfds_test_items PA/PB
all_docs = db.collection("mfds_test_items").get()
pa = [d for d in all_docs if d.id.startswith("PA")]
pb = [d for d in all_docs if d.id.startswith("PB")]
print("mfds_test_items: PA=%d PB=%d" % (len(pa), len(pb)))

# 2. refFeeMapping items PA/PB
doc = db.collection("settings").document("refFeeMapping").get()
if doc.exists:
    items = doc.to_dict().get("items", [])
    pa_i = [i for i in items if str(i.get("testItemCode","")).startswith("PA")]
    pb_i = [i for i in items if str(i.get("testItemCode","")).startswith("PB")]
    print("refFeeMapping.items: PA=%d PB=%d total=%d" % (len(pa_i), len(pb_i), len(items)))
""")
sftp.close()
i,o,e = ssh.exec_command('cd /home/biofl/fss_collector && PYTHONIOENCODING=utf-8 python3 -X utf8 /tmp/vv.py')
print(o.read().decode('utf-8', errors='replace'))
ssh.close()
