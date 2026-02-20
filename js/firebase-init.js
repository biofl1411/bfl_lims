/**
 * BFL LIMS - Firebase 초기화
 * Firestore, Auth, Storage 연결
 *
 * 사용법: 모든 HTML에서 Firebase SDK CDN 로드 후 이 파일을 로드
 * <script src="https://www.gstatic.com/firebasejs/10.14.1/firebase-app-compat.js"></script>
 * <script src="https://www.gstatic.com/firebasejs/10.14.1/firebase-firestore-compat.js"></script>
 * <script src="https://www.gstatic.com/firebasejs/10.14.1/firebase-auth-compat.js"></script>
 * <script src="https://www.gstatic.com/firebasejs/10.14.1/firebase-storage-compat.js"></script>
 * <script src="js/firebase-init.js"></script>
 */

const firebaseConfig = {
  apiKey: "AIzaSyDbG7L2gR9UovOYQXE0vv8nbH0_DqqXyyo",
  authDomain: "bfl-lims.firebaseapp.com",
  projectId: "bfl-lims",
  storageBucket: "bfl-lims.firebasestorage.app",
  messagingSenderId: "694014042557",
  appId: "1:694014042557:web:9162e1e324b7af024072d4",
  measurementId: "G-XKTWZLYY93"
};

// Firebase 앱 초기화 (중복 방지)
if (!firebase.apps.length) {
  firebase.initializeApp(firebaseConfig);
}

// 전역 참조
const db = firebase.firestore();
const auth = firebase.auth();
const storage = firebase.storage();

// Firebase 연결 상태
var _firebaseReady = false;
var _firebaseAuthReady = false;

/**
 * 익명 인증 → Firestore 연결 확인
 * 보안 규칙: request.auth != null → 인증된 사용자만 접근 허용
 * 사용자는 로그인 화면 없이 자동으로 익명 인증됨
 */
(function initFirebaseAuth() {
  auth.onAuthStateChanged(function(user) {
    if (user) {
      // 이미 인증됨 (익명 또는 실명)
      _firebaseAuthReady = true;
      console.log('[Firebase] 인증됨: ' + (user.isAnonymous ? '익명' : user.email) + ' (uid: ' + user.uid + ')');
      _checkFirestoreConnection();
    } else {
      // 인증 안 됨 → 익명 로그인 시도
      console.log('[Firebase] 익명 인증 시도...');
      auth.signInAnonymously().catch(function(err) {
        console.error('[Firebase] 익명 인증 실패:', err.message);
        _firebaseReady = false;
      });
    }
  });
})();

function _checkFirestoreConnection() {
  db.collection('_health').doc('ping').set({
    timestamp: firebase.firestore.FieldValue.serverTimestamp()
  }).then(function() {
    _firebaseReady = true;
    console.log('[Firebase] Firestore 연결 성공 ✅');
    // 커스텀 이벤트 발행 (다른 코드에서 대기 가능)
    window.dispatchEvent(new Event('firebase-ready'));
  }).catch(function(err) {
    _firebaseReady = false;
    console.warn('[Firebase] Firestore 연결 실패:', err.message);
  });
}

/**
 * Firebase 연결 상태 확인
 * @returns {boolean}
 */
function isFirebaseReady() {
  return _firebaseReady && _firebaseAuthReady;
}

/**
 * Firebase 준비 완료까지 대기
 * @returns {Promise<void>}
 */
function waitForFirebase() {
  return new Promise(function(resolve) {
    if (isFirebaseReady()) return resolve();
    window.addEventListener('firebase-ready', function() { resolve(); }, { once: true });
    // 10초 타임아웃
    setTimeout(function() { resolve(); }, 10000);
  });
}
