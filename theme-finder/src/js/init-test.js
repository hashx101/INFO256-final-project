function init(){
    log = false;
    stopped = false;
    currentTask = 0;
    tasks = [{interface_type:'relevance-feedback'}];
    //interactions
    collection = $('select[name="collection"]').val();
    $("select[name='collection']").change(function() {
	    collection = $(this).val();
	    reset();
	})
	$(".accordion-head").click(function(){
	    $(this).next().toggle();
	});	
	$("#task").css("margin-bottom", "0px");
	// send either search query or vector query depending on the query type.
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
	$("div.feedback").hide();
}

function getParticipant() {
    return -1;
}