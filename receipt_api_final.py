# BFL LIMS - 시료접수 API 서버 (최종판)
# 실제 food_item_fee_mapping.js 데이터 활용
# 포트: 5001

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import threading
import re
import os

app = Flask(__name__)
CORS(app)

# 접수번호 동시성 처리
receipt_lock = threading.Lock()
receipt_counter = 1

# 데이터 저장
FOOD_ITEM_FEE_DATA = []

# ============================================================================
# JS 파일 파싱
# ============================================================================

def parse_js_file(filepath):
    """food_item_fee_mapping.js 파싱
    
    형식: {purpose: '...', foodType: '...', bracket: '...', item: '...', fee: 123, count: 1}
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 배열 부분 추출
        match = re.search(r'const\s+FOOD_ITEM_FEE_MAPPING\s*=\s*\[(.*?)\];', content, re.DOTALL)
        if not match:
            print("❌ Could not find FOOD_ITEM_FEE_MAPPING array")
            return []
        
        array_content = match.group(1)
        
        # 각 객체 파싱
        items = []
        # {purpose: '...', foodType: '...', ...} 패턴 찾기
        pattern = r'\{([^}]+)\}'
        
        for obj_match in re.finditer(pattern, array_content):
            obj_str = obj_match.group(1)
            
            item = {}
            
            # purpose 추출
            purpose_match = re.search(r"purpose:\s*'([^']*)'", obj_str)
            if purpose_match:
                item['purpose'] = purpose_match.group(1)
            
            # foodType 추출
            foodtype_match = re.search(r"foodType:\s*'([^']*)'", obj_str)
            if foodtype_match:
                item['foodType'] = foodtype_match.group(1)
            
            # bracket 추출
            bracket_match = re.search(r"bracket:\s*'([^']*)'", obj_str)
            if bracket_match:
                item['bracket'] = bracket_match.group(1)
            
            # item 추출
            item_match = re.search(r"item:\s*'([^']*)'", obj_str)
            if item_match:
                item['item'] = item_match.group(1)
            
            # fee 추출
            fee_match = re.search(r"fee:\s*(\d+)", obj_str)
            if fee_match:
                item['fee'] = int(fee_match.group(1))
            
            # count 추출
            count_match = re.search(r"count:\s*(\d+)", obj_str)
            if count_match:
                item['count'] = int(count_match.group(1))
            
            if 'purpose' in item and 'foodType' in item:
                items.append(item)
        
        print(f"✅ Parsed {len(items)} items from JS file")
        return items
    
    except Exception as e:
        print(f"❌ Error parsing JS file: {e}")
        return []


def load_data():
    """데이터 로드"""
    global FOOD_ITEM_FEE_DATA
    
    # 상대 경로로 JS 파일 찾기
    possible_paths = [
        '../js/food_item_fee_mapping.js',  # api/ 폴더에서 실행 시
        'js/food_item_fee_mapping.js',     # 루트에서 실행 시
        './food_item_fee_mapping.js',       # 같은 폴더
    ]
    
    for filepath in possible_paths:
        if os.path.exists(filepath):
            print(f"📁 Found data file: {filepath}")
            FOOD_ITEM_FEE_DATA = parse_js_file(filepath)
            return
    
    print("⚠️  Warning: food_item_fee_mapping.js not found!")
    print("   Tried paths:", possible_paths)
    FOOD_ITEM_FEE_DATA = []


# 서버 시작 시 데이터 로드
load_data()


# ============================================================================
# 축산 검체유형 목록 (README.md 기준)
# ============================================================================

LIVESTOCK_FOOD_TYPES = {
    '가공치즈', '소시지', '햄', '양념육', '포장육', '식용란', '치즈', 
    '발효유', '농후발효유', '건조저장육류', '분쇄가공육제품', '식육추출가공품'
}

def get_division(food_type, purpose):
    """검체유형과 검사목적으로 검사분야(식품/축산) 구분"""
    
    # 축산 관련 검사목적
    livestock_purposes = {'항생물질(참고용)', 'Allergen(ELISA)'}
    
    # 검체유형으로 판단
    if food_type in LIVESTOCK_FOOD_TYPES:
        return '축산'
    
    # 검사목적으로 판단
    if purpose in livestock_purposes:
        return '축산'
    
    # 기본값
    return '식품'


# ============================================================================
# 데이터 추출 함수
# ============================================================================

def extract_test_purposes():
    """검사목적 추출 (식품/축산 분류)"""
    purposes_dict = {'식품': set(), '축산': set()}
    
    for item in FOOD_ITEM_FEE_DATA:
        purpose = item.get('purpose', '')
        food_type = item.get('foodType', '')
        
        if not purpose:
            continue
        
        division = get_division(food_type, purpose)
        purposes_dict[division].add(purpose)
    
    # Set을 List로 변환 (정렬)
    result = {}
    for division, purposes in purposes_dict.items():
        result[division] = sorted(list(purposes))
    
    return result


def extract_food_types_by_purpose(division, purpose):
    """검사목적별 검체유형 추출"""
    food_types = set()
    
    for item in FOOD_ITEM_FEE_DATA:
        item_division = get_division(item.get('foodType', ''), item.get('purpose', ''))
        
        if item_division == division and item.get('purpose') == purpose:
            food_type = item.get('foodType', '')
            if food_type:
                food_types.add(food_type)
    
    return sorted(list(food_types))


# ============================================================================
# API 엔드포인트
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """서버 상태 확인"""
    return jsonify({
        'status': 'ok',
        'message': 'BFL LIMS Receipt API Server',
        'data_source': 'food_item_fee_mapping.js',
        'items_loaded': len(FOOD_ITEM_FEE_DATA),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/test-purposes', methods=['GET'])
def get_test_purposes():
    """검사목적 조회
    
    GET /api/test-purposes?field=식품
    """
    try:
        field = request.args.get('field', '식품')
        
        all_purposes = extract_test_purposes()
        purposes = all_purposes.get(field, [])
        
        return jsonify({
            'field': field,
            'purposes': purposes,
            'count': len(purposes),
            'source': 'food_item_fee_mapping.js'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/food-types', methods=['GET'])
def get_food_types():
    """검체유형 조회
    
    GET /api/food-types?field=식품&purpose=자가품질위탁검사용
    """
    try:
        field = request.args.get('field', '식품')
        purpose = request.args.get('purpose', '')
        
        if not purpose:
            return jsonify({'error': 'purpose parameter is required'}), 400
        
        food_types = extract_food_types_by_purpose(field, purpose)
        
        return jsonify({
            'field': field,
            'purpose': purpose,
            'food_types': food_types,
            'count': len(food_types),
            'source': 'food_item_fee_mapping.js'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/receipt-no/allocate', methods=['POST'])
def allocate_receipt_no():
    """접수번호 할당
    
    POST /api/receipt-no/allocate
    Body: {"testField": "식품", "testPurpose": "자가품질위탁검사용"}
    """
    global receipt_counter
    
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        test_field = data.get('testField')
        test_purpose = data.get('testPurpose')
        prev_receipt_no = data.get('prevReceiptNo', '')
        
        if not test_field or not test_purpose:
            return jsonify({'error': 'testField and testPurpose are required'}), 400
        
        with receipt_lock:
            today = datetime.now()
            yy = str(today.year)[2:]
            mm = str(today.month).zfill(2)
            dd = str(today.day).zfill(2)
            
            # 이전 번호에서 순번 추출
            if prev_receipt_no:
                try:
                    match = re.search(r'(\d+)-\d+$', prev_receipt_no)
                    if match:
                        prev_seq = int(match.group(1))
                        seq = str(prev_seq + 1).zfill(3)
                    else:
                        seq = str(receipt_counter).zfill(3)
                except:
                    seq = str(receipt_counter).zfill(3)
            else:
                seq = str(receipt_counter).zfill(3)
            
            receipt_no = f'{yy}{mm}{dd}{seq}-001'
            receipt_counter += 1
        
        return jsonify({
            'receiptNo': receipt_no,
            'allocatedAt': today.isoformat(),
            'testField': test_field,
            'testPurpose': test_purpose
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/companies/search', methods=['GET'])
def search_companies():
    """업체 검색 (목업)
    
    GET /api/companies/search?q=탭스
    """
    try:
        query = request.args.get('q', '').strip().lower()
        limit = int(request.args.get('limit', 10))
        
        # 목업 데이터
        companies = [
            {'id': 1, 'name': '(주)탭스인터내셔널1공장', 'businessNo': '725-85-02346', 'ceo': '배윤성', 'phone': '02-1234-5678'},
            {'id': 2, 'name': '(주)나눔공동체', 'businessNo': '119-81-63685', 'ceo': '최영남', 'phone': '02-2345-6789'},
            {'id': 3, 'name': '우리바이오 주식회사', 'businessNo': '134-81-55919', 'ceo': '엄태욱 외 1명', 'phone': '02-3456-7890'},
        ]
        
        if not query:
            return jsonify({'companies': [], 'count': 0})
        
        filtered = [c for c in companies if query in c['name'].lower()]
        filtered = filtered[:limit]
        
        return jsonify({
            'companies': filtered,
            'count': len(filtered),
            'query': query
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/items/search', methods=['GET'])
def search_items():
    """검사항목 검색
    
    GET /api/items/search?q=대장균&purpose=자가품질위탁검사용
    """
    try:
        query = request.args.get('q', '').strip().lower()
        purpose = request.args.get('purpose', '')
        food_type = request.args.get('food_type', '')
        limit = int(request.args.get('limit', 50))
        
        results = []
        
        for item in FOOD_ITEM_FEE_DATA:
            # 필터링
            if purpose and item.get('purpose') != purpose:
                continue
            if food_type and item.get('foodType') != food_type:
                continue
            
            # 검색
            item_name = item.get('item', '').lower()
            if query and query not in item_name:
                continue
            
            results.append(item)
            
            if len(results) >= limit:
                break
        
        return jsonify({
            'items': results,
            'count': len(results),
            'query': query
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# 에러 핸들러
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal Server Error'}), 500


# ============================================================================
# 메인 실행
# ============================================================================

if __name__ == '__main__':
    print('=' * 70)
    print('🧪 BFL LIMS Receipt API Server')
    print('=' * 70)
    print(f'Server URL: http://127.0.0.1:5001')
    print(f'Health Check: http://127.0.0.1:5001/api/health')
    print('-' * 70)
    print(f'Data Source: food_item_fee_mapping.js')
    print(f'Items Loaded: {len(FOOD_ITEM_FEE_DATA)}')
    print('=' * 70)
    
    if len(FOOD_ITEM_FEE_DATA) == 0:
        print('\n⚠️  WARNING: No data loaded!')
        print('   Make sure food_item_fee_mapping.js is in:')
        print('   - ../js/food_item_fee_mapping.js')
        print('   - js/food_item_fee_mapping.js')
        print('   - ./food_item_fee_mapping.js')
        print('')
    
    print('\nAPI Endpoints:')
    print('  GET  /api/health')
    print('  GET  /api/test-purposes?field={식품|축산}')
    print('  GET  /api/food-types?field={}&purpose={}')
    print('  POST /api/receipt-no/allocate')
    print('  GET  /api/companies/search?q={}')
    print('  GET  /api/items/search?q={}&purpose={}')
    print('=' * 70)
    print('\nPress Ctrl+C to stop the server\n')
    
    app.run(host='127.0.0.1', port=5001, debug=False, use_reloader=False)
