<?php
include "../../config.php";
 
$instance = "shakespeare";
connect($instance);

$sql = "SELECT count(*) as c from st_expert_scores 
		WHERE theme_number = 2 
		AND is_relevant > 0;";
$result = mysql_query($sql) or die(mysql_error());
$row = mysql_fetch_assoc($result);

$total_very_relevant = $row["c"];

$participants = array();
$info = array();
$sql = "SELECT distinct rs.participant_id, 
			background, 
			time_in_s, 
			interface_type, 
			number_of_sentences as number_of_sentences,
			understanding,
			theme_understanding,
			performance as performance,
			difficulty as difficulty
			
		FROM st_relevant_sentences as rs,
		st_task_log as tl,
		st_self_evaluation as se,
		st_participant_background as background
		WHERE 
		rs.participant_id = background.participant_id
		AND rs.participant_id = se.participant_id
		AND rs.participant_id = tl.participant_id
		AND tl.task_number = 0
		AND tl.interface_type != 'relevance-control'
		AND background != 'no background'
		AND tl.number_of_sentences > 0
		AND tl.theme_number = 2
		;";
$result = mysql_query($sql) or die(mysql_error());
echo "participant_id,background,time_in_s,interface_type,num_sentences,understanding,theme_understanding,performance,difficulty,num_searches,num_refines,num_relevant,recall,precision,num_operations
<br>";
$i = 0;
while($row = mysql_fetch_assoc($result)){
	$i += 1;
	$new = array();
	$id = $row["participant_id"];
	array_push($participants, $id);
	$info[$id] = array_merge($new, $row);
	$sql = "SELECT COUNT(*) as num_searches 
			FROM st_activity_log WHERE participant_id = '$id'
			AND activity = 'search';";
	$r = mysql_query($sql) or die (mysql_error());
	$res = mysql_fetch_assoc($r);
	$info[$id] = array_merge($info[$id], $res);
	
	$sql = "SELECT COUNT(*) as num_refines 
			FROM st_activity_log WHERE participant_id = '$id'
			AND activity = 'relevance-feedback';";
	$r = mysql_query($sql) or die (mysql_error());
	$res = mysql_fetch_assoc($r) or die(mysql_error());
	$info[$id] = array_merge($info[$id], $res);
	if($info[$id]["num_refines"] == 0){
		$info[$id]["interface_type"] = "search";
	}
	$num_very_relevant = 0;
	$num_slightly_relevant = 0;
	$total_score = 0;
	$num_missed = 0;
	$total = 0;
	$sql = "SELECT * from st_relevant_sentences as rs, st_expert_scores as es
			WHERE rs.participant_id = '$id'
			AND es.is_relevant >= 0
			AND rs.sentence_id = es.sentence_id;";
	$r = mysql_query($sql) or die(mysql_error());
	while($res = mysql_fetch_assoc($r)){
		$score = $res["is_relevant"];
		$total_score += $score;
		if($score == 2) {
			$num_very_relevant += 1;
			$num_slightly_relevant += 1;
		} else if ($score == 1) {
			$num_slightly_relevant += 1;
		}
		$total += 1;
	}
	$recall = $total_very_relevant == 0? 0 : $num_slightly_relevant/$total_very_relevant;
	$precision = $total == 0? 0 : $num_slightly_relevant/$total;
	$info[$id]["num_very_relevant"] = $num_very_relevant;
	$info[$id]["num_slightly_relevant"]	= $num_slightly_relevant;
	$info[$id]["recall"] = $recall;
	$info[$id]["precision"] = $precision;
	$participant = $info[$id];
	$arr = array(
		$i,
		$participant["background"],
		$participant["time_in_s"],
		$participant["interface_type"],
		$participant["number_of_sentences"],
		$participant["understanding"],
		$participant["theme_understanding"],
		$participant["performance"],
		$participant["difficulty"],
		$participant["num_searches"],
		$participant["num_refines"],
		$num_slightly_relevant,
		$participant["recall"],
		$participant["precision"],
		$participant["num_searches"] + $participant["num_refines"]
	);
	echo join(",", $arr);
	echo '<br>';
}

//echo json_encode($info);

?>