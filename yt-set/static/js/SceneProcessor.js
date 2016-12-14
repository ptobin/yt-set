var SceneProcessor = function(_partnerID, _fileName, _arrayOfScenes){
	this.partnerId = _partnerID;
	this.fileName = _fileName;
	this.scenes = _arrayOfScenes.slice();
	this._init();
}
/*
var SceneProcessor = function(intArray){
	var sceneDuration = 2;	
	var size = intArray.length;
	var result = new Array();

 	for( i = 0; i < size; i++){
		var action;
		var actionAsInt = intArray[i];
		if(actionAsInt == 0){
			action = 'keep';
		}
		else{
			if(actionAsInt == 1){
				action = 'remove';
			}
			else{
				action = 'exclude';
			}
		}
		//Scene(index, start_time, end_time, red, green, blue, action, reviewed)
		var scene = new Scene(i, (i*10), ((i+1)*10) ,0 ,0 ,0 ,action ,false);
		result.push(scene);
	}
	this.scenes = result.slice();
 	this.init();
};
*/

SceneProcessor.readScenesFromTrix = function(){
  var trix = SpreadsheetApp.openById("1meHFs5Be7gBxy8wtqNKUrAYuF0n42qsckx0g054ScgA").getSheetByName("scenes");
  var value = trix.getRange("B3").getValue();
  var binaryArray = JSON.parse("[" + value + "]");
  var sceneProcessor = new SceneProcessor(binaryArray);
  return sceneProcessor;
}

SceneProcessor.prototype._init = function(){
  this.scenesForRemoval = this._getScenesForRemoval();
  this.scenesForExclusion = this._getScenesForExclusion();
  this.scenesToBeKept = this._getScenesToBeKept();
  
  this.mergedScenesForRemoval = this._mergeAdjacentScenes(this.scenesForRemoval);
  this.mergedScenesForExclusion = this._mergeAdjacentScenesForExclusion(this.scenesForExclusion);
  this.mergedScenesToBeKept = this._mergeAdjacentScenes(this.scenesToBeKept);

  this.scenesToBeKeptAsJSON = JSON.stringify(this.mergedScenesToBeKept);
  this.scenesForRemovalAsJSON = JSON.stringify(this.mergedScenesForRemoval);

  //this.referenceExclusionsAsString = scenePro._getReferenceExclusions(mergedScenesForExclusion);
  this.combinedScenes = this._combineSceneBlocks();
 
}

SceneProcessor.prototype._adjustOffsets = function(_scenes){
  var offset = 0;
  for(i = 0; i < _scenes.length; i++){
    var scene = _scenes[i];
    //var duration =  ;
    scene.new_start = offset;
    scene.new_end = scene.getDuration() + offset;
    offset = scene.new_end;
  }
  return _scenes;
}

SceneProcessor.prototype._combineSceneBlocks = function(){
  if(this.mergedScenesToBeKept.length == 0){
    return this.mergedScenesForRemoval;
  }
  
  if(this.mergedScenesForRemoval.length == 0){
    return this.mergedScenesToBeKept;
  }
  
  var merged = this.mergedScenesToBeKept.concat(this.mergedScenesForRemoval);
  var result =  merged.sort(function(sceneA,sceneB){return sceneA.start - sceneB.start});
  for(i=0;i< result.length;i++){
    result[i].index = i;
  }
  return result;
};


SceneProcessor.prototype.getOriginalVideoLength = function(){
  var videoLength = 0;
  for(i=0; i< this.scenes.length; i++){
    videoLength += scenes[i].getDuration();
  }
  return videoLength;
};

SceneProcessor.prototype._getScenesForRemoval = function(){
  var result = new Array();
  for(i=0; i < this.scenes.length; i++){
    var scene = this.scenes[i];
    if(scene.action == 'remove'){
      result.push(scene);
    }
  }
  return result;
};

SceneProcessor.prototype._getScenesToBeKept = function(){
  var result = new Array();
  for(i=0;i<this.scenes.length;i++){
    var scene = this.scenes[i];
    if(scene.action != 'remove'){
      result.push(this.scenes[i]);
    }
    else{
    }
  }  
  
  return this._adjustOffsets(result);
  
};

SceneProcessor.prototype._getScenesForExclusion = function(){
  var result = new Array();
  for(i=0; i < this.scenes.length; i++){
    var scene = this.scenes[i];
    if(scene.action == 'exclude'){
      result.push(scene);
    }
  }
  return result;
};

