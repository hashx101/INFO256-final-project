<?php
include 'dbsetup.php';
include 'util.php';
include "../../config.php";

$instance = array_key_exists("instance", $_POST) ?
			$_POST["instance"]
			: "";

connect($instance);

$ratings = explode(" ", $_POST["ratings"]);
foreach($ratings as $rating){
	$components = explode(",", $rating);
	$theme = $components[0];
	$sentence_id = $components[1];
	$rating = $components[2];
	$sql = "INSERT INTO st_expert_scores (theme_number, sentence_id, is_relevant)
		VALUES ($theme, $sentence_id, $rating);";
	$result = mysql_query($sql) or die(mysql_error()."
		<br> on query $sql
		<br> while recording expert scores
		<br> at record-expert-feedback.php line 20.");
}
?>