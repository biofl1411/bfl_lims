/**
 * 소분류 수수료 규칙 공통 모듈
 * - Firestore settings/subChipFees에서 규칙 로드
 * - 소분류별 수수료 계산 (묶음/항목 모드, 다단계 규칙)
 * - 시험항목 배열에 규칙 기반 수수료 매핑
 *
 * 사용처: 접수 등록, 접수 현황
 */

var SUB_CHIP_FEE = (function() {
    var _fees = null;

    /** Firestore에서 소분류 수수료 규칙 로드 */
    async function load() {
        try {
            var doc = await db.collection('settings').doc('subChipFees').get();
            if (doc.exists) {
                var data = doc.data() || {};
                Object.keys(data).forEach(function(k) {
                    if (typeof data[k] === 'number') {
                        data[k] = { mode: 'bundle', rules: [{ items: 0, fee: data[k], maxAdd: 0 }] };
                    }
                });
                _fees = data;
            } else {
                _fees = {};
            }
        } catch(e) { _fees = {}; }
        return _fees;
    }

    /** 현재 로드된 규칙 반환 */
    function getFees() { return _fees || {}; }

    /** 시험항목코드에서 소분류 키 추출 (X20003 → 'X2') */
    function getKey(testItemCode) {
        if (!testItemCode || testItemCode.length < 2) return '';
        var code = testItemCode.toUpperCase();
        if (code.startsWith('PA') || code.startsWith('PB')) return '';
        return code.charAt(0) + code.charAt(1);
    }

    /** 소분류 규칙으로 총 수수료 계산 */
    function calc(subKey, itemCount) {
        if (!_fees || !_fees[subKey]) return null;
        var data = _fees[subKey];
        var rules = data.rules || [];
        if (rules.length === 0) return null;
        var r1 = rules[0];
        if (!r1 || r1.fee <= 0) return null;

        if (data.mode === 'item') return r1.fee * itemCount;

        var total = r1.fee;
        var baseItems = r1.items || itemCount;
        var remaining = Math.max(0, itemCount - baseItems);
        for (var i = 1; i < rules.length && remaining > 0; i++) {
            var rule = rules[i];
            var maxAdd = rule.maxAdd || Infinity;
            var apply = Math.min(remaining, maxAdd);
            total += apply * (rule.fee || 0);
            remaining -= apply;
        }
        return total;
    }

    /** 소분류 규칙의 최대 허용 항목 수 */
    function maxItems(subKey) {
        if (!_fees || !_fees[subKey]) return Infinity;
        var data = _fees[subKey];
        var rules = data.rules || [];
        if (rules.length === 0 || !rules[0] || rules[0].fee <= 0) return Infinity;
        if (data.mode === 'item') return Infinity;
        var max = rules[0].items || 0;
        for (var i = 1; i < rules.length; i++) max += rules[i].maxAdd || 0;
        return max || Infinity;
    }

    /**
     * 소분류별 항목 순서에 따른 개별 수수료 배열 생성
     * @returns {{ fees: number[], maxItems: number }} 규칙 순서별 수수료 + 최대 항목 수
     */
    function buildItemFees(subKey, itemCount) {
        if (!_fees || !_fees[subKey]) return null;
        var data = _fees[subKey];
        var rules = data.rules || [];
        if (rules.length === 0 || !rules[0] || rules[0].fee <= 0) return null;
        var fees = [];
        if (data.mode === 'item') {
            for (var n = 0; n < itemCount; n++) fees.push(rules[0].fee || 0);
        } else {
            var r1 = rules[0];
            var baseItems = r1.items || itemCount;
            for (var n = 0; n < Math.min(baseItems, itemCount); n++) {
                fees.push(n === 0 ? (r1.fee || 0) : 0);
            }
            var remaining = Math.max(0, itemCount - baseItems);
            for (var i = 1; i < rules.length && remaining > 0; i++) {
                var rule = rules[i];
                var maxAdd = rule.maxAdd || Infinity;
                var apply = Math.min(remaining, maxAdd);
                for (var n = 0; n < apply; n++) fees.push(rule.fee || 0);
                remaining -= apply;
            }
        }
        var mi = maxItems(subKey);
        return { fees: fees, maxItems: mi };
    }

    /**
     * 시험항목 배열에 규칙 기반 수수료 매핑 (접수 현황용)
     * 각 항목에 _displayFee, _feeOver 속성 추가
     * @param {Array} items - testItemCode 필드가 있는 항목 배열
     */
    function applyToItems(items) {
        if (!_fees || !Object.keys(_fees).length) return;
        var counts = {};
        items.forEach(function(it) {
            var sk = getKey(it.testItemCode || '');
            if (sk && _fees[sk]) counts[sk] = (counts[sk] || 0) + 1;
        });
        var feeArrays = {};
        Object.keys(counts).forEach(function(sk) {
            var info = buildItemFees(sk, counts[sk]);
            if (info) feeArrays[sk] = info;
        });
        var idxMap = {};
        items.forEach(function(it) {
            var sk = getKey(it.testItemCode || '');
            if (!sk || !feeArrays[sk]) return;
            var si = idxMap[sk] = (idxMap[sk] || 0);
            idxMap[sk]++;
            var info = feeArrays[sk];
            if (si < info.fees.length) {
                it._displayFee = info.fees[si];
            } else {
                it._displayFee = 0;
                it._feeOver = true;
            }
        });
    }

    return {
        load: load,
        getFees: getFees,
        getKey: getKey,
        calc: calc,
        maxItems: maxItems,
        buildItemFees: buildItemFees,
        applyToItems: applyToItems
    };
})();
