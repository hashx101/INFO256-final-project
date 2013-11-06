<?php
/*****************************************************************************
similarsentences.php

Calculates a result set of sentences in response to a query using relevance 
feedback, specifically the Rocchio algorithm.

The top-level dispatch procedure works with either a string query,
or with a vector query and a 2 set of sentences: those judged by the user to
be relevant, and non-relevant. In return it always sends back a set of
sentences.

The Rochhio algorithm uses the vector-space model of information retrieval
to refine a query based on relevance feedback.

*****************************************************************************/
include '../dbsetup.php';
include '../util.php';
include 'sparsevector.php';
include '../priorityqueue.php';


$instance = array_key_exists("instance", $_POST) ?
			$_POST["instance"]
			: "";

$database = connect($instance);

/** Algorithm parameters **/
// weight with which query should be adjusted towards relevant sentences
$ALPHA_plus = 0.75;
// weight with which query should be adjusted towards relevant words
$ALPHA_w_plus = 1; // treat like a search term
// weight with which query should be adjusted away from irrelevant sentences 
$ALPHA_minus = 0.25; 
// weight with which query should be adjusged away from irrelevant words
$ALPHA_w_minus = $ALPHA_w_plus*0.1;
// number of returned sentences
$LIMIT = 200;

// Whether or not to include synonyms in the features.
global $expand_to_synonyms;
$expand_to_synonyms = true;

global $include_dependencies;
$include_dependencies = true;

global $include_phrases;
$include_phrases = true;

global $timing;
$timing = true;

/** dispatch procedure

Sends back sentences based on the $_POST data sent by the client.

Arguments:
	-- 'string_query': "true", or "false". "true" indicates that the query is
						a string query, and the query will be interpreted as             		
						such
	-- 'vector_query': "true" or "false". "true" indicates that the query is 
						a vector query, and the query will be interpreted as
						a vector.
	-- 'query':  a String (if string_query is "true"), or (if 'vector_query' 
				is "true") an object containing 
				features:
					a map from from string feature ID's to floating-point 		
					values 
				relevant: a list of relevant sentences represented 
				irrelevant: a list of irrelevant sentences represented
					
	-- 'relevant': a JSON _list_ of integer sentence ID's judged by the user 		
					to be relevant.
	-- 'irrelevant': a JSON _list_ of integer sentence ID's judged by the user 
					to be NOT relevant.

Return values

A JSON response is sent to the client, containing the following data:
	-- sentences : a list of sentences. Where each sentence has an ID, a 	
				  narrativeID, title, date, and a string.
	-- query : a feature-vector representing the current query, to be stored
				by the client and sent back with further query refinements.
{sentences:
	[{
	sentenceID: integer
	sentence: string
	}
	...,
	....]
 vector_query: {featureID: floating-point value, ..., ...}
 relevant: [ the list of sentence ID's incorporated as relevant],
 irrelevant: [ the list of sentence ID's incorporated as irrelevant],
}
**/
dispatch();
function dispatch(){
	$result = array();
	if($_POST['string_query'] == "true"){
		$current_query = decodePostJSON('vector_query');
		$result = process_string_query(
		    mysql_escape_string(strtolower($_POST['query'])), $current_query);
	}else if($_POST['vector_query'] == "true"){
		
		// unpack the sent data
		// unpack sentences
		$relevant_sentences = decodePostJSON('relevant');
		$irrelevant_sentences = decodePostJSON('irrelevant');
		$query = (array) json_decode($_POST['query']);
		$result = process_relevance_feedback($query, 
			$relevant_sentences, $irrelevant_sentences);
	}
	echo json_encode($result);
}

