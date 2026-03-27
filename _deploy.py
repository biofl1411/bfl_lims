import sys
sys.stdout.reconfigure(encoding='utf-8')
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.0.96', port=22, username='biofl', password='bphsk*1411**')
stdin, stdout, stderr = ssh.exec_command('cd /home/biofl/bfl_lims && git pull origin main 2>&1')
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
