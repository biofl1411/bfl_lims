/**
 * deadline-calc.js — 처리기한 공통 계산 모듈
 * 접수 관리 > 설정 > 처리기한 및 휴일관리의 규칙을 기준으로 동작
 * Firestore settings/deadlineRule (workingDays), settings/holidays (dates[]) 사용
 */
var DeadlineCalc = (function() {
    var _holidays = null;   // ['2026-01-01', ...] 캐시
    var _workingDays = 12;  // 기본값
    var _loaded = false;

    /** Firestore에서 휴일 + 워킹데이 수 로드 */
    async function load() {
        if (_loaded) return;
        try {
            var hDoc = await db.collection('settings').doc('holidays').get();
            if (hDoc.exists && hDoc.data().dates) {
                _holidays = hDoc.data().dates;
            } else {
                _holidays = [];
            }
        } catch(e) {
            console.warn('[DeadlineCalc] 휴일 로드 실패:', e.message);
            _holidays = [];
        }
        try {
            var dDoc = await db.collection('settings').doc('deadlineRule').get();
            if (dDoc.exists && dDoc.data().workingDays) {
                _workingDays = parseInt(dDoc.data().workingDays) || 12;
            }
        } catch(e) {
            console.warn('[DeadlineCalc] 워킹데이 설정 로드 실패:', e.message);
        }
        _loaded = true;
    }

    /** 해당 날짜가 워킹데이인지 (주말 + 휴일 제외) */
    function isWorkingDay(date) {
        var day = date.getDay();
        if (day === 0 || day === 6) return false;
        var y = date.getFullYear();
        var m = ('0' + (date.getMonth() + 1)).slice(-2);
        var d = ('0' + date.getDate()).slice(-2);
        var dateStr = y + '-' + m + '-' + d;
        return (_holidays || []).indexOf(dateStr) < 0;
    }

    /** 접수일 포함 워킹데이 N일 뒤 날짜 계산 */
    function addWorkingDays(startDate, days) {
        var date = new Date(startDate);
        var added = isWorkingDay(date) ? 1 : 0;
        while (added < days) {
            date.setDate(date.getDate() + 1);
            if (isWorkingDay(date)) added++;
        }
        return date;
    }

    /** 접수일 기준 처리기한 날짜 계산 → 'YYYY-MM-DD' */
    function calcDeadline(receiptDate) {
        var dl = addWorkingDays(new Date(receiptDate), _workingDays);
        var y = dl.getFullYear();
        var m = ('0' + (dl.getMonth() + 1)).slice(-2);
        var d = ('0' + dl.getDate()).slice(-2);
        return y + '-' + m + '-' + d;
    }

    /** 오늘부터 처리기한까지 남은 워킹데이 수 (음수면 초과) */
    function remainingWorkingDays(deadlineStr) {
        if (!deadlineStr) return null;
        var today = new Date();
        today.setHours(0, 0, 0, 0);
        var deadline = new Date(deadlineStr);
        deadline.setHours(0, 0, 0, 0);

        if (today.getTime() === deadline.getTime()) return 0;

        var count = 0;
        if (today < deadline) {
            // 남은 워킹데이 (양수)
            var d = new Date(today);
            while (d < deadline) {
                d.setDate(d.getDate() + 1);
                if (isWorkingDay(d)) count++;
            }
            return count;
        } else {
            // 초과 워킹데이 (음수)
            var d = new Date(deadline);
            while (d < today) {
                d.setDate(d.getDate() + 1);
                if (isWorkingDay(d)) count++;
            }
            return -count;
        }
    }

    /**
     * D-day HTML 렌더링
     * @param {string} deadlineStr - 'YYYY-MM-DD'
     * @param {boolean} showDate - 날짜도 함께 표시할지
     * @returns {string} HTML
     */
    function renderDday(deadlineStr, showDate) {
        if (!deadlineStr) return '-';
        var days = remainingWorkingDays(deadlineStr);
        if (days === null) return '-';

        var label, color, weight;
        if (days <= 0) {
            label = 'D+' + Math.abs(days);
            color = '#e53935'; weight = '700';
        } else if (days <= 2) {
            label = 'D-' + days;
            color = '#ff9800'; weight = '700';
        } else if (days <= 5) {
            label = 'D-' + days;
            color = '#f9a825'; weight = '600';
        } else {
            label = 'D-' + days;
            color = '#999'; weight = '400';
        }

        var html = '<span style="color:' + color + ';font-weight:' + weight + '">';
        if (showDate) html += deadlineStr + '<br>';
        html += label + '</span>';
        return html;
    }

    /**
     * 처리기한 컬럼용 렌더 (날짜 + D-day)
     */
    function renderDeadlineCell(deadlineStr) {
        if (!deadlineStr) return '-';
        var days = remainingWorkingDays(deadlineStr);
        if (days === null) return deadlineStr;

        var label, color, weight;
        if (days <= 0) {
            label = 'D+' + Math.abs(days);
            color = '#e53935'; weight = '700';
        } else if (days <= 2) {
            label = 'D-' + days;
            color = '#ff9800'; weight = '700';
        } else if (days <= 5) {
            label = 'D-' + days;
            color = '#f9a825'; weight = '600';
        } else {
            label = 'D-' + days;
            color = '#999'; weight = '400';
        }

        return '<span style="color:' + color + ';font-weight:' + weight + '">' + deadlineStr + '<br>' + label + '</span>';
    }

    /** 행 배경색 결정 (D-day 기준) */
    function getRowBgByDeadline(deadlineStr) {
        if (!deadlineStr) return '';
        var days = remainingWorkingDays(deadlineStr);
        if (days === null) return '';
        if (days <= 0) return 'background-color:#fde8e8;';
        if (days <= 2) return 'background-color:#fff8f0;';
        if (days <= 5) return 'background-color:#fffde7;';
        return '';
    }

    /** 설정값 getter */
    function getWorkingDays() { return _workingDays; }
    function getHolidays() { return _holidays || []; }
    function isLoaded() { return _loaded; }

    return {
        load: load,
        isWorkingDay: isWorkingDay,
        addWorkingDays: addWorkingDays,
        calcDeadline: calcDeadline,
        remainingWorkingDays: remainingWorkingDays,
        renderDday: renderDday,
        renderDeadlineCell: renderDeadlineCell,
        getRowBgByDeadline: getRowBgByDeadline,
        getWorkingDays: getWorkingDays,
        getHolidays: getHolidays,
        isLoaded: isLoaded
    };
})();