/**Searches for sentences that match the given search query, and returns them
along with a vector representation, which is the string query translated into vector form.

Arguments:
	-- query : the string query typed in by the user, escaped for MYSQL 
	           safety.
Return:
A php array() with the following key-value pairs:
	{sentences:[
	           {id:sentenceID, sentence:string sentence}, 
	           ...]
	query:{featureID:floating-point value, ...}
	}
*/
function process_string_query($query, $old_query){
	global $ALPHA_w_plus; // relevant words weight;
	global $MYSQL_STOPWORDS_LIST; // defined in dbsetup.php
	$old_features =  array_key_exists('features', $old_query)? 
							(array) $old_query['features']
							: array();
	$old_vector_query = new SparseVector($old_features);
	$replaced = str_replace("\\\"", " ", $query);
	$vect_query = convert_query_to_sparse_vector($replaced);
	$vect_query = $vect_query->scalarMultiply($ALPHA_w_plus);
	$new_query = $vect_query->vectorAdd($old_vector_query);
	$new_query->normalize();
	$should_use_fulltext = false;
	if(strstr($query, "\"")){
		$should_use_fulltext = true;
		foreach ($MYSQL_STOPWORDS_LIST as $stop) {
			if(strstr($query, $stop)){
				$should_use_fulltext = false;
			}
		}
	}
	if ($should_use_fulltext) {
		$sentences = retrieve_search_results($query);
	} else {
		$sentences = retrieve_sentences_from_vector_query($new_query);	
	}
	$result = array();
	$result['sentences'] = $sentences;
	$result['query'] = array();
	$result['query']['features'] = $new_query->features;
	$result['query']['relevant'] = array_key_exists('relevant', $old_query)?
									(array) $old_query['relevant']
									: array();
	$result['query']['irrelevant'] = array_key_exists('irrelevant', $old_query)?
										(array)$old_query['irrelevant']
										: array();	
	return $result;
}

/* Convert a string query to a sparse vector by assigning weights to the words in the query, where words are determined by splitting on whitespace. */
function convert_query_to_sparse_vector($query){
	global $STOPS;
	$words = explode(" ", $query);
	$vector = new SparseVector();
	$wordID = -1;
	foreach($words as $word){
		if(strlen($word) > 0){
			$wordIDs = explode(", ", getWordIDsAndPOS($word));
			if(!strstr($STOPS, strtolower($word))){ 
				// stopwords defined in dbsetup.php, line 403
				foreach($wordIDs as $wordID){
					$id = explode("-", $wordID);
					$id = $id[0];
					$pos = explode("-", $wordID);
					$pos = $pos[1];
					if($word == replaceWeirdCharacters($word) && strlen($id) > 0){
						add_search_word_feature($id, $pos, $word, 1, $vector);
					}				
				}
			}
		}
	}
	return $vector;
}

/* get ID's and parts of speech of a surface word */
function getWordIDsAndPOS($word){
	$query = "";
	if(!(strstr($word, "*"))){
		$query = "SELECT pos, id FROM word WHERE word ='".mysql_escape_string(trim($word))."';";	
	}else{
		$query = "SELECT pos, id FROM word WHERE word like '".mysql_escape_string(trim(str_replace("*", "%", $word)))."';";
	}
  $result = mysql_query($query);
  if(mysql_num_rows($result)>0){
    $ids = array();
    while($row =  mysql_fetch_array($result)){
      array_push($ids, $row['id']."-".$row['pos']);
    }
    return join(", ", $ids);
  }else{
    return -1;
  }
}

/* Adds a feature corresponding to a word to a sparse vector*/
function add_word_feature($wordID, $pos, $word, $weight, $vector){
	$features = make_word_feature_names($wordID, $pos, $word);
	foreach($features as $feature_name) {
		$vector->setFeatureValue($feature_name, $weight);
	}
}

/* Adds a feature corresponding to a searched word to a sparse vector*/
function add_search_word_feature($wordID, $pos, $word, $weight, $vector){
	$vector->setFeatureValue(make_search_word_feature_name($wordID, $pos, $word), $weight);
}

/** A top-level wrapper for the relevance feedback computation functions.
 Helper functions fetch sentences by updating the current query to reflect the relevance feedback given by the user.

- convert the irrelevant and relevant sentences into vectors v_+ and v_-
- calculate the new query q' = q + (a_+v_+) - (a_-v_-)
- calculate the sentences that match the new query

Arguments:
	-- query : the (sparse) vector query sent by the client 
	           {featureID:floating-point value, ....}
	-- relevant: a list of sentenceID's marked relevant
	-- irrelevant: a list of sentenceID's marked irrelevant
	
Return:
	A php array() with the following key-value pairs.
	{sentences:[
	           {id:sentenceID, sentence:string sentence}, 
	           ...]
	query:{featureID:floating-point value, ...}
	}
*/
function process_relevance_feedback($query, $relevant, $irrelevant){
	$t1 = time();
	$new_query = calculate_new_vector_query($query, $relevant, $irrelevant);
	$t2 = time();
	if ($timing) {
		echo "<br> Time to calculate new vector query: ".($t2-$t1)."s";
	}
	$sentences = retrieve_sentences_from_vector_query($new_query);
	$t3 = time();
	if ($timing) {
		echo "<br> Time to retrieve new sentences: ".($t3-$t2)."s";
	}
	$result = array();
	$result['sentences']  = $sentences;
	$result['query'] = array();
	$result['query']['features'] = $new_query->features;
	$result['query']['relevant'] = $relevant;
	$result['query']['irrelevant'] = $irrelevant;
	return $result;
}

