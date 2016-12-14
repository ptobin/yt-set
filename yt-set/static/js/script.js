$(function(){
	$('button').click(function(){
		
		var _partnerName = "partner_1";
		var _fileName = $('#txtFileName').val();
		var _encoder = $('#txtUsername').val();
		var scene1 = new Scene(1, 0, 180, 0, 0, 0, "remove", true);
		var scene2 = new Scene(2, 180, 240, 0, 0, 0, "keep", true);
		var scene3 = new Scene(3, 240, 300, 0, 0, 0, "keep", true);
		var scene4 = new Scene(4, 360, 420, 0, 0, 0, "exclude", true);
		var scene5 = new Scene(5, 420, 480, 0, 0, 0, "remove", true);
		var scene6 = new Scene(6, 480, 540, 0, 0, 0, "keep", true);
		var sceneArray = new Array();
		sceneArray.push(scene1);
		sceneArray.push(scene2);
		sceneArray.push(scene3);
		sceneArray.push(scene4);
		sceneArray.push(scene5);
		sceneArray.push(scene6);
		
		
		//var user = $('#txtUsername').val();
		//var binaryArray = JSON.parse("[" + user + "]");
		//console.log("user:" + user);
		//console.log("binaryArray:" + binaryArray);
		
		var scenePro = new SceneProcessor(_partnerName, _fileName, sceneArray);
	    var _segmentForFFMPEG = scenePro.getSegmentsForFFMPEG();
		var _segmentForLibAV = scenePro.getSegmentsForLibAV();
		var _referenceExclusions = scenePro.getReferenceExclusions()
		
		var dataToSend = new Object();
		dataToSend.exclusions = _referenceExclusions;
		dataToSend.segmentForFFMPEG = _segmentForFFMPEG;
		dataToSend.segmentForLibAB = _segmentForLibAV;
		dataToSend.fileName = _fileName;
		dataToSend.partnerName = _partnerName;
		dataToSend.encoder = _encoder;

		$.ajax({
			type: 'POST',
			url: '/signUpUser',
			data: JSON.stringify(dataToSend),
			contentType: "application/json; charset=utf-8",
			traditional: true,
			success: function (response){
				console.log(response);
				var responseAsObject = JSON.parse(response);
				var received_file = responseAsObject.received_file;
				var received_exclusions = responseAsObject.received_exclusions;
				var received_python_segments = responseAsObject.received_python_segments;
				var received_message_id = responseAsObject.message_id;
				
				$('#txtExclusions').val(received_exclusions);
				$('#txtPythonSegments').val(received_python_segments);
				$('#txtMessage_id').val(received_message_id);
			},
			error: function(error){
				console.log(error);
			}
		});
	});
});
