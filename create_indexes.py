"""Firestore 복합 인덱스 생성 스크립트"""
import json
import google.auth
import google.auth.transport.requests
from google.oauth2 import service_account
import urllib.request
import urllib.error

SA_PATH = "/home/biofl/bfl_lims/serviceAccountKey.json"
PROJECT_ID = "bfl-lims"

# 필요한 복합 인덱스 정의
INDEXES = [
    {
        "collectionGroup": "fss_businesses",
        "fields": [
            {"fieldPath": "api_source", "order": "ASCENDING"},
            {"fieldPath": "prms_dt", "order": "DESCENDING"},
        ]
    },
    {
        "collectionGroup": "fss_products",
        "fields": [
            {"fieldPath": "api_source", "order": "ASCENDING"},
            {"fieldPath": "last_updt_dtm", "order": "DESCENDING"},
        ]
    },
    {
        "collectionGroup": "fss_materials",
        "fields": [
            {"fieldPath": "api_source", "order": "ASCENDING"},
            {"fieldPath": "chng_dt", "order": "DESCENDING"},
        ]
    },
    {
        "collectionGroup": "fss_changes",
        "fields": [
            {"fieldPath": "api_source", "order": "ASCENDING"},
            {"fieldPath": "chng_dt", "order": "DESCENDING"},
        ]
    },
]

def main():
    # 서비스 계정으로 인증
    creds = service_account.Credentials.from_service_account_file(
        SA_PATH,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    token = creds.token

    base_url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/collectionGroups"

    for idx in INDEXES:
        col = idx["collectionGroup"]
        url = f"{base_url}/{col}/indexes"
        body = {
            "queryScope": "COLLECTION",
            "fields": idx["fields"]
        }
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            method="POST"
        )
        try:
            resp = urllib.request.urlopen(req)
            result = json.loads(resp.read().decode())
            print(f"OK {col}: {idx['fields'][1]['fieldPath']} DESC - {result.get('name','created')}")
        except urllib.error.HTTPError as e:
            err_body = e.read().decode()
            if "already exists" in err_body:
                print(f"SKIP {col}: {idx['fields'][1]['fieldPath']} - already exists")
            else:
                print(f"ERR {col}: {e.code} {err_body[:200]}")

    print("\nDone! Indexes may take a few minutes to build.")

if __name__ == "__main__":
    main()