function calculate_new_vector_query($query, $relevant, $irrelevant){
	$features = (array) $query['features'];
	$vector_query = new SparseVector($features);
	$vector_query->normalize();
	$sentence_adjustment = calculate_sentence_adjustment($query, $vector_query, 
		$relevant, $irrelevant);
	$new_query = $vector_query->vectorAdd($sentence_adjustment);
	$new_query->normalize();
	$new_features = $new_query->features;
	$pruned = prune_features($new_features, $features);
	$pruned_query = new SparseVector($pruned);
	$pruned_query->normalize();
	return $pruned_query;
}


function calculate_sentence_adjustment($query, $vector_query, $relevant, $irrelevant){
	global $ALPHA_plus; // relevant sentences weight
	global $ALPHA_minus; // irrelevant sentences weight
	$already_relevant = (array) $query['relevant'];
	$already_irrelevant = (array) $query['irrelevant'];
	
	$new_relevant = array_subtract($already_relevant, $relevant);
	$no_longer_relevant = array_subtract($relevant, $already_relevant);

	$new_irrelevant = array_subtract($already_irrelevant, $irrelevant);
	$no_longer_irrelevant = array_subtract($irrelevant, $already_irrelevant);
	
	$relevant_vect = convert_sentence_IDs_to_sparse_vector($new_relevant);
	$relevant_vect->normalize();

	$no_longer_relevant_vect = convert_sentence_IDs_to_sparse_vector($no_longer_relevant);
	$no_longer_relevant_vect->normalize();
	
	$irrelevant_vect = convert_sentence_IDs_to_sparse_vector($new_irrelevant);
	$irrelevant_vect->normalize();
	
	$no_longer_irrelevant_vect = convert_sentence_IDs_to_sparse_vector($no_longer_irrelevant);
	$no_longer_irrelevant_vect->normalize();
	
	$positive_adjustment = $relevant_vect->scalarMultiply($ALPHA_plus);
	
	$no_longer_positive_adjustment = $no_longer_relevant_vect->scalarMultiply(-1*$ALPHA_plus);
	
	$negative_adjustment = $irrelevant_vect->scalarMultiply(-1*$ALPHA_minus);
	
	$no_longer_negative_adjustment = $no_longer_irrelevant_vect->scalarMultiply($ALPHA_minus);
	
	$adjustment = $positive_adjustment->vectorAdd($negative_adjustment);
	$adjustment = $adjustment->vectorAdd($no_longer_positive_adjustment);
	$adjustment = $adjustment->vectorAdd($no_longer_negative_adjustment);
	return $adjustment;
}

function array_subtract($to_subtract, $subtract_from){
	$result = array();
	foreach($subtract_from as $item){
		if(!in_array($item, $to_subtract)){
			array_push($result, $item);
		}
	}
	return $result;
}

function array_add($array1, $array2){
	$result = array();
	foreach($array1 as $item){
		array_push($result, $item);
	}
	foreach($array2 as $item){
		array_push($result, $item);
	}
	return $result;
}

