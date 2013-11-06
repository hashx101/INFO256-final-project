<?php
/** 
Utilities and functions for getting a specific set of sentences
*/
include '../../config.php';
include 'dbsetup.php';
include 'util.php';

/** Returns a the sentence with the given number in the given narrative
*/
function getUnit($unit, $narrative, $number){
	$result  = array();
	
	$tableName = "sentence";
	$field = "sentence";
	$index = "id";
	if($unit =="paragraphs"){
		$tableName = "paragraph";
		$field = "text";
		$index = "start_sentence";
	}
	$query = "SELECT * from ".$tableName." where number <= ".($number+1)." AND number >= ".($number-1)." AND narrative_id =".$narrative.";";
	$results =  mysql_query($query);	
	$sentences = array();
	while($row =  mysql_fetch_array($results)){
		$words = getWordsInSentence($row[$index]);
		$sentences = array_merge($sentences, $words);
	}
	$result['sentence'] = $sentences;
	$query = "SELECT * from ".$tableName." where number = ".$number." AND narrative_id =".$narrative.";";
	$results =  mysql_query($query);	
	$row =  mysql_fetch_array($results);
	$result['sentence_id'] = $row[$index];
	$result['narrative'] = $row['narrative_id'];
	return $result;
}

//if used as a script
if($_GET['narrative']){
	$narrative = $_GET['narrative'];
	$unit = $_GET['unit'];
	$sentenceNumbers = explode(" ", trim($_GET['numbers']));
	$sentences = array();
	foreach($sentenceNumbers as $number){
		$sent = getUnit($unit, $narrative, $number);
		array_push($sentences, $sent);
	}
	echo json_encode($sentences);
}
else if($_GET['ids']){
	$ids = explode(" ", trim($_GET['ids']));
	$sentences = array();
	for($i= 0; $i < count($ids); $i++){
		$html = "";
		$id = $ids[$i];
		$sql = 'SELECT * from sentence_xref_word WHERE sentence_id = '.$id.' order by position ASC;';
		$results = mysql_query($sql) or die('SQL error, getsentence.php line 55.');
		$previous = "'";
		while($row = mysql_fetch_array($results)){
			$word = $row['surface'];
			$wordID = $row['word_id'];
			$sentenceID = $row['sentence_id'];
			$space = spaceBetweenWords($previous, $word);
			$html =  $html.$space.'<span class="word" word-id="'.$wordID.'" sentence-id="'.$sentenceID.'">'.$word.'</span>';
			$previous = $word;
		}
		array_push($sentences, array('id'=>$id, 'sentence'=>$html));
	}
	echo json_encode($sentences);
}
?>
