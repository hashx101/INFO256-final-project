<?php
include 'dbsetup.php';
include 'util.php';
include "../../config.php";

$instance = array_key_exists("instance", $_GET) ?
			$_GET["instance"]
			: "";

connect($instance);

getSentences();

function getSentences(){
	$results = array();
	for($i = 0; $i < 3; $i++){
		$results[$i." "] = getThemeSentences($i);
	}
	echo json_encode($results);
}

function getThemeSentences($theme_number){
	$sql = "SELECT distinct sentence_id, sentence, title
	FROM st_relevant_sentences as relevant,
	st_task_log as tasks,
	sentence, narrative
	WHERE tasks.participant_id = relevant.participant_id
	AND tasks.task_number = relevant.task_number
	AND tasks.theme_number = $theme_number
	AND relevant.sentence_id = sentence.id
	AND sentence.narrative_id = narrative.id;";
	
	$result = mysql_query($sql) or die( mysql_error()."Error getting
	sentences
	<br> on query $sql
	<br> at show-results.php lines 20--27.");
	
	$sentences = array();
	while ($row = mysql_fetch_assoc($result)){
		$id =  $row['sentence_id'];
		$sentence = array("id"=>$id, 
						"sentence"=>getWordsInSentence($id),
						"title"=>utf8_encode($row["title"]));
		$sql = "SELECT count(*) as c from st_expert_scores 
		WHERE sentence_id = $id;";
		$res = mysql_query($sql) or die(myqsl_error()."
		<br> on $sql
		<br> at show-results.php l. 42");
		$r = mysql_fetch_assoc($res);
		if($r["c"] == 0){
			array_push($sentences, $sentence);
		}
	}
	return $sentences; 
}
?>