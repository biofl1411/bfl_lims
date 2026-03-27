<%@page import="java.util.ResourceBundle"%>
<%@ page language="java" contentType="text/html; charset=UTF-8"  pageEncoding="UTF-8"%>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<meta charset="UTF-8"/>

<script type="text/javascript" src="<%=request.getContextPath()%>/resources/js/jquery-3.3.1.min.js"></script>
<script type="text/javascript" src="<%=request.getContextPath()%>/resources//bootstrap-3.3.2-dist/js/bootstrap.min.js"></script>
<link rel="stylesheet" href="<%=request.getContextPath()%>/resources//bootstrap-3.3.2-dist/css/bootstrap.min.css"/>
<link rel="stylesheet" href="<%=request.getContextPath()%>/resources/css/unitTest.css"/>

<title>파라미터 만들기</title>

<%
	request.setCharacterEncoding("UTF-8");
	//jsp 에서 사용하기위해서 properties 파일 불러오기
	ResourceBundle resource = ResourceBundle.getBundle("application");
	//lims Url
	String wslimsUrl = resource.getString("wslimsUrl");
	String testParam = request.getParameter("testParamtrCn").replaceAll("\\\\", "/");
%>
<script language='javascript'>

var dataType = '<%=request.getParameter("type") %>';
var dataWsrvSn = '<%=request.getParameter("wsrvSn") %>';
var wslimsUrl = '<%=wslimsUrl %>';

$(document).ready(function(){
	init();
});


function init(){
	//파라미터 내용 String 으로 저장
	var txtParameter = '<%=testParam %>';
	$("#txtTestParamtrCn").val(txtParameter.toString());
	
	if(dataType == "new"){
		//파라미터 생성 신규
		newCreateParameterTable();
	}	
	else if(dataType == "modify"){
		//파라미터 수정
		modifyCreateParameterTable();
	}
	
}

