var SceneAction = {
  KEEP: 0,
  REMOVE: 1,
  EXCLUDE: 2,
};

var Scene = function(index, start_time, end_time, red, green, blue, action, reviewed){
  this.index = index;
  this.action = action;
  this.start = start_time;
  this.end = end_time;
  this.reviewed = reviewed;
  this.red = red;
  this.green = green;
  this.blue = blue;
  this.new_start = start_time;
  this.new_end = end_time;
};

/*
*   00:10-01:00|01:30-02:00
*/
Scene.prototype.getStartEndTime = function(){
  var startTime = this.getStartTime();
  var endTime = this.getEndTime();
  var result = startTime + "-" + endTime;
  return result;
}

Scene.prototype.getStartDuration = function(){
  var startTime = this.getStartTime();
  var endTime = this.getDurationAsString();
  var result = startTime + "-" + endTime;
  return result;
}

Scene.prototype.getDuration = function(){
  return (this.end - this.start);
}

/*
*   [ 3, 5.5 ]
*/
Scene.prototype.getSceneElementForPython = function(){
  var result = new String();
  result += "[ ";
  result += this.start;
  result += " , ";
  result += this.end;
  result += " ]";
  return result;
}


Scene.prototype.getStartTime = function() {
  return this.convertSecondsToHHMMSS(this.new_start);
}

Scene.prototype.getEndTime = function() {
  return this.convertSecondsToHHMMSS(this.new_end);
}

Scene.prototype.getDurationAsString = function() {
  return this.convertSecondsToHHMMSS(this.new_end - this.new_start);
}

Scene.prototype.convertSecondsToHHMMSS = function(seconds){
  var sec_num = seconds;
  var hours   = Math.floor(sec_num / 3600);
  var minutes = Math.floor((sec_num - (hours * 3600)) / 60);
  var seconds = sec_num - (hours * 3600) - (minutes * 60);
  
  if (hours   < 10) {hours   = "0"+hours;}
  if (minutes < 10) {minutes = "0"+minutes;}
  if (seconds < 10) {seconds = "0"+seconds;}
  var result = hours+':'+minutes+':'+seconds;
  return result;
}

Scene.prototype._testGetStartTime = function(){
  //(index, start_time, end_time, red, green, blue, action, reviewed)
  var a = new Scene(0,10,80,0,0,0,'keep',false);
  var startTime = a.getStartTime();
  var endTime = a.getEndTime();
  var result = a.getStartEndTime();
  console.log(result);
}

