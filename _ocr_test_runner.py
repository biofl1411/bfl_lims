import json, base64, sys
sys.stdout.reconfigure(encoding="utf-8")
from pdf2image import convert_from_path
from io import BytesIO
import requests

images = convert_from_path("/tmp/_ocr_test.pdf", dpi=200)
buf = BytesIO()
images[0].save(buf, format="JPEG", quality=90)
img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

payload = {"images": [{"format": "jpeg", "name": "test.jpg", "data": img_b64}]}
resp = requests.post("http://localhost:5002/api/ocr/inspection-form", json=payload, timeout=120)
result = resp.json()
raw = result.pop("_ocrRawText", "")
print("=== OCR RAW ===")
print(raw[:1500])
print("=== RESULT ===")
print(json.dumps(result, ensure_ascii=False, indent=2))
