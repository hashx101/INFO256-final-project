<!DOCTYPE html>
<html>
<head>
	<title>Activity Log: Theme finder usability study </title>
	<link rel="stylesheet" href="style/similar-sentences.css">
</head>
<body>
		<?php
		include "config.php";
		$instance = array_key_exists("instance", $_GET) ?
					$_GET["instance"]
					: "";
		connect($instance);
		$sql = "SELECT COUNT(DISTINCT participant_id) as num_participants
		FROM st_participant_background;";
		$result = mysql_query($sql) or die(mysql_error()."
		<br> getting number of participants");
		$row = mysql_fetch_assoc($result);
		echo '<p> Number of participants <br>'.$row["num_participants"]."</p>";
		echo '<br>';
		$sql  = "SELECT a.participant_id, t.interface_type, a.activity,
		 		a.search_query, a.num_relevant, a.num_irrelevant
		 		FROM st_activity_log as a, st_task_log as t
		 		WHERE a.participant_id = t.participant_id
				AND a.task_number = t.task_number
				ORDER BY a.id desc;";
		$result = mysql_query($sql) or die(mysql_error()."
			<br> getting activity log");	
		echo '<table>';		
		while($row = mysql_fetch_assoc($result)){
			$participant = $row["participant_id"];
			$interface_type = $row["interface_type"];
			$activity = $row["activity"];
			$search_query = $row["search_query"];
			$num_relevant = $row["num_relevant"];
			$num_irrelevant = $row["num_irrelevant"];
			
			
			echo "<tr>
				<td> $participant </td>
				<td> $interface_type </td>
				<td> $activity </td>
				<td> $search_query </td>
				<td> $num_relevant </td>
				<td> $num_irrelevant </td>
				</tr>";
		}
		echo '</table>';
		?>
</body>
</html>