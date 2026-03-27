import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.0.96', port=22, username='biofl', password='bphsk*1411**')
sftp = ssh.open_sftp()
with sftp.open('/tmp/fix_deleted.py', 'w') as f:
    f.write("""import firebase_admin
from firebase_admin import credentials, firestore
cred = credentials.Certificate("serviceAccountKey.json")
app = firebase_admin.initialize_app(cred)
db = firestore.client()

doc = db.collection("settings").document("refFeeMapping").get()
if doc.exists:
    data = doc.to_dict()
    deleted = data.get("deletedCategories", [])
    print("current deletedCategories:", deleted)
    if deleted:
        db.collection("settings").document("refFeeMapping").update({"deletedCategories": []})
        print("cleared!")
    else:
        print("already empty")
""")
sftp.close()
i,o,e = ssh.exec_command('cd /home/biofl/fss_collector && PYTHONIOENCODING=utf-8 python3 -X utf8 /tmp/fix_deleted.py')
print(o.read().decode('utf-8', errors='replace'))
ssh.close()
