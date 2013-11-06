// Functions for manipulating the timer for each task.

startTime = 0;
endTime = 0;
time = 0;
allotedTaskTime = 5;
elapsed = 0;
stopped = true;

function startTaskTimer(){
    startTime = new Date().getTime();
    endTime = startTime + allotedTaskTime * (60000);
    elapsed = 0.0;
    time = 0;
    updateTime();
    window.setTimeout(tick, 100);
    stopped = false;
    $("#timer").show();
}

function tick(){
    time += 100;  
    elapsed = Math.floor(time / 100) / 10;  
    if(Math.round(elapsed) == elapsed) { elapsed += '.0'; }  
    var diff = (new Date().getTime() - startTime) - time;  
    updateTime();
    if(!stopped){
        if(new Date().getTime() < endTime){
            window.setTimeout(tick, (100 - diff));
        }else{
            $("#timer").hide();
            stopTask(currentTask);
        }
    }else{
        recordTaskTime();
    }
}

function updateTime(){
    var diff = (endTime-(time+startTime))/60000 ;
    var minutes = Math.floor(diff);
    var seconds = Math.floor((diff - minutes)*60);
    if(seconds < 10){
        seconds = "0"+seconds
    } 
    $("#timer").html(minutes+":"+seconds)
}

function recordTaskTime(){
    tasks[currentTask].time = time;
    $("#timer").html("");
    stopped = true;
}