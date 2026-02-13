#!/usr/bin/env python3
"""
식약처 I1220(식품제조가공업) 전체 데이터 다운로드
사용법: python3 download_fss.py
결과: data/fss_all.json
"""
import urllib.request, json, time, os

API_KEY = 'e5a1d9f07d6c4424a757'
SERVICE = 'I1220'
PAGE_SIZE = 1000
BASE = f'https://openapi.foodsafetykorea.go.kr/api/{API_KEY}/{SERVICE}/json'

def fetch(start, end):
    url = f'{BASE}/{start}/{end}'
    resp = urllib.request.urlopen(url, timeout=30).read().decode('utf-8')
    return json.loads(resp)

# 1단계: 전체 건수 확인
print('식약처 I1220 전체 데이터 다운로드 시작...')
data = fetch(1, 1)
total = int(data[SERVICE]['total_count'])
print(f'전체: {total:,}건 (예상 {total//PAGE_SIZE + 1}회 호출)')

# 2단계: 전체 다운로드
all_rows = []
for start in range(1, total + 1, PAGE_SIZE):
    end = min(start + PAGE_SIZE - 1, total)
    try:
        data = fetch(start, end)
        rows = data[SERVICE].get('row', [])
        for r in rows:
            all_rows.append({
                'nm': r.get('BSSH_NM', ''),
                'ceo': r.get('PRSDNT_NM', ''),
                'biz': r.get('INDUTY_NM', ''),
                'lic': r.get('LCNS_NO', ''),
                'addr': r.get('LOCP_ADDR', ''),
                'org': r.get('INSTT_NM', ''),
                'tel': r.get('TELNO', ''),
                'dt': r.get('PRMS_DT', '')
            })
        print(f'  [{start:>6}-{end:>6}] {len(rows):>4}건 (누적 {len(all_rows):,}건)')
    except Exception as e:
        print(f'  [{start}-{end}] 오류: {e}')
    time.sleep(0.3)

# 3단계: 저장
os.makedirs('data', exist_ok=True)
with open('data/fss_all.json', 'w', encoding='utf-8') as f:
    json.dump(all_rows, f, ensure_ascii=False, separators=(',', ':'))

size_mb = os.path.getsize('data/fss_all.json') / 1024 / 1024
print(f'\n✅ 완료: {len(all_rows):,}건 → data/fss_all.json ({size_mb:.1f}MB)')
print('이제 git add/commit/push 하세요!')