/** Takes a set of sentence ID's that indicate relevant or not relevant
sentences and converts it into a feature representation.
*/
function convert_sentence_IDs_to_sparse_vector($sentence_ids){
	global $STOPS;
	global $include_phrases;
	global $include_dependencies;

	$features = array();
	if(count($sentence_ids) > 0){
		$sentence_id_string = join(", ", $sentence_ids);
		// get all the words in these sentence and add them to the feature vector
		$sql = "SELECT * from sentence_word_tf_idf, word
		where sentence_id in (".$sentence_id_string.") and word_id = word.id;";
	$words_in_sentences = mysql_query($sql)
		or die("<b>A fatal MySQL error occured</b>.
		<br/> Query: " . $sql . "
		<br/> Error: (" . mysql_errno() . ") " . mysql_error());
	$word_id = -1;
	$weight = -1;
	// add word features
	while($word_in_sentence = mysql_fetch_array($words_in_sentences)){
		// exclude stopwords and weird characters
		$word = $word_in_sentence['word'];
		if(!strstr($STOPS, strtolower($word)) && $word == replaceWeirdCharacters($word)){ 
			$word_features = make_word_feature_names($word_in_sentence['word_id'], 
				$word_in_sentence['pos'], $word_in_sentence['word']);
			$weight = 1;
			foreach ($word_features as $word_feature) {
				if(array_key_exists($word_feature, $features)){
					$features[$word_feature] += $weight;
				}else{
					$features[$word_feature] = $weight;
				}
			}
		}
	}
	if ($include_dependencies) {
		// Add dependency features
		$sql = "SELECT * from dependency, dependency_xref_sentence 
		WHERE sentence_id in ($sentence_id_string)
		AND dependency.id = dependency_id;";
		$result = mysql_query($sql) or die ("Error getting dependency id's in
			sentences<br> on query 
			$sql
			<br> at similarsentences.php l. 350");
		while ($row = mysql_fetch_assoc($result)) {
			$dependency_id = $row['dependency_id'];
			$gov = $row['gov_id'];
			$dep = $row['dep_id'];
			$relation = $row['relation_id'];
			if (!strstr($STOPS, strtolower($row['gov'])) || 
				!strstr($STOPS, strtolower($row['dep']))) {
				$dep_features = make_dependency_feature_names($dependency_id, 
					$gov, 
					$dep, 
					$relation);
				$weight = 1;
				foreach($dep_features as $dep_feature){
					if(array_key_exists($dep_feature, $features)){
						$features[$dep_feature] += $weight;
					}else{
						$features[$dep_feature] = $weight;
					}
				}	
			}
		}
	}
	}
	// create the vector
	$vector = new SparseVector($features);
	return $vector;
}

function make_dependency_feature_names($dependency_id, $gov, $dep, $rel) {
	global $expand_to_synonyms;

	$features = array();
	// a feature for the whole dependency.
	array_push($features, "d_".$dependency_id."_".$gov."_".$rel."_".$dep);

	// a feature for the pairs.
	array_push($features, "dgd_".$gov."_".$dep);
	array_push($features, "dgr_".$gov."_".$rel);
	array_push($features, "drd_".$rel."_".$dep);
	if ($expand_to_synonyms) {
		$gov_synonyms = get_synonym_ids($gov);
		$dep_synonyms = get_synonym_ids($dep);
		foreach($gov_synonyms as $gov) {
			array_push($features, "dgr_".$gov."_".$rel);
			foreach($dep_synonyms as $dep) {
				array_push($features, "dgd_".$gov."_".$dep);
			}
		}
		foreach ($dep_synonyms as $dep) {
			array_push($features, "drd_".$rel."_".$dep);			
		}
	}

	return $features;
}

/** Return format: an array of numbers, the synonyms of the given word ID. 
*/
function get_synonym_ids($word_id) {
	$sql = "SELECT * from synsets where word1_id = $word_id; ";
	$result = mysql_query($sql) or die("Error getting synset ".mysql_error()."
	 	in
		<br> $sql
		<br> at similarsentences.php l. 433");
	$ids = array();
	while ($row = mysql_fetch_assoc($result)) {
		array_push($ids, $row['word2_id']);
	}
	return $ids;
}


/* Use the vector space model of information retrieval to return sentences
that match a given vector query.

Arguments:
	-- query: a vector query {featureID:floating-point value, ....}

Return:
	A list of N=$LIMIT sentences ordered by best match first
	[{id:sentenceID, sentence:string sentence}, ...] 
*/
function retrieve_sentences_from_vector_query($query){
	global $LIMIT;
	$sentence_scores = array();
	$sentences = array();
	// get sentences that match the word-based features
	$word_ids = array();
	$dependency_ids = array();
	foreach(array_keys($query->features) as $featureID){
		if(is_word_feature($featureID) || is_search_word_feature($featureID)){
			array_push($word_ids, get_id_from_feature_name($featureID));
		}
		if (is_dependency_feature($featureID)) {
			array_push($dependency_ids, get_dependency_id_from_feature_name(
				$featureID));
		}
	}
	// get the word scores
	if(count($word_ids) > 0){
		$string_word_ids = join(", ", $word_ids);
		$score_case = convert_to_case_expression($query->features);
		// no normalization by tf-idf: SUM($score_case)/SUM(1) as score
		// with tf-idf normalization: SUM(tf_idf*$score_case)/SUM(tf_idf) as score
		$sql = "SELECT sentence_id,
		SUM($score_case) as score
		from sentence_word_tf_idf
		WHERE word_id in (".$string_word_ids.")
		GROUP BY sentence_id ORDER BY score desc LIMIT ".$LIMIT.";";
		$words_in_sentences = mysql_query($sql)
				or die("<b>A fatal MySQL error occured</b>.
				<br/> Query: " . $sql . "
				<br/> Error: (" . mysql_errno() . ") " . mysql_error());
		while($scores = mysql_fetch_array($words_in_sentences)){
			if($scores['score'] > 0){
				array_push($sentences, $scores['sentence_id']);
				$sentence_scores[$scores['sentence_id']] =
					$scores['score'];
			}
		}
	}
	// get the dependency scores
	$string_sentence_ids = join(",", $sentences);
	return fetch_top_n_sentences($sentences);
	if (count($dependency_ids) > 0 ) {
		$string_dependency_ids = join(",", $dependency_ids);
		$score_case = convert_to_dependency_case_expression($query->features);
		// no normalization by tf-idf: SUM($score_case)/SUM(1) as score
		// with tf-idf normalization: SUM(tf_idf*$score_case)/SUM(tf_idf) as score
		$sql = "SELECT sentence_id,
		SUM($score_case) as score
		from dependency_xref_sentence
		WHERE sentence_id in ($string_sentence_ids)
		GROUP BY sentence_id ORDER BY score desc LIMIT ".$LIMIT.";";
		$results = mysql_query($sql)
				or die("<b>A fatal MySQL error occured</b>.
				<br/> Query: " . $sql . "
				<br/> Error: (" . mysql_errno() . ") " . mysql_error());
		while($scores = mysql_fetch_array($results)){
			if($scores['score'] > 0){
				$sentence_scores[$scores['sentence_id']] += $scores['score'];
			}
		}
	}
	$sentences = array();
	foreach ($sentence_scores as $sentence) {
		array_push($sentences, array("id"=>$sentence, 
			"score"=>$sentence_scores[$sentence]));
	}
	
	usort($sentences, score_compare);
	$sent_ids = array();
	foreach ($sentences as $sent) {
		array_push ($sent_ids, $sent['id']);
	}
	return fetch_top_n_sentences($sent_ids);
}

function score_compare($a, $b) {
		return $a['score'] > $b['score'] ? 1 : 
			($a['score'] == $b['score']) ? 0 : -1;
}

function convert_to_dependency_case_expression($features){
	$totals = array();
	$when_clauses = array();
	foreach(array_keys($features) as $feature){
		$score = $features[$feature];
		if (is_dependency_feature($feature)) {
			$id = get_dependency_id_from_feature_name($feature);
			if(!array_key_exists($id, $totals)){
				$totals[$id] = 0;
			}
			$totals[$id] += $score;
		} else if (is_dependency_pair_feature($feature)) {
			$components = explode("_", $feature);
			$type = $components[0];
			$id1 = $components[1];
			$id2 = $components[2];
			if ($type == "dgr") {
				array_push($when_clauses,
					" WHEN (gov_id = $id1 AND relation_id = $id2) THEN $score ");
			}
		}
	}
	$sql = "(CASE";
	foreach(array_keys($totals) as $id){
		$score = $totals[$id];
		$sql = $sql." WHEN dependency_id = ".$id." THEN ".$score;
	}
	foreach ($when_clauses as $clause) {
		$sql = $sql . $clause;
	}
	$sql = $sql." ELSE 0 END)";
	return $sql;
}

function convert_to_case_expression($features){
	$totals = array();
	foreach(array_keys($features) as $feature){
		$word_id = get_dependency_id_from_feature_name($feature);
		$score = $features[$feature];
		if(!array_key_exists($word_id, $totals)){
			$totals[$word_id] = 0;
		}
		$totals[$word_id] += $score;
	}
	$sql = "(CASE";
	foreach(array_keys($totals) as $id){
		$score = $totals[$id];
		$sql = $sql." WHEN word_id = ".$id." THEN ".$score;
	}
	$sql = $sql." ELSE 0 END)";
	return $sql;
}

/* Fetches the sentences corresponding to the top N sentence ID's in order.

Arguments:
	-- sentenceIDs: the list of sentence id's to fetch in order
	-- N: the number of sentences to fetch, starting from the beginning of the
		  given list.

Return:
	A list of N sentences ordered by best match first
	[{id:sentenceID, sentence:string sentence, [and other metadata]}, ...]
*/
function fetch_top_n_sentences($top_n){
	global $database;
	$sentences = array();
	if(count($top_n) > 0){
	$top_n_id_string = join(", ", $top_n);

	$sql = "SELECT 
		sentence.id as id, sentence.document_id as narrative_id, sentence, title
	 	from sentence, document 
		WHERE sentence.id in (".$top_n_id_string.")
		AND sentence.document_id = document.id;";
	$sentences_result = mysql_query($sql)
			or die("<b>A fatal MySQL error occured</b>.
			<br/> Query: " . $sql . "
			<br/> Error: (" . mysql_errno() . ") " . mysql_error());
	
	$sentence = array();
	while($sentence_result = mysql_fetch_array($sentences_result)){
		$sentence = array();
		$sentence['id'] = $sentence_result['id'];
		$sentence['words'] = getWordsInSentence($sentence['id']); //util.php
		// ... and whatever other metadata here
		$sentence['narrative_id'] = $sentence_result['narrative_id'];
		$sentence['title'] = $sentence_result['title'];
		// store the information
		if(count($sentence['words']) > 0){
			$sentences[$sentence['id']] = $sentence;
		}
	}
	}
	$ordered = array();
	foreach($top_n as $id){
		array_push($ordered, $sentences[$id]);
	}
	return $ordered;
}

function retrieve_search_results($query) {
	$sql = "SELECT 
			sentence.id as id, sentence.narrative_id, sentence, title, date, full as author 
		 	from sentence, narrative, 
			author_xref_narrative as axn, author
			WHERE MATCH sentence AGAINST ('$query' IN BOOLEAN MODE)
			AND sentence.narrative_id = narrative.id
			AND axn.narrative_id = narrative.id
			AND axn.author_id = author.id;";
	$result = mysql_query($sql) or die ("Error searching for sentences with
	<br> query $query:
	<br> ".mysql_error()."
	<br> on SQL query $sql
	<br> at similarsentences/similar-sentences.php lines 377--381");

	$sentences = array();
	while ($sentence_result = mysql_fetch_assoc($result)){
		$sentence = array();
		$sentence['id'] = $sentence_result['id'];
		$sentence['words'] = getWordsInSentence($sentence['id']); //util.php
		// ... and whatever other metadata here
		$sentence['narrative_id'] = $sentence_result['narrative_id'];
		$sentence['title'] = $sentence_result['title'];
		$sentence['date'] = $sentence_result['date'];
		$sentence['author'] = $sentence_result['author'];
		// store the information
		if(count($sentence['words']) > 0){
			array_push($sentences, $sentence);
		}
	}
	return $sentences;
}

/** Removes features whose absolute values have decreased (i.e they've gotten
less important).
*/
function prune_features($features, $old_features) {
	$max = 0;
	$min = 0;
	foreach (array_keys($features) as $feature) {
		if ($max < abs($features[$feature])) {
			$max = $features[$feature];
		}
		if ($min > abs($features[$feature])) {
			$min = abs($features[$feature]);
		}
	}
	$cutoff = $min;
	if ($max > $min) {
		$cutoff = ($max - $min) / 2;
	}
	$pruned_features = array();
	foreach (array_keys($features) as $feature) {
		if ($features[$feature] > $cutoff) {
			$pruned_features[$feature] = $features[$feature];
		}
	}
	return $pruned_features;
}

function is_word_feature($featureID){
	return starts_with($featureID, "w");
}

function is_dependency_feature($featureID){
	return starts_with($featureID, "d_");
}

function is_dependency_pair_feature($featureID){
	return starts_with($featureID, "dg") || starts_with($featureID, "dr") ;
}

function is_search_word_feature($featureID){
	return starts_with($featureID, "s");
}

function get_id_from_feature_name($featureID){
	$components = explode("_", $featureID);
	return $components[1];
}

function get_dependency_id_from_feature_name($featureID){
	$components = explode("_", $featureID);
	return $components[1];
}

function get_pos_from_feature_name($featureID){
	$components = explode("_", $featureID);
	return $components[2];
}

function get_word_from_feature_name($featureID){
	$components = explode("_", $featureID);
	return $components[3];
}

function starts_with($haystack, $needle){
    $length = strlen($needle);
    return (substr($haystack, 0, $length) === $needle);
}

function make_word_feature_names($wordID, $pos, $word){
	global $expand_to_synonyms;
	$features = array();
	array_push($features, "w_".$wordID);
	 if ($expand_to_synonyms) {
	 	$synonym_ids = get_synonym_ids($wordID);
	 	foreach($synonym_ids as $id) {
	 		array_push($features, "w_".$id);
	 	}
	 }
	return $features;
}

function make_search_word_feature_name($wordID, $pos, $word){
	return "s_".$wordID.'_'.$pos.'_'.$word;
}
?>