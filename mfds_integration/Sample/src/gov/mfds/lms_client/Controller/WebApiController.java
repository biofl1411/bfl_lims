package gov.mfds.lms_client.Controller;

import java.util.HashMap;
import java.util.ResourceBundle;
import javax.servlet.http.HttpServletRequest;
import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.util.EntityUtils;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.springframework.context.ApplicationContext;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.context.ContextLoader;
import org.springframework.web.multipart.MultipartHttpServletRequest;
import com.authSecure.AuthenticateCert;


@Controller
public class WebApiController {
	
	private ApplicationContext context = ContextLoader.getCurrentWebApplicationContext();
	
	final private static ResourceBundle resource = ResourceBundle.getBundle("application");	
	
	//인증에 사용되는 jks 파일 경로
	private String keyStoreLoc = resource.getString("keyStore.keyStoreLoc");
	
	//인증에 사용되는 구분자
	private String alias = resource.getString("keyStore.keyAlias");
	
	//인증에 사용되는 키
	private String passWord = resource.getString("KeyStore.keyPassWord");
	
	//파일을 저장할 서버의 경로
	private String localStorage = resource.getString("fileDownloadPath");
	
	//해당 기관의 URL
	private String wslimsUrl = resource.getString("wslimsUrl");
	
	AuthenticateCert ac = new AuthenticateCert(keyStoreLoc, alias, passWord, context);
	
	/**
	 * 통합 LIMS WEB API 테스트 호출
	 * @param model
	 * @return
	 */
	@RequestMapping(value = "/", method = {RequestMethod.GET, RequestMethod.POST})
	public String unitTest(Model model){
		return "unitTest";
	}
	
	/**
	 * 시나리오 상세정보 화면으로 이동
	 * @param model
	 * @return
	 */
	@RequestMapping(value = "/unitTestDetail", method = {RequestMethod.GET, RequestMethod.POST})
	public String unitTestDetail(Model model){
		return "unitTestDetail";
	}
	
	/**
	 * 파라미터 만들기 화면으로 이동
	 * @param model
	 * @return
	 */
	@RequestMapping(value = "/createParameters", method = {RequestMethod.GET, RequestMethod.POST})
	public String createParameters(Model model, HttpServletRequest request){
		return "createParameters";
	}
	
	/**
	 * 파일 다운로드 호출
	 * @param model
	 * @return
	 */
	@RequestMapping(value = "/unitTestFileDownLoad", method = {RequestMethod.GET, RequestMethod.POST})
	public String unitTestFileDownLoad(Model model){
		return "unitTestFileDownLoad";
	}
	
	/**
	 * 공통 Rest 호출
	 * @param url
	 * @param param
	 * @return
	 */
	public String callWebApiRest(String url, String param){
		return ac.callWebApiRest(url, param, localStorage);
	}

	/**
	 * 공통 Soap 호출
	 * @param url
	 * @param param
	 * @return
	 */
	public String callWebApiSoap(String url, String param){
		return ac.callWebApiSoap(url, param, localStorage);
	}
	
	/**
	 * Rest, Soap 호출을 위한 함수
	 * @param param
	 * @return
	 */	
    @RequestMapping(value = "/selectUnitTest", method = {RequestMethod.GET, RequestMethod.POST})
	public @ResponseBody String selectUnitTest(@RequestBody String param){
    	
		String result = "";
		String map = "";
		
		try{
			JSONParser parser = new JSONParser();
			JSONObject jsonResult = (JSONObject)parser.parse(param);
			
			map = String.valueOf(jsonResult.get("param"));
			
			//Rest 호출
			if(String.valueOf(jsonResult.get("type")).equals("rest")){
				result = callWebApiRest(String.valueOf(jsonResult.get("url")), map);
			}
			//Soap 호출
			else if(String.valueOf(jsonResult.get("type")).equals("soap")){
				result = callWebApiSoap(String.valueOf(jsonResult.get("url")), map);
			}
			
		}catch(Exception e){
			e.printStackTrace();
		}
		
		return result;
		
	}
    
    /**
     * 파일 첨부가 있을 경우 MultipartHttpServletRequest 형식으로 REST, SOAP 호출
     * @param request
     * @return
     */
    @RequestMapping(value = "/selectUnitTestFile", method = RequestMethod.POST, produces = "application/text;charset=utf8")
	public @ResponseBody String selectUnitTest(MultipartHttpServletRequest request){
    	
		String result = "";
		
		try{			
			//Rest 호출
			if(String.valueOf(request.getParameter("type")).equals("rest")){
				result = ac.callWebApiRest(request);
			}
			//Soap 호출
			else if(String.valueOf(request.getParameter("type")).equals("soap")){
				result = ac.callWebApiSoap(request);
			}
			
		}catch(Exception e){
			e.printStackTrace();
		}
		
		return result;
		
	}
	
    /**
     * 통합테스트 목록 조회
     * @param param
     * @return
     */
	@RequestMapping(value = "/unitTestInit", method = {RequestMethod.GET, RequestMethod.POST})
	public @ResponseBody String unitTestInit(@RequestBody HashMap<String, String> param){
		
		try { 
			
			String result = "";
			//2. X509 Certificate Setting
			HttpClient httpClient = ac.setAuthHttpClient();
			
			//3. Host Url Setting
			String listUri = param.get("url");
			HttpGet httpGet = new HttpGet(listUri);
			httpGet.addHeader("accept","application/json");
			
			//4. Execute
			HttpResponse response = httpClient.execute(httpGet);
			HttpEntity httpEntity = response.getEntity();
			
			result = EntityUtils.toString(httpEntity,"UTF-8");			
			
			return result;
			
		} catch (Exception e) {
			e.printStackTrace();
			return e.getMessage();
		}		
	}

    
}
