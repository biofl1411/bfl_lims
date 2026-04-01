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
var storage = (typeof firebase.storage === 'function') ? firebase.storage() : null;

// Firebase 연결 상태
var _firebaseReady = false;
var _firebaseAuthReady = false;

// 현재 로그인한 사용자 (전역 참조)
var _currentUser = null;

/**
 * 인증 가드 — 비로그인 시 login.html로 리디렉션
 * login.html, companyRegForm_v2.html은 공개 페이지이므로 제외
 */
(function initFirebaseAuth() {
  var _currentFile = (location.pathname.split('/').pop() || 'index.html').toLowerCase();
  var _publicPages = ['login.html', 'companyregform_v2.html'];
  var _isPublic = _publicPages.indexOf(_currentFile) !== -1;

  auth.onAuthStateChanged(function(user) {
    if (user && !user.isAnonymous) {
      // 정상 로그인됨
      _currentUser = user;
      _firebaseAuthReady = true;
      console.log('[Firebase] 로그인: ' + user.email + ' (uid: ' + user.uid + ')');
      _checkFirestoreConnection();
    } else {
      // 로그인 안 됨 (또는 익명 사용자)
      _currentUser = null;
      if (!_isPublic) {
        // 현재 페이지를 redirect 파라미터로 넘겨 로그인 후 복귀
        var redirect = encodeURIComponent(location.pathname.split('/').pop() + location.search + location.hash);
        window.location.replace('login.html?redirect=' + redirect);
      }
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
