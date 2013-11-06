<?php
function indexOf($needle, $haystack) {               
        for ($i=0;$i<count($haystack);$i++) {         
                if ($haystack[$i] == $needle) {       
                        return $i;                                    }
        }
        return -1;
}

function decodePostJson($param) {
	if (array_key_exists($param, $_POST)) {
		$str = str_replace('\\"', '"', $_POST[$param]);
		return json_decode($str, true);
	} else {
		return array();
	}
}


function replaceWeirdCharacters($input){
	$text = str_replace(
	 array("\xe2\x80\x98", "\xe2\x80\x99", "\xe2\x80\x9c", "\xe2\x80\x9d", "\xe2\x80\x93", "\xe2\x80\x94", "\xe2\x80\xa6", "—"),
	 array("'", "'", '"', '"', '-', '--', '...', "-"),
	 $input);
	// Next, replace their Windows-1252 equivalents.
	 $text = str_replace(
	 array(chr(145), chr(146), chr(147), chr(148), chr(150), chr(151), chr(133)),
	 array("'", "'", '"', '"', '-', '--', '...'),
	 $text);
	return $text;
}

function getRelationsFromFormValue($value){
	switch($value){
		case 1:
			return "none";
		case 2:
			return "";
		case 3:
			return "amod advmod";
		case 4:
			return "agent subj nsubj csubj nsubjpass csubjpass";
		case 5:
			return "obj dobj iobj pobj";
		case 6:
			return "prep_because prep_because_of prep_on_account_of prep_owing_to prepc_because prepc_because_of prepc_on_account_of prepc_owing_to";
		case 7:
			return "conj_and";
		case 8:
			return "purpcl";
		case 9:
			return "prep_with prepc_with prep_by_means_of prepc_by_means_of";
		case 9.5:
			return "prep";
		case 10:
			return "prep_to";
		case 11:
			return "prep_from";
		case 12:
			return "prep_of";
		case 13:
			return "prep_on";
		case 14:
			return "prep_by";
		case 15:
			return "prep_in";
		case 16:
			return "poss";
	}
}

function getNameFromRelation($value){
	switch($value){
		case "none":
			return "search";
		case "":
			return "(any relation)";
		case "amod advmod":
			return "described as" ;
		case "agent subj nsubj csubj nsubjpass csubjpass":
			return "done by";
		case "obj dobj iobj pobj":
			return "done to";
		case "prep_because prep_because_of prep_on_account_of prep_owing_to prepc_because prepc_because_of prepc_on_account_of prepc_owing_to":
			return "because";
		case "conj_and":
			return "and";
		case "purpcl":
			return "in order to";
		case "prep_with prepc_with prep_by_means_of prepc_by_means_of":
			return "with";
		case "prep_to":
			return "to";
		case "prep_from":
			return "from";
		case "prep_of":
			return "of";
		case "prep_on":
			return "on";
		case "prep_by":
			return "by";
		case "prep_in":
			return "in";
		case "poss":
			return "possessed by";
	}
}

function remove_spaces_before_punctuation($sentence){
	$no_space_before_punctuation = array(".", ",", "!","`", "\"", "?", "`", "'",";", ")", ":", "—");
	$no_space_after_punctuation = array("`", "'", "\"", "`", "`", "(", "—");
	
	$sent = replaceWeirdCharacters($sentence);
	foreach($no_space_before_punctuation as $mark){
		$sent = str_replace(" ".$mark, $mark, $sent);
	}
	foreach($no_space_after_punctuation as $mark){
		$sent = str_replace($mark." ", $mark, $sent);
	}
	return $sent;
}

function getWordsInSentence($sentenceID){
	$sql = "SELECT surface, word_id 
		from sentence_xref_word 
		WHERE sentence_id = ".$sentenceID."
		ORDER BY position ASC;";
	$result = mysql_query($sql);
	$words = array();
	while($row = mysql_fetch_array($result)){
		$word = array('word'=>replaceWeirdCharacters($row['surface']), 'id'=>$row['word_id']);
		array_push($words, $word);
	}
	return $words;
}

