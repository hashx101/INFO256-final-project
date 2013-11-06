<?php

function connect($instance){
	if($instance == "personals"){
		$user="wordseer_e";     # DB username
		$password="wordseer"; # DB password.
		$database="wordseer_e"; # DB schema
	}
	if($instance == "shakespeare"){
		$user="wordseer_a";     # DB username
		$password="your password here"; # DB password.
		$database="wordseer_a"; # DB schema
	}
	mysql_connect('localhost',$user,$password) or die (mysql_error());
	mysql_select_db($database) or die( "Unable to connect: ".mysql_error());
	return $database;
}

?>
