<%@page import="java.util.ResourceBundle"%>
<%@page import="org.json.simple.parser.JSONParser"%>

<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>

<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

<script type="text/javascript" src="<%=request.getContextPath()%>/resources/js/jquery-3.3.1.min.js"></script>
<script type="text/javascript" src="<%=request.getContextPath()%>/resources/bootstrap-3.3.2-dist/js/bootstrap.min.js"></script>
<link rel="stylesheet" href="<%=request.getContextPath()%>/resources/bootstrap-3.3.2-dist/css/bootstrap.min.css"/>
<link rel="stylesheet" href="<%=request.getContextPath()%>/resources/css/unitTest.css"/>


<title>WEB API TEST</title>

<%
	
	//jsp 에서 사용하기위해서 properties 파일 불러오기
	ResourceBundle resource = ResourceBundle.getBundle("application");
	//lims Url
	String wslimsUrl = resource.getString("wslimsUrl");
	
%>
<script language='javascript'>

//lims Url
var wslimsUrl = '<%=wslimsUrl%>';


$(document).ready(function(){
	
	/*통합테스트 목록 조회*/
	init();
	
	//통합테스트 목록 변경 이벤트
	$("#unityTestSn").change(function(){
		$("#unityNm").text($("#unityTestSn option:selected").text());
	});
	
	//검색 버튼 클릭 이벤트
	$("#btnSearch").click(function(){
				
		var paramUrl = encodeURI(wslimsUrl + "/webService/rest/selectUnityTestSenario", "UTF-8");
		var unityTestSn = $("#unityTestSn option:selected").val();
		var type = "rest";
		
		var param = {"url" : paramUrl, "type" : type, "param" : {"unityTestSn" : unityTestSn}};
		
		$.ajax({
			url : "/ApiClient/selectUnitTest",
			type : "POST",
			dataType : "json",
			data : JSON.stringify(param),
			contentType : "application/json; charset=utf-8",
			success:function(data){
				
				//테이블 생성
				ctrateTable(data);
			},
			error:function(request, status,error){
				console.log("code: " + request.status + "\n" + "message: " + request.responseText + "\n" + "error: " + error);
			}
		});
		
	});
});

/*화면 초기 설정*/
function init(){
	//Rest url
	var param = {
			"url" : wslimsUrl + "/webService/rest/selectUnityTest"
	}
	
	/*통합테스트 목록 조회*/
	$.ajax({
		url : "/ApiClient/unitTestInit",
		type : "POST",
		dataType:"json",
		data : JSON.stringify(param),
		contentType : "application/json; charset=utf-8",
		success:function(data){
			
			var str = "";
			//통합 테스트 목록 조회후 select box 추가
			for(var i=0; i<data.resultData.length; i++){
				//처음 option을 선택하게 한다
				if(i == 0){
					str += "<option selected value='"+data.resultData[i].unityTestSn+"'>"+data.resultData[i].unityTestSj+"</option>";
				}
				else{
					str += "<option  value='"+data.resultData[i].unityTestSn+"'>"+data.resultData[i].unityTestSj+"</option>";
				}
				
			}
			
			$("#unityTestSn").append(str);
			
			//select box 생성 후 선택된 값 통합 테스트 에 적용 
			$("#unityNm").text($("#unityTestSn option:selected").text());
		},
		error:function(request, status,error){
			console.log("code: " + request.status + "\n" + "message: " + request.responseText + "\n" + "error: " + error);
		}
	});
}

/*unitTestDetail.jsp 호출*/
function startPopupDetail(event){
	//Pop에 값을 전달하기 위해 form 생성
	var form = document.createElement("form");
	form.setAttribute("method",      "post");
	form.setAttribute("action", 	 "/ApiClient/unitTestDetail");
	form.setAttribute("target", 	 "popup_id");
	form.setAttribute("name",   	 "unitTestDetail");
		
	$("body").append(form);
	
	var str = "";
	var tdArry = new Array();
	
	//클릭한 해당 테이블의 tr id를 가져옴
	var tr = $("#"+event.id).closest("tr");
	//클릭한 tr의 자식 td 를 가져옴
	var td = tr.children();
	
	//tdArry 변수에 td text 내용을 담기
	td.each(function(i){
		tdArry.push(td.eq(i).text());
	});
	
	//td 내용을 각각 변수에 담기
	for(var i=0; i<tdArry.length; i++){
		switch(i){
			case 1 : //시나리오 순번
				senarioSn = tdArry[i];
				break;
				
			case 2 : //시나리오 제목
				senarioSj = tdArry[i];
				break;
				
			case 3 : //시나리오 내용
				senarioCn = tdArry[i];
				break;
				
			case 4 : //API 아이디
				intrfcId = tdArry[i];
				break;
				
			case 5 : //API 명
				wsrvNm = tdArry[i];
				break;			
			
			case 6 : //파라미터 내용
				testParamtrCn = tdArry[i];
				break;
				
			case 7 : //Rest Url
				rstflUrl = tdArry[i];
				break;
			
			case 8 : //Soap Url
				soapMethods = tdArry[i];
				break;
			
			case 9 : //WSRV_SN
				wsrvSn = tdArry[i];
				break;
		}
		
	}
	
	var param = new Array();
	var input = new Array();
	
	param.push(["senarioSn", senarioSn]);
	param.push(["senarioSj", senarioSj]);
	param.push(["senarioCn", senarioCn]);
	param.push(["intrfcId", intrfcId]);
	param.push(["wsrvNm", wsrvNm]);
	param.push(["testParamtrCn", testParamtrCn]);
	param.push(["rstflUrl", rstflUrl]);
	param.push(["soapMethods", soapMethods]);
	param.push(["wsrvSn", wsrvSn]);
	
	for(var i=0; i<param.length; i++){
		
		input[i] = document.createElement("input");
		input[i].setAttribute("type", "hidden");
		input[i].setAttribute("name", param[i][0]);
		input[i].setAttribute("value", param[i][1]);
		
		$("[name=unitTestDetail]").append(input[i]);
		
	}
	
	//popup 오픈
	window.open("/ApiClient/unitTestDetail", "popup_id", "width=1100, height=800, left=600, top=100");
	$("[name=unitTestDetail]").submit();
}