function startsWith($haystack, $needle)
{
    $length = strlen($needle);
    return (substr($haystack, 0, $length) === $needle);
}

function endsWith($haystack, $needle)
{
    $length = strlen($needle);
    $start  = $length * -1; //negative
    return (substr($haystack, $start) === $needle);
}

function spaceBetweenWords($word1, $word2){
	$prev = substr($word1, -1);
	$next = substr($word2, 0, 1);
	$alphabet = "abcdefghijklmnopqrstuvwxyz&1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ";
	$no_space_before=".!,`)?;:%\"'";
	$no_space_after='\'"`(';
	if(strpos($alphabet, $prev)){
		if(strstr($no_space_before, $next)){
			return '';
		}else{
			return ' ';
		}
	}else if(strstr($no_space_after, $prev)){
		return '';
	}else{
		return ' ';
	}	
}

/** gets the sentence ids that are within a particular chapter or section**/
function getSentenceIDsInUnit($unitID, $type){
	$query = "SELECT sentence.id from ".$type.", sentence
	WHERE ".$type.".id = ".$unitID."
	AND ".$type.".narrative_id = sentence.narrative_id
	AND ".$type.".number = ".$type."_number;";
	$result = mysql_query($query) or die("<b>Fatal MySQL error</b>
	<br/> Query: ". $query ."
	<br/> Error: (".mysql_errno().") ".mysql_error());
	$ids = array();
	while($row = mysql_fetch_assoc($result)){
		array_push($ids, $row['id']);
	}
	return join(", ", $ids);
}

function getSectionID($narrativeID, $sectionNumber){
	$q = "SELECT id from section where narrative_id = ".$narrativeID." AND number = ".$sectionNumber.";";
	$result = mysql_query($q);
	$row = mysql_fetch_array($result);
	return $row['id'];
}

function getSectionStartSentence($narrativeID, $sectionNumber){
	$q = "SELECT MIN(id) as id from sentence where narrative_id = ".$narrativeID." AND section_number = ".$sectionNumber.";";
	$result = mysql_query($q);
	$row = mysql_fetch_array($result);
	return $row['id'];
}

function getSectionTitle($narrativeID, $sectionNumber){
	$q = "SELECT title from section where narrative_id = ".$narrativeID." AND number = ".$sectionNumber.";";
	$result = mysql_query($q);
	$row = mysql_fetch_array($result);
	return $row['title'];
}

function getChapterID($narrativeID, $chapterNumber){
	$q = "SELECT id from chapter where narrative_id = ".$narrativeID." AND number = ".$chapterNumber.";";
	$result = mysql_query($q);
	$row = mysql_fetch_array($result);
	return $row['id'];
}

function getChapterStartSentence($narrativeID, $chapterNumber){
	$q = "SELECT MIN(id) as id from sentence where narrative_id = ".$narrativeID." AND chapter_number = ".$chapterNumber.";";
	$result = mysql_query($q);
	$row = mysql_fetch_array($result);
	return $row['id'];
}

function getChapterTitle($narrativeID, $chapterNumber){
	$q = "SELECT title from chapter where narrative_id = ".$narrativeID." AND number = ".$chapterNumber.";";
	$result = mysql_query($q);
	$row = mysql_fetch_array($result);
	return $row['title'];
}

function getTitle($idParam){
	$components = explode("_", $idParam);
	$id = $components[0];
	$sql = "SELECT title from narrative WHERE id = ".$id.";";
	$result = mysql_query($sql);
	$row = mysql_fetch_array($result);
	return $row['title'];
}

function getGetParam($param) {
	if(array_key_exists($param, $_GET)){
		return mysql_real_escape_string($_GET[$param]);
	} else {
		return "";
	}
}
?>