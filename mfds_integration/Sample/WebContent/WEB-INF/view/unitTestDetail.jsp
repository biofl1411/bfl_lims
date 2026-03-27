<%@page import="org.springframework.web.multipart.MultipartHttpServletRequest"%>
<%@page import="java.util.ResourceBundle"%>
<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>



<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

<script type="text/javascript" src="<%=request.getContextPath()%>/resources/js/jquery-3.3.1.min.js"></script>
<script type="text/javascript" src="<%=request.getContextPath()%>/resources//bootstrap-3.3.2-dist/js/bootstrap.min.js"></script>
<link rel="stylesheet" href="<%=request.getContextPath()%>/resources//bootstrap-3.3.2-dist/css/bootstrap.min.css"/>
<link rel="stylesheet" href="<%=request.getContextPath()%>/resources/css/unitTest.css"/>
<title>시스템 통합 테스트 시나리오 상세정보</title>

<%
	request.setCharacterEncoding("UTF-8");
	//jsp 에서 사용하기위해서 properties 파일 불러오기
	ResourceBundle resource = ResourceBundle.getBundle("application");
	//lims Url
	String wslimsUrl = resource.getString("wslimsUrl");

%>

<script language='javascript'>

//lims Url
var wslimsUrl = '<%=wslimsUrl%>';
var apiFileUpload = false;

$(document).ready(function(){
	init();
	
	$("#txtParameter").change(function(){
		var testParam = $("#txtParameter").val();
		testParam = testParam.replace(/\r|\n/g, " ");
		
		$("#txtParameter").val(testParam);
	});
	
});

/*화면 초기 설정*/
function init(){
	
	/*시료 첨부파일 등록, 시험항목 첨부파일 등록, 시험일지 첨부파일 등록, 유전자 변형생물체 검사결과 저장, 검사기관 수정 이면 
	     파일 업로드가 있으므로 multipart 형식으로 컨트롤러를 호출 할지 여부를 설정함
	  true = 파일업로드, false = 파일업로드 없음
	*/
	if($("#txtApiId").val() == "I-LMS-0204" || $("#txtApiId").val() == "I-LMS-0205"
			|| $("#txtApiId").val() == "I-LMS-0206" || $("#txtApiId").val() == "I-LMS-0232"){
		
		apiFileUpload = true;
		$(".i-lms-api-06").remove();
	}
	else if($("#txtApiId").val() == "I-LMS-0620"){
		apiFileUpload = true;
		$(".i-lms-api-02").remove();
	}
	else{
		$(".i-lms-api-02").remove();
		$(".i-lms-api-06").remove();
	}
	
	
	//파라미터 내용 String 으로 저장
	var txtParameter = '<%=request.getParameter("testParamtrCn")%>';

	//undefined 안뜨게하기
	if(!txtParameter || txtParameter == "undefined"){
		$("#txtParameter").val("");
	}
	else{
		$("#txtParameter").val(txtParameter.toString());
	}
	
	
}


/* 파일 추가 삭제 기능 */
function modifyFileInputForm(type){
	if(type == "add"){
		var str = "";
		
		str += "<li>";
		str += "<input type='file' name='uploadFile'>";
		str += "</li>";
		str += "<br>";
		$("#divUploadFile").append(str);
	}
	else if(type == "del"){
		var uploadFile = $("[name=uploadFile]");
		var length = uploadFile.length;
		
		$("#divUploadFile").find("li").eq(length-1).remove();
		
	}
}

