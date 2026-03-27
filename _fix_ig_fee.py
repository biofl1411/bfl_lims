import firebase_admin
from firebase_admin import credentials, firestore
cred = credentials.Certificate("/home/biofl/bfl_lims/serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# mfds_test_items에서 항목명 → 코드 + 수수료 맵 구축
test_snap = db.collection("mfds_test_items").get()
name_to_code = {}
for d in test_snap:
    data = d.to_dict()
    code = data.get("시험항목코드", "")
    kor = data.get("한글명", "")
    if code and kor:
        name_to_code[kor] = code

# mfdsFeeMapping에서 코드 → 수수료 맵
fee_doc = db.collection("settings").document("mfdsFeeMapping").get()
code_to_fee = {}
if fee_doc.exists:
    for m in fee_doc.to_dict().get("items", []):
        code_to_fee[m.get("mfdsCode", "")] = m.get("fee", 0)

print("name_to_code: %d건" % len(name_to_code))
print("code_to_fee: %d건" % len(code_to_fee))

# itemGroups 전체 업데이트: 항목명으로 testItemCode 매칭 → 수수료 설정
ig_snap = db.collection("itemGroups").get()
batch = db.batch()
updated = 0
batch_count = 0

for d in ig_snap:
    data = d.to_dict()
    item_name = data.get("항목명", "")
    existing_code = data.get("testItemCode", "") or data.get("시험항목코드", "")
    existing_fee = data.get("항목수수료", 0)

    # 이미 코드+수수료 있으면 스킵
    if existing_code and existing_fee and existing_fee > 0:
        continue

    # 항목명으로 코드 매칭
    matched_code = existing_code
    if not matched_code and item_name:
        matched_code = name_to_code.get(item_name, "")

    if not matched_code:
        continue

    # 수수료 조회
    fee = existing_fee if existing_fee and existing_fee > 0 else code_to_fee.get(matched_code, 0)

    update_data = {}
    if not existing_code and matched_code:
        update_data["testItemCode"] = matched_code
    if (not existing_fee or existing_fee == 0) and fee > 0:
        update_data["항목수수료"] = fee

    if update_data:
        batch.update(d.reference, update_data)
        updated += 1
        batch_count += 1
        if batch_count >= 450:
            batch.commit()
            batch = db.batch()
            batch_count = 0
            print("  배치 커밋... %d건" % updated)

if batch_count > 0:
    batch.commit()

print("업데이트 완료: %d건" % updated)

# 확인
ig_snap2 = db.collection("itemGroups").get()
no_fee = 0
no_code = 0
for d in ig_snap2:
    data = d.to_dict()
    if not data.get("testItemCode") and not data.get("시험항목코드"):
        no_code += 1
    if not data.get("항목수수료") or data.get("항목수수료") == 0:
        no_fee += 1

print("잔여 코드없음: %d건" % no_code)
print("잔여 수수료없음: %d건" % no_fee)
