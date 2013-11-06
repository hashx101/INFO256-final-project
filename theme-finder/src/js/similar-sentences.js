/**similar-sentences.js
Front end for similar sentences exploration

local storage contains the current query
**/


lastAction = "";
/** Reset the query vector and lists of relevant and irrelevant words **/
function reset(){
    $(".relevance-feedback-search-results").hide();
    $(".feedback").hide();
    relevant = [];
    irrelevant = [];
    sentence_relevance = {};
    updateVectorQuery(undefined, getCurrentVectorQuery());
    $(".relevant-table").html("");
    $(".irrelevant-table").html("");
    displayResults("");
    $("div.task"+currentTask).find(".refine-results").hide();
}

/***************************************
Asking the server to process a new query
****************************************/

/**submit a search query (as opposed to relevance feedback)**/
function sendSearchQuery(){
    lastAction = "search";
    if(!stopped){
        data = {};
        data['instance'] = collection;
        data['string_query'] = 'true';
        data['vector_query'] = 'false';
        query = $("div.task"+currentTask).find('input[name="query"]').val();
        data['query'] = query;
        data['vector_query'] = JSON.stringify(getCurrentVectorQuery());
        $(".relevance-feedback-search-results").show();
        $(".relevance-feedback-search-results").html("Loading...");
        $.post("src/php/similarsentences/similarsentences.php",
        data,
        handleResults);
    } else {
        startTimedTask(currentTask);
        sendSearchQuery();
    }
    logActivity({
        instance:collection,
        participant: getParticipant(),
        task_number: currentTask,
        activity: "search",
        search_query: query,
        num_relevant : -1,
        num_irrelevant: -1,
    })
}

/* ask server to refine results based on the marked sentences*/
function refineResults(){
    if(!stopped){
        data = {};
        data['instance'] = collection;
        if(tasks[currentTask].interface_type == "relevance-feedback"){
            data['string_query'] = 'false';
            data['vector_query'] = 'true';
            data['query'] = JSON.stringify(getCurrentVectorQuery());
            data['relevant'] = JSON.stringify(relevant);
            data['irrelevant'] = JSON.stringify(irrelevant);
        } else if(tasks[currentTask].interface_type == "relevance-control") {
            data['string_query'] = 'true';
            data['vector_query'] = 'false';
            data['query'] = query;
        }
        $(".relevance-feedback-search-results").html("Loading...");
        $.post("src/php/similarsentences/similarsentences.php",
        data,
        handleResults);
        lastAction = "refine";
    } else {
        startTimedTask(currentTask);
        refineResults();
    }
    logActivity({
        instance:collection,
        participant: getParticipant(),
        task_number: currentTask,
        activity: "relevance-feedback",
        search_query: "",
        num_relevant : relevant.length,
        num_irrelevant: irrelevant.length,
    })
}

/* ask server to refine results based on the marked sentences
 but do not display the results*/
function refineVectorQuery(){
    data = {};
    data['instance'] = collection;
    if(tasks[currentTask].interface_type == "relevance-feedback"){
        data['string_query'] = 'false';
        data['vector_query'] = 'true';
        data['query'] = JSON.stringify(getCurrentVectorQuery());
        data['relevant'] = JSON.stringify(relevant);
        data['irrelevant'] = JSON.stringify(irrelevant);
    }
    $.post("src/php/similarsentences/similarsentences.php",
    data,
    handleRefineVectorQuery);
}

function logActivity(data) {
    if(log){
    console.log("logging activity");
    $.getJSON("src/php/log-activity.php", data, function(){
        var string = JSON.stringify(data)
        console.log("Logged :\n"+string);
    })
   }
}

/** handle results from the server -- wrapper**/
function handleResults(d){
    var data = $.parseJSON(d);
    if(tasks[currentTask].interface_type == "relevance-feedback"){
        currentQuery = getCurrentVectorQuery();
        updateVectorQuery(data.query, currentQuery);
    }
    if(lastAction == "refine"){
        displayResults(data.sentences);
    }else{
        refineResults();
    }
}

