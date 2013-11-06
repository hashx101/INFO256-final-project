function init(){
    log = false;
    populated = false;
    currentTask = -1;
    numTasks = 1;
    collection = false;
    tasks = [{}, {}, {}];
    explanations = {
        search : "",
        relevance : "",
        general : "",
    }
    instructionsVisible = false;
    //interactions
	$(".accordion-head").click(function(){
	    $(this).next().toggle();
	});	
	$("#task").css("margin-bottom", "0px");
	// send either search query or vector query depending 
    // on the query type.
    $('.search').click(function(){
        sendSearchQuery();
    })
    $("input[name='query']").keypress(function(e){
          if(e.which == 13){
            sendSearchQuery();
           }
          });
    $('.reset').click(function(){
        reset();
    })
    $(".refine-results").click(function(){
        refineResults();
	});	
	relevant = [];
	irrelevant = [];
	sentence_relevance = {};
	localStorage.setItem("previous-similarity-vector-query","[]");
	localStorage.setItem("current-vector-query", 'undefined');
    $(".feedback").hide();
    $("div.pane").hide();
    $("#no-double-participation").hide();
    $.get("study/search.html", {}, function(data){
        explanations.search = data;
        $.get("study/relevance-feedback.html", {}, function(data){
                explanations.relevance = data;
                $.get("study/general-explanation.html", {}, function(data){
                        explanations.general = data;
                        if(!makeParticipant()){                
                    	    resumeParticipation();
                    	}else{
                    	    localStorage.setItem("currentState", "introduction");
                    	    startTasks();
                    	}
                    }, "text");
            }, "text");
        }, "text");
    $("#timer").hide();
}


function makeParticipant(){
    var id = new Date().getTime();
    id += "-"+Math.floor(Math.random()*9);
    if(localStorage.getItem("participant")){
        return false;
    }else{
        localStorage.setItem("participant", id);
        return true;
    }
}

function getParticipant(){
    return localStorage.getItem("participant");
}

function resumeParticipation(){
    currentTask = parseInt(localStorage.getItem("current-task"));
    var currentState = localStorage.getItem("current-state");
    if(localStorage.getItem("configured") != "true"){
        configureTasks();
    } else {
        tasks = $.parseJSON(localStorage.getItem("tasks"));
        collection= localStorage.getItem("collection");
        populateHTMLFromTasks();
        bindEvents();
    }
    if (currentState == "introduction") {
        startTasks();
    } else if (currentState == "not-started-task") {
        startTask(currentTask);
    } else if (currentState == "task"){
        startTask(currentTask);
    } else if (currentState == "eval") {
        stopTask(currentTask);
    } else if (currentState == "done") {
        disallowParticipation();
    } else {
        startTasks();
    }
}
function disallowParticipation(){
    $("#timer").hide();
    $("#tasks").hide()
    $("#introduction").hide();
    $("#no-double-participation").show();
}



function startTasks(){
    $("#introduction").show();
    configureTasks();
    populateHTMLFromTasks();
    bindEvents();
}

function configureTasks(){
    collection = chooseRandomlyFrom(TASK_PARAMS.collections);
    var interface_order = chooseRandomlyFrom(TASK_PARAMS.interface_orders);
    var theme_order = chooseRandomlyFrom(TASK_PARAMS.theme_orders);
    for(var i = 0; i < numTasks; i++){
        tasks[i] = {
            collection: collection,
            interface_type: TASK_PARAMS.interfaces[interface_order[i]],
            theme: TASK_PARAMS.themes[collection][theme_order[i]],            
        };      
    }
    localStorage.setItem("tasks", JSON.stringify(tasks));
    localStorage.setItem("configured", "true"); 
    localStorage.setItem("collection", collection);
};

function populateHTMLFromTasks(){
    if(!populated){
    for (var i = 0; i < numTasks; i++) {
        var elementID = "div.task"+i;
        var explanation = explanations.relevance;
        if(tasks[i].interface_type == "search"){
            $(elementID).find("input.refine-results").remove();
            explanation = explanations.search;
        }
        explanation += explanations.general;
        var html = "<h1> System "+(i+1) + "</h1>";
        html += explanation;
        $(elementID+".explanation").html(html);
        $(elementID+".explanation").attr("title", "Instructions");
        $(elementID+".explanation").attr("task", elementID);
        $(elementID+".explanation").dialog({
                autoOpen:false,
                height:500,
                width: 530,
                position:[500, 10],
                close: function(){
                    hideInstructions();
                },
                open: function(){
                    showInstructions();
                }
            });
        $(elementID+".task").prepend("<h1 class='collection'> Search " +             
                                             collection +"'s works.</h1>");
        $(elementID).find("div.header").prepend("<button class='show-instructions'> Show instructions </button>");
        $(elementID).find("div.header").append('<p><button class="start-task'+i+'">Start Task</button></p>');
        $(elementID).find("button.show-instructions").attr("task", elementID);
        $(elementID).find("button.show-instructions").click(function(){
            var task = $(this).attr("task");
            instructionsVisible ? hideInstructions(task) 
                                : showInstructions(task);
        })
        $(elementID).find("p.theme-name").html(tasks[i].theme.title);
        $(elementID).find("p.theme-example.1").html(
            "<h5>Example 1</h5>"+tasks[i].theme.example_0.replace(/<br>/g, " "));
        $(elementID).find("p.theme-example.2").html(
            "<h5>Example 2</h5>"+tasks[i].theme.example_1.replace(/<br>/g, " "));
    }
    populated = true;
    }
}

