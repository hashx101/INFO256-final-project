/** Code for viewing the results of the theme-finder interface **/

instance = "";
function init(inst){
    instance = inst;
    getResults();
}

function getResults(){
    $.getJSON("src/php/show-results.php", {instance:instance}, showResults);
}

function showResults(data){
    for(var i = 2; i < 3; i++){
        theme_sentences = data[i+" "];
        html = "<div theme='"+i+"'>"
        html += "<h2>"+TASK_PARAMS.themes[instance][i].title +"</h2>";
        html += "<table style='width:1000px'>"
        html += "<tr class='header'>";
        html += "<td>Play</td><td>Sentence</td><td>Wrong Theme</td><td>Not Relevant</td><td>Slightly Relevant</td><td> Very Relevant</td>"
        html += "</tr>"
        for(var k = 0; k < theme_sentences.length; k++){
            var sentence = theme_sentences[k].sentence;
            var id = theme_sentences[k].id;
            var title = theme_sentences[k].title;
            html += "<tr>";
            html += "<td style='width:200px'>"+title+"</td>";
            html += "<td>";
            for(j = 0; j < sentence.length; j++){
                var word = sentence[j];
                var previousWord = "'";
                if(j > 0) previousWord = sentence[j-1].word;
                var space = spaceBetweenWords(previousWord, word.word);
                html += (space + word.word);
            }
            html += "</td>";
            html += '<td><input type="radio" theme="'+i+'" value="-1" name="'+i+','+id+'"></td>';
            html += '<td><input type="radio" theme="'+i+'" value="0" name="'+i+','+id+'"></td>';
            html += '<td><input type="radio" theme="'+i+'" value="1" name="'+i+','+id+'"></td>';
            html += '<td><input type="radio" theme="'+i+'" value="2" name="'+i+','+id+'"></td>';
            html += "</tr>"
        }
        html += "</table>"
        html += '<br><button class="submit">Submit</button>';
        html += "</div>"
        $('body').append(html);
        $("button.submit").click(submitRatings);
    }
}

function submitRatings(){
    var ratings = [];
    $(this).parent().find("input[type='radio']:checked").each(function(){
        var name = $(this).attr("name");
        var value = $(this).val();
        ratings.push(name+","+value);
    })
    $.post("src/php/record-expert-feedback.php",
        {instance: instance, ratings:ratings.join(" ")},
        function(){
            alert("Thanks Michael!");
            $("body").html("")
        })
}