/** update the vector query**/
function handleRefineVectorQuery(d){
    var data = $.parseJSON(d);
    if(tasks[currentTask].interface_type == "relevance-feedback"){
        currentQuery = getCurrentVectorQuery();
        updateVectorQuery(data.query, currentQuery);
    }
}

/* update stored values to reflect the state of sentence and word relevance */
function updateStoredValues(){
    relevant = [];
    irrelevant = [];
    for(id in sentence_relevance){
        if(sentence_relevance[id] > 0){
            relevant.push(id);
        }else if(sentence_relevance[id] < 0){
            irrelevant.push(id);
        }
    }
}


/******************************************
Refining results based on Relevant/Irrelevant Sentences
******************************************/

/** get the current vector query **/
function getCurrentVectorQuery(){
    queryString = localStorage.getItem("current-vector-query");
    if(queryString != 'undefined'){
        return $.parseJSON(queryString);
    }else{
        return {'features':{}, 'relevant':[], 'irrelevant':[]};
    }
}

/** update the vector query in local storage **/
function updateVectorQuery(query, previous){
    if(previous != ""){
        previousQuery = localStorage.getItem("previous-similarity-vector-query")
        previousQuery = $.parseJSON(previousQuery);
        previousQuery.push(previous);	localStorage.setItem("previous-similarity-vector-query",JSON.stringify(previousQuery))
    }
    localStorage.setItem("current-vector-query", JSON.stringify(query));
}

/***************************************
Display Search results
*************************************/
function displayResults(sentences){
    var html = "<h3>"
    html += (sentences.length == 1)?
    "1 result"
    : (sentences.length < 200)?
    sentences.length+" results"
    : "Top "+sentences.length+" results";
    html += '</h3>';
    html += '<table class="searchresults" id="relevance-feedback-sentence-results"><tr>'
    // html += '<td class="title header">Title</td>';
    html += '<td class="sentence header">Sentence</td>';
    html += '<td class="mark-relevance-feedback header">';
    html += '<p class="feedback-label">Not relevant</p></td>';
    html += '<td class="mark-relevance-feedback header"><p class="feedback-label">Neutral</p>';
    html += '</td><td class="mark-relevance-feedback header"><p class="feedback-label">Relevant</p>';
    html += '</td></tr>';
    var randomly_permuted = [];
    if(tasks[currentTask].interface_type == "relevance-control"){
        randomly_permuted = permuteIndices(sentences.length);
    }
    for(i = 0; i < sentences.length; i++){
        sentence = sentences[i];
        if(tasks[currentTask].interface_type == "relevance-control"){
            sentence = sentences[randomly_permuted[i]];
        }
        if(sentence_relevance[sentence.id] != -1
            && sentence_relevance[sentence.id] != 1){
            // only show relevant or neutral sentences
            html += '<tr class="search-result-row">';
            // html += '<td class="title">'+sentence.title+"</td>";
            html += '<td class="sentence"><span class="sentence" sentence-id="'+sentence.id+'">';
            for(j = 0; j < sentence.words.length; j++){
                var word = sentence.words[j];
                var previousWord = "'";
                if(j > 0) previousWord = sentence.words[j-1].word;
                var space = spaceBetweenWords(previousWord, word.word);
                html += space+'<span class="word" sentence-id="'+sentence.id+'" word-id="'+word.id+'">'
                var highlightClassNumber = shouldBeHighlighted(word.word);
                if(highlightClassNumber != -1){
                    html += '<span class="highlight'+(highlightClassNumber%6);
                    html += '">'+word.word+"</span>";
                }else{
                    html += word.word
                }
                html += "</span>";
            }
            html +="</td>";
            html += '<td class="mark-relevance-feedback">'
            html +='<input value = "-1" function="feedback" type="radio" ';
            html += 'name="'+sentence.id+'"';
            html += ' class="relevance-feedback"></input></td>';
            html += '<td class="mark-relevance-feedback">'
            html += '<input value = "0" function="feedback" type="radio" name="'+sentence.id+'" class="relevance-feedback"></input></td>'
            html += '<td class="mark-relevance-feedback">'
            html += '<input value = "1" function="feedback" type="radio" name="'+sentence.id+'" class="relevance-feedback"></input></td>';
            html += '</tr>'
        }
    }
    html += "</table>"
    if(tasks[currentTask].interface_type == "relevance-control"){
        setTimeout(function(){
            makeResultsVisible(html);
        }, 1000)
    }else{
        makeResultsVisible(html);
    }
}