/* 웹서비스 순번 조회 */
function selectParameter(){
	
	var paramUrl = encodeURI(wslimsUrl + "/webService/rest/selectWsrvItem", "UTF-8");
	var unityTestSn = $("#unityTestSn option:selected").val();
	var type = "rest";
	
	var param = {"url" : paramUrl, "type" : type, "param" : {"wsrvSn" : dataWsrvSn}};
	
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

/* 신규 파라미터 생성 */
function newCreateParameterTable(){
	var data = selectParameter();
	var lstNm = ""; //lst 명을 저장
	
	var str = "";
	var cnt = 0;
		
	str = "<tbody>";
	for(var i=0; i < data.resultData.length; i++){
				
		if(!data.resultData[i]["upperIemId"]){
			data.resultData[i]["upperIemId"] = "null";
		}
		
		if(data.resultData[i]["iemTy"] == "LST"){
			str += "<tr id='"+data.resultData[i]["wsrvIemId"]+"' class='LST'>";
			str += "<td></td>";	//No.
			
			lstNm = data.resultData[i]["wsrvIemId"];//LST 이름을 저장
			
			str += "<td>" + data.resultData[i]["wsrvIemId"] + "</td>"; //항목
			
			//항목 한글명 null 이면 빈값
			if(data.resultData[i]["wsrvIemNm"] == null || data.resultData[i]["wsrvIemNm"] == "null" || data.resultData[i]["wsrvIemNm"] == ""){
				str += "<td></td>";
			}
			else{
				str += "<td>" + data.resultData[i]["wsrvIemNm"] + "</td>"; //항목 한글명
			}			
			
			str += "<td></td>"; //데이터
			
			//항목유형 null 이면 빈값
			if(data.resultData[i]["iemTy"] == null || data.resultData[i]["iemTy"] == "null" || data.resultData[i]["iemTy"] == ""){
				str += "<td></td>";
			}			
			else{
				str += "<td>" + data.resultData[i]["iemTy"] + "</td>";
			}			
			
			str += "<td>";			
			str += "<div class='btn-group'>"
			str += "<button type='button' class='btn btn-primary' id='"+data.resultData[i]["wsrvIemId"]+"' onClick='addRow(this)'>추가</button>";
			str += "<button type='button' class='btn btn-primary' id='"+data.resultData[i]["wsrvIemId"]+"' onClick='delRow(this)'>삭제</button>";
			str += "</div>";
			str += "</td>";
			lstNm = "LST";
			cnt++;
		}
		else{
			
			if(data.resultData[i]["iemTy"] != "OBJ" && data.resultData[i]["upperIemId"] == "null"){
				str += "<tr class='BASE'>";
			}
			else if(data.resultData[i]["iemTy"] == "OBJ" && data.resultData[i]["upperIemId"] == "null"){
				str += "<tr id='"+data.resultData[i]["wsrvIemId"]+"' class='OBJ'>";
				lstNm = "OBJ";
			}
			else{
				if(lstNm == "LST"){
					str += "<tr name='"+lstNm+cnt+"' class='"+data.resultData[i]["upperIemId"]+" danger'>";
				}else{
					str += "<tr name='"+lstNm+cnt+"' class='"+data.resultData[i]["upperIemId"]+"'>";
				}
				
			}
			
			str += "<td>"+ (i+1) +"</td>";	//No.
			
			str += "<td>" + data.resultData[i]["wsrvIemId"] + "</td>"; //항목
			
			//항목 한글명  null 이면 빈값
			if(data.resultData[i]["wsrvIemNm"] == null || data.resultData[i]["wsrvIemNm"] == "null" || data.resultData[i]["wsrvIemNm"] == ""){
				str += "<td></td>";
			}			
			else{
				str += "<td>" + data.resultData[i]["wsrvIemNm"] + "</td>"; //항목 한글명
			}			
			
			if(data.resultData[i]["iemTy"] == "OBJ" && data.resultData[i]["upperIemId"] == "null"){
				str += "<td></td>";
			}
			else{
				str += "<td>";
				str += "<input type='text' class='form-control' id='txtData_"+i+"'>"; //데이터
				str += "</td>";				
			}
			
			
			//항목유형 null 이면 빈값
			if(data.resultData[i]["iemTy"] == null || data.resultData[i]["iemTy"] == "null" || data.resultData[i]["iemTy"] == ""){
				str += "<td></td>";	   
			}			
			else{
				str += "<td>" + data.resultData[i]["iemTy"] + "</td>";
			}
			
			str += "<td></td>";
		}	
		
		str += "</tr>";
		
	}
	str += "</tbody>";
	
	$("#createParamTable").append(str);
	
	sort(); //No. 정렬
}

/* 넘어온 파라미터 수정 */
function modifyCreateParameterTable(){
	newCreateParameterTable();
	
	var data = selectParameter();
	
	paramCnVal = '<%=testParam %>';
	
	if(paramCnVal){
		var testParamtrCn = JSON.parse(paramCnVal);
	}
	
	//해당 API의 파라미터 정보가 DB에 저장되어있으면 테이블 생성후 값 적용 
	if(data.resultData.length > 0){
		
		var trLength = $("#createParamTable").find("tr").length;
		var objInput ;
		var objInputValue ;
		
		/************* 기본정보 데이터와 OBJ 대이터룰 테이블과 비교하여 넘어온 데이터 적용 시작 *************/
		$.each(testParamtrCn, function(index, item){
			
			for(var i=0; i<trLength; i++){
				if($("#createParamTable").find("tr").eq(i).find("td").eq(1).text() == index){
					
					if(typeof(item) == "string"){
						
						objInput = $("#createParamTable").find("tr").eq(i).find("td").eq(3).children("input")[0];
						
						if(!testParamtrCn[index]){
							objInputValue = "";
						}
						else{
							objInputValue = testParamtrCn[index];
						}						
						
						objInput.value = objInputValue;
							
					}
					else{

						$.each(testParamtrCn[index], function(sIndex, sItem){
							for(var j=0; j<trLength; j++){
								if($("#createParamTable").find("tr").eq(j).find("td").eq(1).text() == sIndex){
									if(!testParamtrCn[index].length){
										objInput = $("#createParamTable").find("tr").eq(j).find("td").eq(3).children("input")[0];
										
										if(!sItem){
											objInputValue = "";
										}
										else{
											objInputValue = sItem;
										}										
										
										objInput.value= objInputValue;
									}
								}
							}
						});
					}
				}
			}
		});	
		/************* 기본정보 데이터 테이블과 비교하여 넘어온 데이터 적용 종료 *************/
		
		/************* LST length 가 1인 데이터 테이블과 비교하여 넘어온 데이터 적용 시작 *************/
		var input ;
		var inputValue ;
		
		for(var i=0; i<$(".LST").length; i++){
			for(var j=0; j<$("."+$(".LST").eq(i)[0]["id"]).length; j++){
				$.each(testParamtrCn, function(index, item){
					if(index == $(".LST").eq(i)[0]["id"]){
						for(var y=0; y<testParamtrCn[index].length; y++){
							if(testParamtrCn[index].length == 1){
								input = $("."+$(".LST").eq(i)[0]["id"]).eq(j).find("td").eq(3).children("input")[0];								
								
								if(!testParamtrCn[index][i][$("."+$(".LST").eq(i)[0]["id"]).eq(j).find("td").eq(1).text()]){
									inputValue = "";
								}
								else{
									inputValue = testParamtrCn[index][i][$("."+$(".LST").eq(i)[0]["id"]).eq(j).find("td").eq(1).text()];
								}
								
								input.value = inputValue;
								
							}
						}
					}
				});	
			}
		}
		/************* LST length 가 1인 데이터 테이블과 비교하여 넘어온 데이터 적용 종료 *************/
		
		/************* detail 에서 넘어온 데이터를 확인하여 추가 테이블 생성 시작 *************/
		var lstLength = $(".LST").length;
		var lstClassLength = 0;
		var lstId = "";
		var paramJson = new Object();
		
		for(var i=0; i<lstLength; i++){
			
			lstId = $(".LST").eq(i)[0]["id"];
			lstClassLength = $("."+$(".LST").eq(i)[0]["id"]).length;
			
			for(var j=0; j<lstClassLength; j++){
				$.each(testParamtrCn, function(index, item){
					
					if(index == lstId){
						if(testParamtrCn[index].length > 1){
							paramJson[index] = testParamtrCn[index].length;
							
						}				
					}
				});
			}
		}
		
		//name 을 다른 tr과 다르게 주기위해서 랜덤으로 작성, JSON 만들기에서 구분하기위해 필요
		var lstText = "";
		var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890";
		var cnt = 0;
		var str = "";
		var color = "info";
		var delLstName = new Object();
		
		$.each(paramJson, function(index, item){
			cnt = $("."+index).length;
			str = "";
			
			
			
			for(var i=0; i<parseInt(item); i++){
				
				
				lstText = "";
				
				for(var x=0; x<7; x++){
					lstText += possible.charAt(Math.floor(Math.random() * possible.length));
				}
				
				for(var j=0; j<cnt; j++){
					
					if($("."+index).eq(j).attr("name")){
						delLstName[$("."+index).eq(j).attr("name")] = $("."+index).eq(j).attr("name");
					}
					
					
					var inputVal = testParamtrCn[index][i][$("."+index).eq(j).find("td").eq(1).text()];
					
					if(!inputVal){
						inputVal = "";
					}
					
					
					str += "<tr name='LST"+lstText+"' class='"+index+" "+color+"'>";
					str += "<td></td>";
					str += "<td>"+$("."+index).eq(j).find("td").eq(1).text()+"</td>";
					str += "<td>"+$("."+index).eq(j).find("td").eq(2).text()+"</td>";
					str += "<td><input type='text' id='txtData_"+lstText+"' class='form-control' value='"+inputVal+"'></td>";
					str += "<td>"+$("."+index).eq(j).find("td").eq(4).text()+"</td>";					
					str += "<td>"+$("."+index).eq(j).find("td").eq(5).text()+"</td>";
					
					var fileLstNm = $("."+index).eq(j).find("td").eq(6).text();
					
					if(fileLstNm == "File"){
						str += "<td style='display:none;'>File</td>";
					}
					else{
						str += "<td></td>";
					}
					
					str += "</tr>";
					
				}
				
				if(color == "danger"){
					color = "info";
				}
				else{
					color = "danger";
				}
				
			}
			
			$("#"+index).after(str);
			sort();
			
		});	

		$.each(delLstName, function(index, item){			
			$("tr[name="+index+"]").remove();
			
		});
		/************* detail 에서 넘어온 데이터를 확인하여 추가 테이블 생성 종료 *************/
	}
}

/*LST 추가*/
function addRow(event){
	var targetClass = event.id;
	var paramData = selectParameter();
	var backGroundColor = "";
	
	var str = "";
	//name 을 다른 tr과 다르게 주기위해서 랜덤으로 작성, JSON 만들기에서 구분하기위해 필요
	var text = "";
	var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890";
	
	for(var i=0; i<7; i++){
		text += possible.charAt(Math.floor(Math.random() * possible.length));
	}
	
	//DB에 저장된 파라미터 정보가 있을떄
	if(paramData.resultData.length > 0){
		for(var i=0; i<paramData.resultData.length; i++){		
			
			if(paramData.resultData[i]["upperIemId"] == targetClass){
				if($("#"+targetClass).next()[0]["className"].indexOf("danger") != -1){
					backGroundColor = "info";
				}
				else{
					backGroundColor = "danger";
				}
				
				str += "<tr name='LST"+text+"' class='"+targetClass+" "+backGroundColor+"'>";
				str += "<td class='add'></td>";
				str += "<td name='wsrvId'>"+paramData.resultData[i]["wsrvIemId"]+"</td></td>";
				str += "<td name='wsrvNm'>"+paramData.resultData[i]["wsrvIemNm"]+"</td></td>";
				str += "<td><input type='text' class='form-control'></td>";				
				str += "<td></td>";
				str += "<td></td>";
				
		 		str += "</tr>";
			}			
		}
	}
	
	
	
	$("#"+targetClass).after(str);
	
	sort(); //No. 정렬
	
}

/*LST 삭제*/
function delRow(event){
	//선택한 버튼의 상위 tr id
	var trId = event.id; 
	var paramData = selectParameter();
	
	for(var i=0; i<paramData.resultData.length; i++){
		if(paramData.resultData[i]["upperIemId"] == trId){
			if($("#"+trId).next().children("td")[0]["className"] == "add"){
				$("#"+trId).next().remove();
			}
		}
	}
	
	sort(); //No. 정렬
}

/* No. 순서 다시 정렬 */
function sort(){
	
	var trLength = $("#createParamTable").find("tr").length;
	var cnt = 0;
	
	for(var i=1; i<trLength; i++){
		$("#createParamTable").find("tr").eq(i).find("td").eq(0).text(i);
		cnt++;
	}
	
	$("#lbCount").text(cnt);
}

/* JSON 만들기 */
function createJson(){
	
	$("#txtJsonApply").val("");
	
	var trCnt = $("#createParamTable").find("tr").length;
    var str = "";

    var strText = "";
	var strValue = "";
	var eqType = "";
	var eqTypeNm = "";
	var eqListTypeNm = "";
	
	var eqCntType = "";
	
	var baseCnt = 0;
	var lstCnt = 0;
	var i = 1;
	
	str += "{";
	
	for(i; i<trCnt; i++){
		eqType = $("#createParamTable").find("tr").eq(i)[0]["className"];
		eqTypeNm = $("#createParamTable").find("tr").eq(i).find("td").eq(1).text();

		if(eqType == "BASE"){
			strText = $("#createParamTable").find("tr").eq(i).find("td").eq(1).text();
			strValue = $("#createParamTable").find("tr").eq(i).find("td").eq(3).children("input")[0].value;

			if(i == 1){
				str += "\""+strText+"\"" + ":" + "\""+strValue+"\"";
			}
			else{
				str += "," + "\""+strText+"\"" + ":" + "\""+strValue+"\"";
			}			
		}
		else if(eqType == "OBJ"){
			
			var j = i + 1;
			
			str += "," + "\""+eqTypeNm+"\"" + ":{";
			
			for(j; j<trCnt; j++){
				eqCntType = $("#createParamTable").find("tr").eq(j).find("td").eq(4).text();
				
				if(eqCntType != ""){
					
					i = j - 1;
					
					break;
				}
				
				strText = $("#createParamTable").find("tr").eq(j).find("td").eq(1).text();
				strValue = $("#createParamTable").find("tr").eq(j).find("td").eq(3).children("input")[0].value;
				
				str += "\""+strText+"\"" + ":" + "\""+strValue+"\"" + ",";
				
				
			}
			str = str.substring(0, str.length-1);
			str += "}";
			
			
		}
		else if(eqType == "LST"){
			eqTypeNm = $("#createParamTable").find("tr").eq(i).find("td").eq(1).text();
			
			str += "," + "\""+eqTypeNm+"\"" + ":[";
			
			//해당 List row 수
			var classLength = $("."+eqTypeNm).length;
			
			//List 아래 묶음 수
			var trNm = $("#createParamTable").find("tr").eq(i).next("tr").attr("name");
			var trNmLength = $("[name='"+trNm+"']").length;			
			var cnt = i + 1;
			
			for(var y=1; y<=(classLength/trNmLength); y++){
			
				str += "{";
				
				for(var x=1; x<=trNmLength; x++){
					
					strText = $("#createParamTable").find("tr").eq(cnt).find("td").eq(1).text();
					strValue = $("#createParamTable").find("tr").eq(cnt).find("td").eq(3).children("input")[0].value;
					
					str += "\""+strText+"\"" + ":" + "\""+strValue+"\"" + ",";
					cnt++;
				}
				str = str.substring(0, str.length-1);
				str += "},";
				
			}
			str = str.substring(0, str.length-1);
			
			str += "]";
		}
	}
	
	
	str += "}";
	
	$("#txtJsonApply").val(str);
	
	
}

/*뒤로가기로 unitTestDetail.jsp 이동*/
function backUnitTestDetail(){
	unitTestDetail("back");
}

/*JSON 적용 으로 unitTestDetail.jsp 이동*/
function jsonApply(){
	unitTestDetail("json");
}

function unitTestDetail(type){
	
	var tr = $("#createParamTable").find("tbody").find("tr");	
	var fileCnt = 0;
	
	for(var i=0; i<tr.length; i++){
		
		if(tr.eq(i).find("td").eq(6).text() == "File"){
			fileCnt++;
		}
	}
	
	var form = "<form name='unitTestDetail' method='post' action='/ApiClient/unitTestDetail'>";
	
	$("body").append(form);
	
	var param = new Array();
	var input = new Array();
	
	param.push(["senarioSj",	 $("#txtSenarioSj").val()]);
	param.push(["senarioCn",	 $("#txtSenarioCn").val()]);
	param.push(["rstflUrl", 	 $("#txtRstflUrl").val()]);
	param.push(["soapMethods",	 $("#txtSoapMethods").val()]);
	param.push(["intrfcId", 	 $("#txtIntrfcId").val()]);		
	param.push(["wsrvSn",	     $("#txtWsrvSn").val()]);
	param.push(["fileCount",     fileCnt]);
	
	//json : JSON 적용, back : 뒤로가기
	if(type == "json"){
		param.push(["testParamtrCn", $("#txtJsonApply").val()]);
	}
	else{
		param.push(["testParamtrCn", $("#txtTestParamtrCn").val()]);
	}
	
	for(var i=0; i<param.length; i++){
		
		input[i] = document.createElement("input");
		input[i].setAttribute("type", "hidden");
		input[i].setAttribute("name", param[i][0]);
		input[i].setAttribute("value", param[i][1]);
		
		$("[name='unitTestDetail']").append(input[i]);
		
	}
	
	$("[name='unitTestDetail']").submit();
}

/* JSON 적용 버튼 클릭 */
function createJsonApply(){	
	
	/* JSON textarea 에 데이터 가 있는지 체크 */
	if(!$("#txtJsonApply").val()){
		$("#jsonApplyNull").modal();
		return;
	}
	
	var regex = /[^0-9]/g;
	
	/* JSON 형식에 숫자만 있을때 */
	if(!regex.test($("#txtJsonApply").val())){
		$("#checkJson").modal();
		return;
	}
	
	/* JSON 형식 체크 */
	try{
		JSON.parse($("#txtJsonApply").val().toString())
	}catch(error){
		$("#checkJson").modal();
		return;
	}finally{
		
	}
	
	$("#jsonApply").modal();
}
</script>

</head>
<body>

	<input type="hidden" id="txtSenarioSj" 		value="<%=request.getParameter("senarioSj")%>">
	<input type="hidden" id="txtSenarioCn" 		value="<%=request.getParameter("senarioCn")%>">
	<input type="hidden" id="txtRstflUrl" 		value="<%=request.getParameter("rstflUrl")%>">
	<input type="hidden" id="txtSoapMethods"	value="<%=request.getParameter("soapMethods")%>">
	<input type="hidden" id="txtIntrfcId" 		value="<%=request.getParameter("intrfcId")%>">
	<input type="hidden" id="txtTestParamtrCn"  value="">
	<input type="hidden" id="txtWsrvSn" 		value="<%=request.getParameter("wsrvSn") %>">
	
	<div class="container">
		<h2>파라미터 만들기</h2>
		<!-- 파라미터 만들기 panel 시작 -->
		<div class="panel-group">
			<div class="panel panel-primary"  style="width:900px">
				<div class="panel-heading">파라미터</div>
				<div class="panel-body">
					
					<div class="row">
						<div class="col-md-3">Count : <label id="lbCount"></label></div>
						<div class="col-md-5"></div>
						<div class="col-md-4" style="text-align:right;"><label style="color:red;">*파일 업로드는 신규저장만 됩니다.</label></div>
					</div>
					<div class="row" style="padding-left:20px;">
						<table id="createParamTable" class="table table-bordered" style="width:870px;">										
							<thead class="thead-dark">
								<tr>
									<th>No.</th>
									<th>항목</th>
									<th>항목 한글명</th>
									<th>데이터</th>
									<th>항목 유형</th>
									<th>#</th>
								</tr>
							</thead>
						</table>
					</div>
					<div class='row'>
						<center>
							<div class="btn-group">
								<button type="button" class="btn btn-primary" onClick="createJson()">JSON 만들기</button>
								<button type="button" class="btn btn-primary" data-toggle="modal" data-target="#backDatail" >뒤로가기</button>
							</div>
						</center>
					</div>
				</div>
			</div>
		</div>		
		<!-- 파라미터 만들기 panel 종료 -->
		<!-- JSON panel 시작 -->
		<div class="panel-group">
			<div class="panel panel-primary"  style="width:900px">
				<div class="panel-heading">JSON</div>
				<div class="panel-body">
					<div class="row">
						<div class="col-md-12">						
							<div class="form-group">				
								<textarea id="txtJsonApply" class="form-control" rows="6" cols="5"></textarea>
							</div>		
						</div>	
					</div>								
					<div class="row" >
						<center>
							<button type="button" class="btn btn-primary" onClick="createJsonApply()">JSON 적용</button>
						</center>
					</div>					
				</div>
			</div>
		</div>
		<!-- JSON panel 종료-->
	</div>
	
	<!-- 뒤로가기 클릭 모달창 시작 -->
	<div class="modal fade" id="backDatail" role="dialog">
		<div class="modal-dialog">
			<div class="modal-content">
				<div class="modal-header">
					<button type="button" class="close" data-dismiss="modal">&times;</button>
					<h4 class="mdal-title">뒤로가기</h4>
				</div>
				<div class="modal-body">
					<p>작성된 내용이 모두 초기화 됩니다.</p>
				</div>
				<div class="modal-footer">
					<button type="button" class="btn btn-default" data-dismiss="modal" onClick="backUnitTestDetail()">확인</button>
					<button type="button" class="btn btn-default" data-dismiss="modal">취소</button>
				</div>
			</div>
		</div>
	</div>
	<!-- 뒤로가기 클릭 모달창 종료-->
	<!-- JSON적용 클릭 모달창 시작-->
	<div class="modal fade" id="jsonApply" role="dialog">
		<div class="modal-dialog">
			<div class="modal-content">
				<div class="modal-header">
					<button type="button" class="close" data-dismiss="modal">&times;</button>
					<h4 class="mdal-title">JSON 적용</h4>
				</div>
				<div class="modal-body">
					<p>작성된 JSON 내용이 [시스템 통합 테스트 시나리오 상세정보] 의 파라미터에 적용됩니다, 해당화면에서 작성된 파라미터 내용이 모두 초기화 됩니다.</p>
				</div>
				<div class="modal-footer">
					<button type="button" class="btn btn-default" data-dismiss="modal" onClick="jsonApply()">확인</button>
					<button type="button" class="btn btn-default" data-dismiss="modal">취소</button>
				</div>
			</div>
		</div>
	</div>
	<!-- JSON적용 클릭 모달창 종료-->
	<!-- JSON적용 클릭 데이터가 없을때 시작-->
	<div class="modal fade" id="jsonApplyNull" role="dialog">
		<div class="modal-dialog">
			<div class="modal-content">
				<div class="modal-header">
					<button type="button" class="close" data-dismiss="modal">&times;</button>
					<h4 class="mdal-title">JSON 적용</h4>
				</div>
				<div class="modal-body">
					<p>작성된 JSON 내용이 없습니다.</p>
				</div>
				<div class="modal-footer">
					<button type="button" class="btn btn-default" data-dismiss="modal"">확인</button>
				</div>
			</div>
		</div>
	</div>
	<!-- JSON적용 클릭 데이터가 없을때 종료-->
	<!-- 파라미터 만들기 JSON 유효성 체크 시작 -->
	<div class="modal fade" id="checkJson" role="dialog">
		<div class="modal-dialog">
			<div class="modal-content">
				<div class="modal-header">
					<button type="button" class="close" data-dismiss="modal">&times;</button>
					<h4 class="mdal-title">파라미터 만들기</h4>
				</div>
				<div class="modal-body">
					<p>파라미터 정보의 JSON 형식이 잘못 되었습니다.</p>
				</div>
				<div class="modal-footer">
					<button type="button" class="btn btn-default" data-dismiss="modal">확인</button>
				</div>
			</div>
		</div>
	</div>
	<!-- 파라미터 만들기 파라미터 만들기 JSON 유효성 체크 종료-->
</body>
</html>