/*REST, SOAP Service 실행*/
function startApiService(event){
	
	var param = "";
	var url = "";
	var type = "";
	
	//REST
	if(event == "rest"){		
		url = wslimsUrl + "/webService/rest" + $("#txtRestUrl").val();
		type = "rest";
	}
	//SOAP
	else if(event == "soap"){
		url = $("#txtSoapUrl").val();
		type = "soap";
	}
	
	param = {"url" : url, "type" : type, "param" : $("#txtParameter").val()};	
	
	/* 파일 정보가 있을때 multipart 형식으로 처리 */
	if(apiFileUpload == true){

		var input = new Array();
		
		$("#uploadForm").find("input").remove();
		
		//url 정보 input 생성
		input[0] = document.createElement("input");
		input[0].setAttribute("type", "hidden");
		input[0].setAttribute("name", "url");
		input[0].setAttribute("value", url);
		
		//type 정보 input 생성
		input[1] = document.createElement("input");
		input[1].setAttribute("type", "hidden");
		input[1].setAttribute("name", "type");
		input[1].setAttribute("value", type);
		
		//param 정보 input 생성
		input[2] = document.createElement("input");
		input[2].setAttribute("type", "hidden");
		input[2].setAttribute("name", "param");
		input[2].setAttribute("value", $("#txtParameter").val());
		
		//form 에 추가
		$("#uploadForm").append(input[0]);
		$("#uploadForm").append(input[1]);
		$("#uploadForm").append(input[2]);
		
		//form 정보를 formData 에 담기
		var formData = new FormData();
		
		formData.append("url", $("[name=url]").val());
		formData.append("type", $("[name=type]").val());
		formData.append("param", $("[name=param]").val());
			
		//업로드할 파일 개수 만큼  추가
		for(var i=0; i<$("[name=uploadFile]").length; i++){
			formData.append("uploadFile", $("[name=uploadFile]")[i].files[0]);
		}
		
		$.ajax({
			url : "/ApiClient/selectUnitTestFile",
			type : "POST",
			data : formData,
			processData : false,
			contentType : false,
			success:function(data){
				//조회 테이블 생성
				ctrateTable(data);
				
			},
			error:function(request, status,error){
				console.log("code: " + request.status + "\n" + "message: " + request.responseText + "\n" + "error: " + error);
			}
		});
	}
	else{
		$.ajax({
			url : "/ApiClient/selectUnitTest",
			type : "POST",
			dataType : "json",
			data : JSON.stringify(param),
			contentType : "application/json; charset=utf-8",
			success:function(data){				
				//조회 테이블 생성
				ctrateTable(data);			
				
			},
			error:function(request, status,error){
				console.log("code: " + request.status + "\n" + "message: " + request.responseText + "\n" + "error: " + error);
			}
		});
	}
}