/*
* creates the string representation of the reference exlusion segments expected by the CSV web video template
* resuting string has the following pattern:
* 00:00:00-00:00:10|00:00:25-00:00:30|00:00:40-00:00:50|00:00:55-00:01:05|00:01:15-00:01:20|00:01:30-00:01:40
*/
SceneProcessor.prototype.getReferenceExclusions = function(){
  var result = new String();
  for(i=0; i < this.mergedScenesForExclusion.length; i++){
    result = result + this.mergedScenesForExclusion[i].getStartEndTime();
    if(i < (this.mergedScenesForExclusion.length-1)){
      result = result + "|";
    }
  }
  return result;
};

/*
produces the string expected by the ssimple.py python script to create the command line for FFMPEG for file splitting
segments = [
[ 3, 5.5 ] ,
[ 10.11, 14.1 ],
[ 20.2, 30.3]
]
*/
SceneProcessor.prototype.getSegmentsForFFMPEG = function(){
  var result = "segments = [";
  for(i = 0 ; i < this.mergedScenesToBeKept.length ; i++){
    var scene = this.mergedScenesToBeKept[i];
    var segmentForPython = scene.getSceneElementForPython();
    result += segmentForPython;
    if(i < (this.mergedScenesToBeKept.length -1)){
      result += ",";
    }
  }
  result += " ]"
  return result;
}

SceneProcessor.prototype.getSegmentsForLibAV = function(){
  var result = new String();
  for(i=0; i < this.mergedScenesToBeKept.length; i++){
    result = result + this.mergedScenesToBeKept[i].getStartDuration();
    if(i < (this.mergedScenesToBeKept.length-1)){
      result = result + "|";
    }
  }
  return result;
}


SceneProcessor.prototype._mergeAdjacentScenes = function(_scenesInput){
  if(_scenesInput.length < 2){
    return _scenesInput;
  };
  
  var mergedScenes = new Array();
  var addedScenes = 0;
  var added = false;
  var sceneStart = _scenesInput[0].start;
  var sceneEnd = _scenesInput[0].end;
  var forEndsAt = _scenesInput.length -1; 
  for(i = 0; i < forEndsAt; i++){
    var currentScene = _scenesInput[i]
    var nextScene = _scenesInput[i+1];
    if((nextScene.index - currentScene.index) == 1 ){
      //this is an adjacent scene
      sceneEnd = nextScene.end;
      added = false;
    }
    else{
      var sceneBlock = new Scene(addedScenes, sceneStart, sceneEnd,0,0,0,currentScene.action, true);
      addedScenes = addedScenes + 1;
      mergedScenes.push(sceneBlock);
      sceneStart = _scenesInput[i+1].start;
      sceneEnd = _scenesInput[i+1].end;
      added = true;
    }
  }
  if(added == false){
    var sceneBlock = new Scene(addedScenes, sceneStart, sceneEnd, 0,0,0, currentScene.action, true);
    mergedScenes.push(sceneBlock);
  };
  
  addedScenes = addedScenes + 1;
  var lastScene = _scenesInput[_scenesInput.length -1];
  if(lastScene.end != mergedScenes[mergedScenes.length-1].end){
    var sceneBlock = new Scene(addedScenes , lastScene.start, lastScene.end, 0,0,0, lastScene.action, true);
    mergedScenes.push(sceneBlock);
  }
  return mergedScenes;
};


SceneProcessor.prototype._mergeAdjacentScenesForExclusion =function(_scenesInput){
  if(_scenesInput.length < 2){
    return _scenesInput;
  };
  
  var mergedScenes = new Array();
  var addedScenes = 0;
  var added = false;
  var sceneStart = _scenesInput[0].new_start;
  var sceneEnd = _scenesInput[0].new_end;
  var forEndsAt = _scenesInput.length -1; 
  for(i = 0; i < forEndsAt; i++){
    var currentScene = _scenesInput[i]
    var nextScene = _scenesInput[i+1];
    if((nextScene.index - currentScene.index) == 1 ){
      //this is an adjacent scene
      sceneEnd = nextScene.new_end;
      added = false;
    }
    else{
      var sceneBlock = new Scene(addedScenes, sceneStart, sceneEnd,0,0,0,currentScene.action, true);
      addedScenes = addedScenes + 1;
      mergedScenes.push(sceneBlock);
      sceneStart = _scenesInput[i+1].new_start;
      sceneEnd = _scenesInput[i+1].new_end;
      added = true;
    }
  }
  if(added == false){
    var sceneBlock = new Scene(addedScenes, sceneStart, sceneEnd, 0,0,0, currentScene.action, true);
    mergedScenes.push(sceneBlock);
  };
  
  addedScenes = addedScenes + 1;
  var lastScene = _scenesInput[_scenesInput.length -1];
  if(lastScene.new_end != mergedScenes[mergedScenes.length-1].new_end){
    var sceneBlock = new Scene(addedScenes , lastScene.new_start, lastScene.new_end, 0,0,0, lastScene.action, true);
    mergedScenes.push(sceneBlock);
  }
  return mergedScenes;
};


