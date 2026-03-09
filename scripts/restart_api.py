"""api_server.py 재시작 스크립트"""
import paramiko, sys, time
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.0.96', port=22, username='biofl', password='bphsk*1411**')

# 1. 기존 api_server 프로세스 종료
print('1. 기존 프로세스 종료...')
stdin, stdout, stderr = ssh.exec_command('pkill -f "python api_server.py" || true')
stdout.channel.recv_exit_status()
time.sleep(1)

# 2. 재시작 (bash -c 사용하여 nohup이 blocking 안 되게)
print('2. api_server.py 재시작...')
transport = ssh.get_transport()
channel = transport.open_session()
channel.exec_command('bash -c "cd /home/biofl/bfl_lims && nohup /home/biofl/bfl_lims/venv/bin/python api_server.py > /tmp/bfl-lims-api.log 2>&1 & disown"')
channel.recv_exit_status()
time.sleep(3)

# 3. 확인
print('3. 프로세스 확인...')
stdin, stdout, stderr = ssh.exec_command('ps aux | grep "python api_server" | grep -v grep')
out = stdout.read().decode('utf-8', errors='replace')
print(out if out.strip() else '(프로세스 없음 - 로그 확인 필요)')

# 4. 포트 확인
stdin, stdout, stderr = ssh.exec_command('ss -tlnp | grep 5003')
out5 = stdout.read().decode('utf-8', errors='replace')
print('포트 5003:', out5.strip() if out5.strip() else '(미사용)')

# 5. health check
stdin, stdout, stderr = ssh.exec_command('curl -s --connect-timeout 3 http://localhost:5003/api/health')
health = stdout.read().decode('utf-8', errors='replace')
print('health:', health if health.strip() else '(응답 없음)')

# 6. 로그 확인
stdin, stdout, stderr = ssh.exec_command('tail -5 /tmp/bfl-lims-api.log 2>/dev/null')
print('로그:', stdout.read().decode('utf-8', errors='replace'))

ssh.close()
print('완료')