/*조회 테이블 생성*/
function ctrateTable(data){
	
	var str = "";
	
	//생성된 테이블 삭제
	$("#resultData table").remove();
	$("#resultData div").remove();
	
	//panel 크기 조정
	$("#resultBody").css("height", "700px");
	$("#resultBody").css("width", "100%");	
	//테이블이 들어갈 공간 크기 조정
	$("#resultData").css("height", "650px");
	
	//Vo Header 가 있을 경우 테이블 생성
	if(data.header != null){
		var header = data.header; //헤더  저장
		var resultData = data.resultData; // 내용 저장
		var cnt = 0; //No. 생성
		
		
		str += "<table id='resultTable' class='table table-bordered' style='table-layout:fixed;'>";
		
		str += "<colgroup>";
		str += "<col style='width:50px;'>";
		$.each(header, function(index, item){
			str += "<col style='width:"+(item.length*50)+"px;'>";				
			
		});
		str += "</colgroup>";
		
		str += "<thead class='thead-dark'>";
		str += "<tr>";
		str += "<th>순번</th>";
		
		
		//header 생성
		$.each(header, function(index, item){
			str += "<th>"+item+"</th>";				
		});
		
		str += "</tr>";
		str += "</thead>";
		
		//td 내용 생성
		$.each(resultData, function(rIndex, rItem){		
			cnt ++;
			str += "<tr>";
			str += "<td>"+cnt+"</td>";
			
			$.each(header, function(hIndex, hItem){
				str += "<td>";
				
				if(!rItem[hIndex]){
					str += "";					
				}
				else{
					str += rItem[hIndex];
				}
				
				str += "</td>";
			});
			
			str += "</tr>";		
		});
		
		str += "</table>";
		
		
		
	}
	//Vo Header 가 없을 경우
	else{
		
		//결과 초기화
		$("#resultData").text("");
		
		//결과값 append
		str += "<div class='row'>";
		str += JSON.stringify(data);
		str += "</div>";
		
		//파일 다운로드 url 비교 하여 파일 다운로드 파일 생성
		var resultUrl = $("#txtRestUrl").val();
		var soapUrl = $("#txtSoapUrl").val();
		
		str += "<br/>";
		
		if(resultUrl == "/selectAtchmnflDwld" || soapUrl == "/selectAtchmnflDwldSoap" ||
				resultUrl == "/selectGrdcrtPrevew" || soapUrl == "/selectGrdcrtPrevewSoap" ||
				resultUrl == "/selectGrdcrtDmOutpt" || soapUrl == "/selectGrdcrtDmOutptSoap" ||
				resultUrl == "/selectGrdcrtPdfOutpt" || soapUrl == "/selectGrdcrtPdfOutptSoap" ||
				resultUrl == "/selectGrdcrtOutpt" || soapUrl == "/selectGrdcrtOutptSoap" ||
				resultUrl == "/selectReqestRceptRdmsPdf" || soapUrl == "/selectReqestRceptRdmsPdfSoap"){
			
			str += "<div class='row'>";
			str += "<button type='button' class='btn btn-primary' onClick='onDownLoad("+JSON.stringify(data)+")'>파일 다운로드</button>";
			str += "</div>";
			
		}
		
		
	}	

	setTimeout(function(){
		$("#resultData").append(str);		
	},200);
	
}

/* 파일 다운로드 */
function onDownLoad(resultData){	
	var fileName = resultData["resultData"][0]["fileName"];

	$(location).attr("href", "/ApiClient/unitTestFileDownLoad?fileName="+fileName+"");
}

/* 파라미터 생성 jsp로 이동*/
function createParameter(type){
	
	var data = selectParameter();
	
	/* 수정일때만 파라미터 데이터 체크 */
	if(type == "modify"){
		/* 시스템 웹서비스 항목 테이블에 관련된 파라미터 정보가 없습니다. */
		if(data.resultData.length <= 0){
			$("#checkParam").text("시스템 웹서비스 항목 테이블에 관련된 파라미터 정보가 없습니다.");
			$("#ctrateParam").modal();
			return;
		}
		
		/* 파라미터 정보가 빈값인지 체크 */		
		if(!$("#txtParameter").val()){
			$("#checkParam").text("파라미터 정보가 없습니다.");
			$("#ctrateParam").modal();
			return;
		}
		
		
		var regex = /[^0-9]/g;
		
		/* JSON 형식에 숫자만 있을때 */
		if(!regex.test($("#txtParameter").val())){	
			if($("#txtParameter").val()){
				$("#checkParam").text("파라미터 정보의 JSON 형식이 잘못 되었습니다.");
				$("#ctrateParam").modal();
				return;
			}		
		}
		
		/* JSON 형식 체크 */	
		try{
			if($("#txtParameter").val()){
				JSON.parse($("#txtParameter").val());
			}
			
		}catch(error){
			$("#checkParam").text("파라미터 정보의 JSON 형식이 잘못 되었습니다.");
			$("#ctrateParam").modal();
			return;
		}
	}
	
	//폼 생성
	var form = "<form name='createParameters' method='post' action='/ApiClient/createParameters'>";
	
	$("body").append(form);
	
	var param = new Array();
	var input = new Array();	
	
	//웹서비스 순번
	param.push(["wsrvSn", $("#wsrvSn").val()]);
	//시나리오 제목	
	param.push(["senarioSj", $("#txtTile").val()]);
	//시나리오 내용
	param.push(["senarioCn", $("#txtCn").val()]);
	//REST URL
	param.push(["rstflUrl", $("#txtRestUrl").val()]);
	//REST SOAP
	param.push(["soapMethods", $("#txtSoapUrl").val()]);
	//API 아이디
	param.push(["intrfcId", $("#txtApiId").val()]);
	//파라미터 내용
	param.push(["testParamtrCn", $("#txtParameter").val()]);
	//신규 인지 수정인지
	param.push(["type", type]);
	
	//신규이면 파라미터 값을 널로 보내고 조회하여 새로 작성
	if(type == "new"){
	
		param.push(["testParamtrCn", ""]);
	}
	else if(type = "modify"){
		
		param.push(["testParamtrCn", $("#txtParameter").val()]);
	}
	
	
	for(var i=0; i<param.length; i++){
		input[i] = document.createElement("input");
		input[i].setAttribute("type", "hidden");
		input[i].setAttribute("name", param[i][0]);
		input[i].setAttribute("value", param[i][1]);
		
		$("[name=createParameters]").append(input[i]);
		
	}
	
	$("[name=createParameters]").submit();
	
}

