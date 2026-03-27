<%@page import="java.util.ResourceBundle"%>
<%@page import="java.io.FileNotFoundException"%>
<%@page import="java.io.FileInputStream"%>
<%@page import="java.io.File"%>
<%@page import="java.io.OutputStream"%>
<%@page import="java.io.InputStream"%>
<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<title>파일 다운로드</title>

<%
	request.setCharacterEncoding("UTF-8");
	
	//properties 파일 불러오기
	ResourceBundle resource = ResourceBundle.getBundle("application");

	//파일 업로드된 경로
	String savePath = resource.getString("fileDownloadPath");
	
	//서버에 실제 저장된 파일명
	String fileName = request.getParameter("fileName");
	
	//실제 내보낼 파일명
	String orgFileName = request.getParameter("fileName");
	
	InputStream in = null;
	OutputStream os = null;
	
	File file = null;
	boolean skip = false;
	String client = "";
	
	try{
				
		//파일을 읽어 스트림에 담기
		file = new File(savePath, fileName);
		in = new FileInputStream(file);
			
		client = request.getHeader("User-Agent");
		
		//파일 다운로드 헤더 지정
		response.reset();
		response.setContentType("application/octet-stream");
		response.setHeader("Content-Description", "JSP Generated Data");
		
		if(in != null){
			//IE
			if(client.indexOf("MSIE") != -1){
				response.setHeader("Content-Disposition", "attachment; filename" + new String(orgFileName.getBytes("KSC5601"), "ISO8859_1"));
			}else{
				//한글 파일명 처리
				orgFileName = new String(orgFileName.getBytes("utf-8"), "iso-8859-1");
				
				response.setHeader("Content-Disposition", "attachment; filename=\"" + orgFileName + "\"");
				response.setHeader("Content-Type", "application/octet-stream; charset=utf-8");
			}
			
			response.setHeader("Content-Length", "" + file.length());
			
			out.clear();
			out = pageContext.pushBody();
			
			
			os = response.getOutputStream();
			byte b[] = new byte[(int)file.length()];
			int leng = 0;
			
			while( (leng = in.read(b)) > 0){
				os.write(b, 0, leng);
			}
		}
		else{
			response.setContentType("text/html;charset=UTF-8");
			System.out.println("<script language='javascript'>alert('파일을 찾을 수 없습니다.'); history.back();</script>");
		}
		
		
	}catch(Exception e){
		e.printStackTrace();
	}finally{
		if (in != null){
			in.close();
		}			
		if (os != null){
			os.close();
		}
			
	}
%>
</head>
<body>

</body>
</html>