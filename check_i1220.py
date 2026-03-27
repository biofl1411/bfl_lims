import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("/home/biofl/bfl_lims/serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# I1220 prms_dt 내림차순 상위 10건 조회
print("=== I1220 prms_dt order_by DESC 시도 ===")
try:
    q = db.collection("fss_businesses").where("api_source", "==", "I1220").order_by("prms_dt", direction=firestore.Query.DESCENDING).limit(10)
    docs = q.get()
    count = 0
    for d in docs:
        data = d.to_dict()
        print(f"  {data.get('lcns_no','?'):15} {data.get('bssh_nm','?'):25} prms_dt={data.get('prms_dt','')}")
        count += 1
    if count == 0:
        print("  결과 없음")
    print(f"  --- {count}건 ---")
except Exception as e:
    print(f"  order_by 실패: {e}")

print()
print("=== prms_dt >= 20251001 필터 ===")
try:
    q2 = db.collection("fss_businesses").where("api_source", "==", "I1220").where("prms_dt", ">=", "20251001").limit(20)
    docs2 = q2.get()
    count = 0
    for d in docs2:
        data = d.to_dict()
        print(f"  {data.get('lcns_no','?'):15} {data.get('bssh_nm','?'):25} prms_dt={data.get('prms_dt','')}")
        count += 1
    if count == 0:
        print("  2025-10-01 이후 데이터 없음")
    print(f"  --- {count}건 ---")
except Exception as e2:
    print(f"  필터 실패: {e2}")
