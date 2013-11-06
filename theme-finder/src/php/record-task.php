<?php
/*****************************************************************************
record-task.php

Records theme finder task performance in the DB.
*****************************************************************************/

include 'dbsetup.php';
include 'util.php';
include "../../config.php";

$instance = array_key_exists("instance", $_GET) ?
			$_GET["instance"]
			: "";

connect($instance);

if (array_key_exists("participant", $_GET)) {
	$participant = $_GET["participant"];
	if ($_GET["type"] == "eval") {
		$task_number = $_GET["task_number"];
		$understanding = $_GET["understanding"];
		$theme_understanding = $_GET["theme_understanding"];
		$performance = $_GET["performance"];
		$difficulty = $_GET["difficulty"];
		$sql = "INSERT IGNORE INTO st_self_evaluation
		(participant_id, task_number, understanding, theme_understanding, 
			performance, difficulty)
		VALUES ('$participant', $task_number, $understanding, $theme_understanding,
			$performance, $difficulty);";
			$result = mysql_query($sql) or die(" Error recording self-evaluation:
				<br>".mysql_error()."
				<br> On query ".$sql."
				<br> at src/php/record-task.php lines 44--50.");
	} else if ($_GET["type"] == "task") {
		$task_number = $_GET["task_number"];
		$interface_type = $_GET["interface_type"];
		$theme_number = $_GET["theme_number"];
		$relevant_sentence_ids = explode(" ", $_GET["relevant_sentence_ids"]);
		
		$time_in_s = $_GET["time_in_s"];
		$number_of_sentences = count($relevant_sentence_ids);
		$sql = "INSERT IGNORE INTO st_task_log
				(participant_id, task_number, interface_type, 
					theme_number, time_in_s, number_of_sentences)
				VALUES ('$participant', $task_number, '$interface_type',
					$theme_number, $time_in_s, $number_of_sentences);";
		$result = mysql_query($sql) or die(" Error recording task: <br>
			".mysql_error()."
			<br> On query ".$sql."
			<br> at src/php/record-task.php lines 27--32.");
		foreach ($relevant_sentence_ids as $sentence_id) {
			$sql = "INSERT IGNORE INTO st_relevant_sentences
			(participant_id, task_number, sentence_id)
			VALUES ('$participant', $task_number, $sentence_id);";
			$result = mysql_query($sql) or die(" Error recording sentences: <br>
				".mysql_error()."
				<br> On query ".$sql."
				<br> at src/php/record-task.php lines 44--50.");
		}
	} else if ($_GET["type"] == "background") {
		$background = $_GET["background"];
		$sql = "INSERT IGNORE INTO st_participant_background
		(participant_id, background)
		VALUES ('$participant', '$background');";
		$result = mysql_query($sql) or die(" Error recording background: <br>
			".mysql_error()."
			<br> On query ".$sql."
			<br> at src/php/record-task.php lines 41--67.");
	}
}
echo json_encode(array("status"=>"ok"));
?>
