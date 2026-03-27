package gov.mfds.lms_client;


import java.net.URLDecoder;
import java.util.ResourceBundle;
import javax.ws.rs.Consumes;
import javax.ws.rs.POST;
import javax.ws.rs.Path;

import javax.ws.rs.Produces;
import javax.ws.rs.core.MediaType;
import org.slf4j.LoggerFactory;
import org.springframework.context.ApplicationContext;
import org.springframework.stereotype.Component;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.context.ContextLoader;
import com.authSecure.AuthenticateCert;

@Component
public class WebApiService {

private ApplicationContext context = ContextLoader.getCurrentWebApplicationContext();
	
	final private static ResourceBundle resource = ResourceBundle.getBundle("application");	
	
	//인증에 사용되는 jks 파일 경로
	private String keyStoreLoc = resource.getString("keyStore.keyStoreLoc");
	
	//인증에 사용되는 구분자
	private String alias = resource.getString("keyStore.keyAlias");
	
	//인증에 사용되는 키
	private String passWord = resource.getString("KeyStore.keyPassWord");	
	
	AuthenticateCert ac = new AuthenticateCert(keyStoreLoc, alias, passWord, context);
    
    static org.slf4j.Logger logger = LoggerFactory.getLogger(WebApiService.class);

    /**
     * DEAMON 양방향 통신 테스트
     * @param jsonParam
     * @return
     */
    @POST
    @Path("/daemonUpdateTest")
    @Consumes(MediaType.APPLICATION_JSON)
	@Produces(MediaType.APPLICATION_JSON)
	public String daemonUpdateTest(@RequestParam("param") String jsonParam){
		
		try{
			String param = URLDecoder.decode(jsonParam,"UTF-8");
			System.out.println("Success::"+param);
			return "Y";
		}catch(Exception e){
			return "N";
		}
		
	}



	
	
	

	
	
	
	
}
