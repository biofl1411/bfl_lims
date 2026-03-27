import sys, os
sys.stdout.reconfigure(encoding='utf-8')
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.0.96', port=22, username='biofl', password='bphsk*1411**')

sftp = ssh.open_sftp()
sftp.put(r'C:\Users\user\Desktop\bfl_lims\_merge_pa_server.py', '/tmp/merge_pa2.py')
sftp.close()

stdin, stdout, stderr = ssh.exec_command('python3 /tmp/merge_pa2.py 2>&1')
r = stdout.read().decode('utf-8', errors='replace')
print(r)
ssh.close()
