/* ============================================================
   BFL LIMS 공통 토스트 시스템
   - 10초 표시
   - 여러 개일 때 계단식 (아래→위 스택)
   - 화면 하단 중앙 위치
   ============================================================ */
(function() {
    // 스타일 삽입
    var style = document.createElement('style');
    style.textContent = `
        .bfl-toast-container {
            position: fixed;
            bottom: 32px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 99999;
            display: flex;
            flex-direction: column-reverse;
            align-items: center;
            gap: 8px;
            pointer-events: none;
        }
        .bfl-toast {
            pointer-events: auto;
            padding: 12px 28px;
            border-radius: 10px;
            font-size: 14px;
            font-weight: 600;
            font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
            color: #fff;
            background: #323842;
            box-shadow: 0 6px 24px rgba(0,0,0,.25);
            opacity: 0;
            transform: translateY(20px);
            transition: opacity .3s, transform .3s;
            max-width: 600px;
            text-align: center;
            word-break: keep-all;
            line-height: 1.5;
        }
        .bfl-toast.show {
            opacity: 1;
            transform: translateY(0);
        }
        .bfl-toast.hide {
            opacity: 0;
            transform: translateY(-10px);
        }
        .bfl-toast.success { background: #2e7d32; }
        .bfl-toast.error   { background: #c62828; }
        .bfl-toast.warn    { background: #e65100; }
        .bfl-toast.info    { background: #1565c0; }
    `;
    document.head.appendChild(style);

    // 컨테이너 생성
    var container = null;
    function ensureContainer() {
        if (container && document.body.contains(container)) return container;
        container = document.createElement('div');
        container.className = 'bfl-toast-container';
        document.body.appendChild(container);
        return container;
    }

    /**
     * showToast(msg, type, duration)
     * @param {string} msg - 표시할 메시지
     * @param {string} type - 'success' | 'error' | 'warn' | 'info' (기본 'success')
     * @param {number} duration - 표시 시간 ms (기본 10000)
     */
    window.showToast = function(msg, type, duration) {
        if (!msg) return;
        // type 별칭 매핑
        if (type === 'warning') type = 'warn';
        // type 미지정 시 메시지 내용으로 자동 판별
        if (!type) {
            if (/^[❌🚫⛔]|실패|오류|에러/.test(msg)) type = 'error';
            else if (/^[⚠️🔒]|경고|주의|다릅니다|없음|불가/.test(msg)) type = 'warn';
            else if (/^[📋📢🎯ℹ️🔍]|감지|선택됨|안내|참고/.test(msg)) type = 'info';
            else type = 'success';
        }
        // 토스트 개수에 따라 기본 시간 조정 (5개 미만 10초, 이상 20초)
        if (!duration) {
            var existing = ensureContainer().querySelectorAll('.bfl-toast').length;
            duration = (existing >= 4) ? 20000 : 10000;
        }

        var c = ensureContainer();
        var t = document.createElement('div');
        t.className = 'bfl-toast ' + type;
        t.textContent = msg;
        c.appendChild(t);

        // show 애니메이션
        requestAnimationFrame(function() {
            requestAnimationFrame(function() {
                t.classList.add('show');
            });
        });

        // 자동 제거
        var timer = setTimeout(function() { removeToast(t); }, duration);

        // 클릭으로 즉시 닫기
        t.style.cursor = 'pointer';
        t.addEventListener('click', function() {
            clearTimeout(timer);
            removeToast(t);
        });
    };

    function removeToast(t) {
        t.classList.remove('show');
        t.classList.add('hide');
        setTimeout(function() {
            if (t.parentNode) t.parentNode.removeChild(t);
        }, 300);
    }
})();
