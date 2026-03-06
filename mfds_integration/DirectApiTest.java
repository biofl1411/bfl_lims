import com.authSecure.AuthenticateCert;

public class DirectApiTest {
    public static void main(String[] args) {
        try {
            String keyStoreLoc = "/home/biofl/mfds_certs/O000170.jks";
            String alias = "o000170";
            String passWord = "mfds2015";
            String ethName = "enp2s0";
            String dirPath = "/home/biofl/mfds_files";

            // 5-param constructor with explicit ethName (no Spring context)
            System.out.println("=== Creating AuthenticateCert with ethName=" + ethName + " ===");
            AuthenticateCert ac = new AuthenticateCert(keyStoreLoc, alias, passWord);

            // Set ethName via reflection since 3-param constructor doesn't accept it
            java.lang.reflect.Field ethField = AuthenticateCert.class.getDeclaredField("clientEthName");
            ethField.setAccessible(true);
            ethField.set(ac, ethName);
            System.out.println("clientEthName set to: " + ethField.get(ac));

            // Test 1: REST call
            String url = "https://wslims.mfds.go.kr/webService/rest/selectListCmmnCode";
            String param = "{\"mfdsLimsId\":\"apitest01\",\"psitnInsttCode\":\"O000170\",\"classCode\":\"IM36\"}";

            System.out.println("\n=== Calling REST API ===");
            System.out.println("URL: " + url);
            System.out.println("Param: " + param);

            String result = ac.callWebApiRest(url, param, dirPath);

            System.out.println("\n=== RESULT ===");
            System.out.println(result);

        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
