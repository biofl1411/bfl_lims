"""nginx config 업로드 스크립트 - $ 변수 보존을 위해 파일 SFTP 전송"""
import paramiko, sys, os
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.0.96', port=22, username='biofl', password='bphsk*1411**')

# 1. Upload config file via SFTP
print('1. Uploading nginx config via SFTP...')
sftp = ssh.open_sftp()
local_path = os.path.join(os.path.dirname(__file__), 'nginx_config.conf')
sftp.put(local_path, '/tmp/bfl_lims_nginx.conf')
sftp.close()
print('   Upload complete')

# 2. Verify $ variables preserved
print('2. Verifying $ variables...')
stdin, stdout, stderr = ssh.exec_command('grep -c "\\$host" /tmp/bfl_lims_nginx.conf')
count = stdout.read().decode().strip()
print(f'   $host count: {count}')

# 3. Copy to nginx dir
print('3. Copying to nginx dir...')
stdin, stdout, stderr = ssh.exec_command('echo "bphsk*1411**" | sudo -S cp /tmp/bfl_lims_nginx.conf /etc/nginx/sites-available/bfl_lims 2>&1')
stdout.channel.recv_exit_status()

# 4. Test config
print('4. Testing nginx config...')
stdin, stdout, stderr = ssh.exec_command('echo "bphsk*1411**" | sudo -S nginx -t 2>&1')
result = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print(f'   {result}{err}')

if 'test is successful' in result or 'test is successful' in err:
    # 5. Reload nginx
    print('5. Reloading nginx...')
    stdin, stdout, stderr = ssh.exec_command('echo "bphsk*1411**" | sudo -S systemctl reload nginx 2>&1')
    stdout.channel.recv_exit_status()
    print('   Reload complete')

    # 6. Test MFDS proxy
    print('6. Testing /mfds/ proxy...')
    stdin, stdout, stderr = ssh.exec_command('curl -sk https://localhost:8443/mfds/ -o /dev/null -w "%{http_code}" 2>&1')
    print(f'   HTTP status: {stdout.read().decode()}')

    # 7. Test MFDS selectUnitTest
    print('7. Testing /mfds/selectUnitTest...')
    stdin, stdout, stderr = ssh.exec_command('curl -sk -X POST https://localhost:8443/mfds/selectUnitTest -o /dev/null -w "%{http_code}" 2>&1')
    print(f'   HTTP status: {stdout.read().decode()}')
else:
    print('ERROR: nginx config test failed! Restoring backup...')
    stdin, stdout, stderr = ssh.exec_command('echo "bphsk*1411**" | sudo -S cp /etc/nginx/sites-available/bfl_lims.bak /etc/nginx/sites-available/bfl_lims 2>&1')
    stdout.channel.recv_exit_status()
    stdin, stdout, stderr = ssh.exec_command('echo "bphsk*1411**" | sudo -S systemctl reload nginx 2>&1')
    stdout.channel.recv_exit_status()
    print('   Backup restored')

ssh.close()
print('Done!')
