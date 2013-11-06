<?php
include 'dbsetup.php';
include 'util.php';
include "../../config.php";

$instance = array_key_exists("instance", $_GET) ?
			$_GET["instance"]
			: "";

connect($instance);

$participant_id = getGetParam("participant");
$task_number = getGetParam("task_number");
$activity = getGetParam("activity");
$search_query = getGetParam("search_query");
$num_relevant = getGetParam("num_relevant");
$num_irrelevant = getGetParam("num_irrelevant");

$sql = "INSERT INTO st_activity_log
		(participant_id, task_number, activity, search_query, num_relevant,
			num_irrelevant)
		VALUES ('$participant_id', $task_number, '$activity', '$search_query',
			$num_relevant, $num_irrelevant);";
$result = mysql_query($sql) or die(mysql_error()." logging activity
	<br> on query 
	<br> $sql");
	
$status = array("status"=>"ok");
echo json_encode($status);
?>