function bindEvents(){
    $("button.start-first").click(function(){
        startTask(0);
    });
    $("button.start-task0").click(function(){
        startTimedTask(0);
    });
    $("button.done-with-first").click(function(){
        stopTask(0);
    });
    $("button.finish").click(function(){
        if(allEvalFilledIn()){
            sendEvalResults();
            $("div.sequence").hide();
            localStorage.setItem("current-state", "done");
            disallowParticipation();
        } 
    });
}

function startTask(n){
    okToStart = true;
    if(n > 0){
        if(allEvalFilledIn()){
            sendEvalResults();
        } else {
            okToStart = false;
        }
    } else {
        sendBackground();
        $("#introduction").hide();
    }
    if(okToStart){
        currentTask = n;
	    reset();
        console.log("Started task "+n);
        console.log("With parameters "+JSON.stringify(tasks[n]));
        $("#tasks").show();
        $("div.sequence").hide();
        $("div.explanation.task"+n).dialog('open');
        instructionsVisible = true;
        $("div.eval.task"+n).hide();
        $("div.task.task"+n).show();
        currentTask = n;
        $("#timer").hide();
        localStorage.setItem("current-state", "not-started-task")
        localStorage.setItem("current-task", n);
		relevant = tasks[currentTask].theme.relevant_ids;
		irrelevant = [];
		for(var i = 0; i < relevant.length; i++){
			sentence_relevance[relevant[i]] = 1;
			addSentence("relevant", relevant[i], 
				tasks[currentTask].theme["example_"+i]);
			$("div.task"+currentTask).find(".feedback").show();
		}
		if(tasks[currentTask].interface_type == "relevance-feedback"){
			refineVectorQuery();
		}
    }
}

function allEvalFilledIn(){
    var elementID = "div.eval.task"+currentTask;
    var allFilledIn = ($(elementID).find(
                    "input[name='understanding']:checked").length > 0)
                    && ($(elementID).find(
                    "input[name='theme-understanding']:checked").length > 0)
                    && ($(elementID).find(
                        "input[name='performance']:checked").length > 0)
                    && ($(elementID).find(
                        "input[name='difficulty']:checked").length > 0);
    if(!allFilledIn){
        alert("Please fill in all responses");
    }
    return allFilledIn;
}

function startTimedTask(n){
    query = "";
    $("#tasks").show();
    $("div.sequence").hide();
    $("div.task.task"+n).show();
    $("div.eval.task"+n).hide();    
    hideInstructions("div.task"+n);
    $("button.start-task"+n).remove();
    $("p.instructions-introduction"+n).remove();
    console.log(n);
    startTaskTimer();
    localStorage.setItem("current-state", "task");
}

function stopTask(n){
    $("#tasks").show();
    $("#timer").hide();
    $("div.explanation.task"+n).dialog('close');
    $("div.sequence").hide();
    $("div.task"+n+".eval").show();
    recordTaskTime();
    sendTaskResults();
    reset();
    localStorage.setItem("current-state", "eval");
}

function chooseRandomlyFrom(arr){
    var index = Math.floor(Math.random()*arr.length);
    return arr[index];
}

function showInstructions(taskElementID){
    $(taskElementID+".explanation").dialog("open");
    instructionsVisible = true;
    $(taskElementID).find("button.show-instructions").text( 
        "Hide instructions.");
}

function hideInstructions(taskElementID){
    $(taskElementID+".explanation").dialog("close");
    instructionsVisible = false;
    $(taskElementID).find("button.show-instructions").text( 
        "Show instructions.");
}

function sendBackground(){
   if(log){
    var data = {
       participant : getParticipant(),
       instance : collection,
       type : "background",
       background : $("select[name='background']").val()
   }
   $.getJSON("src/php/record-task.php", data, function(response){
       if(response.status == "ok"){
           console.log("Background "+currentTask+" recorded.");
       } else {
           console.log("Failed to record background");
       }
   }) 
  }
}

function sendTaskResults(){
    if(log){
        updateStoredValues()
        var data = {
           participant : getParticipant(),
           instance : collection,
           type : "task",
           task_number : currentTask,
           interface_type : tasks[currentTask].interface_type,
           theme_number : tasks[currentTask].theme.number,
           relevant_sentence_ids : relevant.join(" "),
           time_in_s : Math.floor(tasks[currentTask].time/1000),
       }
       $.getJSON("src/php/record-task.php", data, function(response){
           if(response.status == "ok"){
               console.log("Sentences from task "+currentTask+" recorded.");
           } else {
               console.log("Failed to record sentences from task "+currentTask);
           }
       })
       logActivity({
              instance:collection,
              participant: getParticipant(),
              task_number: currentTask,
              activity: "submit",
              search_query: "",
              num_relevant: relevant.length,
              num_irrelevant: -1,
          })
  }
}

function sendEvalResults(){
    if(log){
    var data = {
       participant : getParticipant(),
       instance : collection,
       type : "eval",
       task_number : currentTask,
       understanding : $("input[name='understanding']:checked").val(),
       theme_understanding: $("input[name='theme-understanding']:checked").val(),
       performance : $("input[name='performance']:checked").val(),
       difficulty : $("input[name='difficulty']:checked").val(),
   }
   $.getJSON("src/php/record-task.php", data, function(response){
       if(response.status == "ok"){
           console.log("Self-evaluation of task "+currentTask+" recorded.");
       } else {
           console.log("Failed to record sentences from task "+currentTask);
       }
   })
   logActivity({
          instance:collection,
          participant: getParticipant(),
          task_number: currentTask,
          activity: "eval",
          search_query: "u:"+data.understanding+" tu:"+data.theme_understanding     + " p:"+data.performance + " d:" + data.difficulty,
          num_relevant: -1,
          num_irrelevant: -1,
      })
  }
}