function makeResultsVisible(html){
    $(".relevance-feedback-search-results").html("");
    $("div.task.task"+currentTask+" > .relevance-feedback-search-results").html(html);
    $('input[function="feedback"][value="0"]').prop("checked", true);
    // mark pre-existing relevant and not-relevant ones
    $('input[function="feedback"]').each(function(){
        var radio = $(this);
        var id = radio.attr("name");
        if(id in sentence_relevance){
            if(radio.val() == sentence_relevance[id]){
                radio.prop("checked", true);
            }
        }
    })
    $('input[function="feedback"]').click(feedback);
    $(".relevance-feedback-search-results").show();
}

function shouldBeHighlighted(word){
    var matched = -1;
    var query_words = query.replace(/\"/g, "").split(" ");
    for (var i = 0; i < query_words.length; i++){
        var query_word = query_words[i];
        re = new RegExp(" "+query_word+" ", "i");
        if(re.test(" "+word+" ")){
            matched = i;
        }
    }
    return matched;
}

/***************************************
Refining results
****************************************/

/** handle the selecting or unselecting of a feedback checkbox **/
function feedback(){
    var radio = $(this);
    var value = radio.val();
    var id = radio.attr("name");
    if(value == 1){
        relevance = "relevant"
    }else if(value == -1){
        relevance = "irrelevant"
    }else if(value == 0){
        relevance = "neutral"
    }
    if(radio.is(":checked")){
        sentence_relevance[id] = value;
        removeSentence(id)
        addSentence(relevance, id, 'none')
    }else{
        sentence_relevance[id] = 0;
        removeSentence(id)
    }
    updateStoredValues();
    if(relevant.length + irrelevant.length > 0){
        $("div.task"+currentTask).find(".refine-results").show();
    }else{
        $("div.task"+currentTask).find(".refine-results").hide();
    }
}

/** updates the user's view of what is relevant **/
function addSentence(relevance, id, sent){
    if(relevance == "relevant" || relevance == "irrelevant"){
        tableID = ".relevant-table"
        if(relevance == "irrelevant"){
            tableID = ".irrelevant-table";
        }
        sentence = sent=='none'? $('span[sentence-id="'+id+'"]').html():sent;
        var html = '<tr relevance="'+relevance+'" sentence-id="'+id+'">';
        html +='<td><img src="img/close.png" class="button close remove-feedback"></img></td>';
        html +='<td><span class="sentence" sentence-id="'+id+'">'+sentence+"</span></td>";
        html +="</tr>";
        $("div.task.task"+currentTask+"> .feedback").find(tableID).append(html);
    }
	$("div.task.task"+currentTask+"> .feedback").find(tableID).show();
    $("img.remove-feedback").click(removeFeedback);
	console.log("added :"+sent);
}


/* remove a sentence from all the tables in which it appears,
usually a precursor to adding it back to one table */
function removeSentence(id){
    $(".relevant-table").find('tr[sentence-id="'+id+'"]').remove()
    $(".irrelevant-table").find('tr[sentence-id="'+id+'"]').remove()
}

/* what to do when the user removes a relevant/irrelevant sentence*/
function removeFeedback(){
    var id = $(this).closest("tr").attr("sentence-id");
    $(this).closest("tr").remove();
    sentence_relevance[id] = 0;
    $('input[name="'+id+'"]').prop("checked", false);
    $('input[name="'+id+'"][value="0"]').prop("checked", true);
    updateStoredValues();
    if(relevant.length + irrelevant.length > 0){
        $("div.task"+currentTask).find(".refine-results").show();
    }else{
        $("div.task"+currentTask).find(".refine-results").hide();
    }
}