/*테이블 생성*/
function ctrateTable(data){
	//생성된 테이블 삭제
	$("#apiTable tbody").remove();
	
	//count
	$("#lbCount").text(data.resultData.length);
	
	//조회한 시나리오 데이터 테이블 추가
	var str = "";
	str += "<tbody>";
	
	for(var i=0; i<data.resultData.length; i++){
		
		str += "<tr>";					
		str += "<td class='align-center'>"+(i+1)+"</td>";			 						 //No.
		str += "<td>"+data.resultData[i]["senarioSn"]+"</td>";		 					 	 //시나리오 순번
		str += "<td>"+data.resultData[i]["senarioSj"]+"</td>";								 //시나리오 제목
		str += "<td>"+data.resultData[i]["senarioCn"]+"</td>";								 //시나리오 내용
		str += "<td>"+data.resultData[i]["intrfcId"]+"</td>";								 //API 아이디
		str += "<td>"+data.resultData[i]["wsrvNm"]+"</td>";									 //API 명
		str += "<td style='display:none;'>"+data.resultData[i]["testParamtrCn"]+"</td>";     //파라미터 내용
		str += "<td style='display:none;'>"+data.resultData[i]["rstflUrl"]+"</td>";  		 //REST URL
		str += "<td style='display:none;'>"+data.resultData[i]["soapMethods"]+"</td>";  	 //SOAP URL
		str += "<td style='display:none;'>"+data.resultData[i]["wsrvSn"]+"</td>"; 	 	     //wsrv 순번
		str += "<td class='align-center'>";							                         //#
		str += "<button type='button' class='btn btn-primary' id='btnPopup_"+i+"' onClick='startPopupDetail(this)'>실행</button>";
		str += "</td>";					
		str += "</tr>";
	}
	str += "</tbody>";
	
	setTimeout(function(){
		$("#apiTable").append(str);
	},300);
	
	
}

/* 파일 다운로드 */
function onDownLoad(type){
	var fileName = "";
	//소스 다운로드
	if(type == "source"){
		fileName = "lms_client.zip";
	//개발자 가이드 다운로드 파일명은 수동으로 관리함 버전업 할때마다 fileName 변경해야함
	}else if(type == "guide"){
		fileName = "검사기관개발가이드_v0.9.zip";
	}

	$(location).attr("href", "/ApiClient/unitTestFileDownLoad?fileName="+fileName+"");
}
</script>


</head>
<body>
	<div class="container" style="width:90%;">
		<h2>통합LIMS WEB API 테스트 </h2>
		<div class="row">
			<div class="col-md-12" style="text-align:right;">
				<button type="button" class="btn" onclick="onDownLoad('source')">Source 다운로드</button>
				<button type="button" class="btn" onclick="onDownLoad('guide')">개발가이드 다운로드</button>
			</div>			
		</div>
		<br/>
		
		<!-- 검색조건 panel 시작 -->
		<div class="panel-group">
			<div class="panel panel-primary">
				<div class="panel-heading">검색조건</div>
				<div class="panel-body">
					<div class="row">
						<div class="col-md-1"><h5>통합 테스트 목록
												
						</h5></div>
						<div class="col-md-4" >
							<select id="unityTestSn" class="form-control">
							</select>
						</div>
						<div class="col-md-2">
							<button id="btnSearch" type="button" class="btn btn-primary">검색</button>
						</div>
					</div>
					<br/>
					<div class="row">
						<div class="col-md-1">통합 테스트 :</div>
						<div class="col-md-7"><label id="unityNm"></label></div>
					</div>
				</div>
			</div>
		</div>
		<!-- 검색조건 panel 종료 -->
		
		<!-- 시스템 통합 테스트 시나리오 panel 시작 -->
		<div class="panel-group">
			<div class="panel panel-primary">
				<div class="panel-heading">시스템 통합 테스트 시나리오 </div>
				<div class="panel-body">
					<div class="row">
						<div class="col-md-1">Count : <label id="lbCount"></label></div>
					</div>
					<div class="row">
						<div class="col-md-12">
							<div class="container" style="width:100%;">
							<table id="apiTable" class="table table-bordered">
								<thead class="thead-dark">
									<tr>
										<th>No.</th>
										<th>시나리오 순번</th>
										<th>시나리오 제목</th>
										<th>시나리오 내용</th>
										<th>API 아이디</th>
										<th>API 명</th>
										<th>#</th>
									</tr>
								</thead>
							</table>
							</div>
						</div>
					</div>
				</div>
			</div>			
		</div>
		<!-- 시스템 통합 테스트 시나리오 panel 종료 -->
	</div>
</body>
</html>