/* 초기화 버튼 클릭 - 결과 초기화*/
function resetResult(){
	$("#resultData table").remove();
	$("#resultData div").remove();
	
	//panel 크기 조정
	$("#resultBody").css("height", "");
	$("#resultBody").css("width", "");	
	//테이블이 들어갈 공간 크기 조정
	$("#resultData").css("height", "");
}

/* 웹서비스 순번 조회 */
function selectParameter(){
	
	var paramUrl = encodeURI(wslimsUrl + "/webService/rest/selectWsrvItem", "UTF-8");
	var unityTestSn = $("#unityTestSn option:selected").val();
	var type = "rest";
	
	var param = {"url" : paramUrl, "type" : type, "param" : {"wsrvSn" : $("#wsrvSn").val()}};
	
	var result;
	
	$.ajax({
		url : "/ApiClient/selectUnitTest",
		type : "POST",
		dataType : "json",
		async : false,
		data : JSON.stringify(param),
		contentType : "application/json; charset=utf-8",
		success:function(data){
			
			result = data;
		},
		error:function(request, status,error){
			console.log("code: " + request.status + "\n" + "message: " + request.responseText + "\n" + "error: " + error);
		}
	});
	
	return result
}
</script>

</head>
<body>
	<form id='uploadForm' name='uploadForm' method='post' action='/ApiClient/selectUnitTestFile' enctype='multipart/form-data'>
	</form>

	<!-- 웹서비스 순번 -->
	<input type="hidden" id="wsrvSn" value="<%=request.getParameter("wsrvSn")%>">
	
	<div class="container" style="width:90%;">
		<h2>시스템 통합 테스트 시나리오 상세정보</h2>
		<!-- 상세정보 panel 시작-->
		<div class="panel-group">
			<div class="panel panel-primary">
				<div class="panel-heading">상세정보</div>
				<div class="panel-body">
					<!-- 상세정보 테이블 시작 -->
					<div class="row">
						<div class="col-md-12">
							<div class="container" style="width:100%;">
							<table id="apiTable" class="table table-bordered">
								<thead>
									<tr class="tr-sm">
										<th class="thead-dark" >시나리오 제목</th>
										<td><input type="text" class="form-control input-sm" id="txtTile" value="<%=request.getParameter("senarioSj")%>" readonly></td>
									</tr>
									<tr>
										<th class="thead-dark" >시나리오 내용</th>
										<td><input type="text" class="form-control input-sm" id="txtCn" value="<%=request.getParameter("senarioCn")%>" readonly></td>
									</tr>
									<tr>
										<th class="thead-dark" >Rest URL</th>
										<td><input type="text" class="form-control input-sm" id="txtRestUrl" value="<%=request.getParameter("rstflUrl")%>" readonly></td>
									</tr>
									<tr>
										<th class="thead-dark" >Soap URL</th>
										<td><input type="text" class="form-control input-sm" id="txtSoapUrl" value="<%=request.getParameter("soapMethods")%>" readonly></td>
									</tr>
									<tr>
										<th class="thead-dark" >API 아이디</th>
										<td><input type="text" class="form-control input-sm" id="txtApiId" value="<%=request.getParameter("intrfcId")%>" readonly></td>
									</tr>
									<tr>
										<th class="thead-dark" style="line-height:120px !important;">파라미터</th>
										<td>
										 	<textarea id="txtParameter" name="txtParameter" class="form-control" rows="6" cols="50"></textarea>
										</td>
									</tr>
									<tr class="i-lms-api-02">
										<th class="thead-dark" style="line-height:150px !important;">파일첨부</th>
										<td>
											<button type="button" class="btn btn-primary" onclick="modifyFileInputForm('add')">추가</button>
											<button type="button" class="btn btn-primary" onclick="modifyFileInputForm('del')">삭제</button>
											<br>
											<br>								
											<ul id="divUploadFile">
											</ul>
										</td>
									</tr>
									<tr class="i-lms-api-06">
										<th class="thead-dark" style="line-height:150px !important;">파일첨부</th>
										<td>
											<label for="txtUploadLogo">로고</label>
											<input type="file" id="txtUploadLogo" name="uploadFile">
											<br>
											<label for="txtUploadStamp">직인</label>
											<input type="file" id="txtUploadStamp" name="uploadFile">
											<br>
											<label for="txtUploadStampEng">영문 직인</label>
											<input type="file" id="txtUploadStampEng" name="uploadFile">
										</td>
									</tr>
								</thead>
							</table>
							</div>
						</div>
					</div>
					<!-- 상세정보 테이블 종료 -->
					<!-- 상세정보 버튼 시작 -->
					<div class="row">
						<center>
						<div class="btn-group">
							<button type="button" class="btn btn-primary" onclick="startApiService('rest')">REST</button>
							<button type="button" class="btn btn-primary" onclick="startApiService('soap')">SOAP</button>
							
							<div class="btn-group">
								<button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown">
									파라미터 만들기<span class="caret"></span></button>								
								<ul class="dropdown-menu" role="menu">
									<li onclick="createParameter('new')"><a href="#">신규</a></li>
									<li onclick="createParameter('modify')"><a href="#">수정</a></li>									
								</ul>
							</div>
						</div>
						</center>
					</div>
					<br/>
					<br/>
					<br/>
					<br/>
				</div>
			</div>
		</div>
		<!-- 상세정보 panel 종료-->
		
		<!-- 결과 panel 시작-->
		<div class="panel-group">
			<div class="panel panel-primary">
				<div class="panel-heading">결과  <button type="button" class="btn btn-default" onclick="resetResult()">초기화</button></div>
				<div id="resultBody" class="panel-body">
					<div class="row">
						<div class='col-md-12' style="overflow:auto;">
							<div id="resultData" class="container">
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
		<!-- 결과 panel 종료-->
	</div>

	<!-- 파라미터 만들기 시작 -->
	<div class="modal fade" id="ctrateParam" role="dialog">
		<div class="modal-dialog">
			<div class="modal-content">
				<div class="modal-header">
					<button type="button" class="close" data-dismiss="modal">&times;</button>
					<h4 class="mdal-title">파라미터 만들기</h4>
				</div>
				<div class="modal-body">
					<p id="checkParam"><!-- 메시지  --></p>
				</div>
				<div class="modal-footer">
					<button type="button" class="btn btn-default" data-dismiss="modal">확인</button>
				</div>
			</div>
		</div>
	</div>
	<!-- 파라미터 만들기 종료-->
</body>
</html>