<?php
include '../../../config.php';

/** Global Variables
*/
$gov_result = array();
$dep_result = array();
$rel_result = array();

function getRelationID($relation){
  $query = "SELECT id FROM relationship WHERE relationship ='".$relation."';";
  //echo $query.'
  //';
  $result = mysql_query($query);
  if(mysql_num_rows($result)>0){
    $row =  mysql_fetch_array($result);
    return $row['id'];
  }else{
    return -1;
  }
}

/**
	Even though this function is named "getWordID", it
	actually returns all the ID's that correspond to a
	given surface word. A word can have multiple id's
	if it has different parts of speech.
*/
function getWordID($word){
	$query = "";
	if(!(strstr($word, "*"))){
		$query = "SELECT id FROM word WHERE word ='".mysql_escape_string(trim($word))."';";
	}else{
		$query = "SELECT id FROM word WHERE word like '".mysql_escape_string(trim(str_replace("*", "%", $word)))."';";
	}
  $result = mysql_query($query);
  if(mysql_num_rows($result)>0){
    $ids = array();
    while($row =  mysql_fetch_array($result)){
      array_push($ids, $row['id']);
    }
    return join(", ", $ids);
  }else{
    return 'null';
  }
}

function getWord($id){
  $query = "SELECT word from word where id = ".$id.";";
  $result = mysql_query($query);
  if(mysql_num_rows($result)>0){
    return $row['id'];
  }else{
    return '??';
  }
}

function getDependencyID($relationID, $govID, $depID){
  $query = "SELECT id FROM dependency WHERE relation_id =".$relationID." AND gov_id =".$govID." and dep_id = ".$depID.";";
  $result = mysql_query($query);
  if(mysql_num_rows($result)>0){
    $row= mysql_fetch_array($query);
    return $row['id'];
  }else{
    return -1;
  }
}


function getMetadata($sentenceID){
   $query="SELECT sentence, title, publisher, full, pubPlace, para.narrative_id as id, paragraph.id as pid, type, date
   FROM paragraph
   JOIN
   (SELECT sentence, title, publisher, full, pubPlace, N.narrative_id, date, paragraph_id as id
     FROM (author
     JOIN author_xref_narrative
     ON author.id = author_xref_narrative.author_id)
     JOIN(SELECT sentence, title, publisher, pubPlace, narrative_id, paragraph_id, date
         from narrative JOIN
         (SELECT DISTINCT sentence, narrative_id, paragraph_id
         from sentence
         WHERE sentence.id = ".$sentenceID.") as S
       ON narrative.id = S.narrative_id) as N
   ON author_xref_narrative.narrative_id = N.narrative_id) AS para
   ON paragraph.id = para.id;";
    $result = mysql_query($query);
    return $result;
}

/** Get matching dependency ID's

@param	withinSentence	True if you want to search within
						a set of sentences
@param	withinNarrative	True if you want to search within a
						set of narratives
@param	within			a list of sentence or narrative id's
						if either <withinSentence> or
						<withinNarrative> is marked as True.
						Otherwise, false.
*/
function getDependencyIDs($gov, $dep, $relation, $withinNarrative, $withinSentence, $within, $getStatistics){
  $tablenames = "dependency, dependency_xref_sentence ";
  $where = "";
  if($withinSentence && strlen($within)>0){
	  $tablenames = "dependency, dependency_xref_sentence ";
      $where = "AND sentence_id in (".$within.")";
  }else if ($withinNarrative && strlen($within)>0){
    $tablenames = "dependency, dependency_xref_sentence, sentence ";
    $where = " AND sentence.id = sentence_id AND narrative_id in (".$within.")";
  }
  $r = strlen($relation)>0;
  $g = strlen($gov)>0;
  $d = strlen($dep)>0;
  $rel_w = "";
  $gov_w  ="";
  $dep_w = "";
  if($r){
    $rel_w = "dependency.relation_id IN (".$relation.")";
  }
  if($g){
    $gov_w = "dependency.gov_id IN (".$gov.")";
  }
  if($d){
    $dep_w = "dependency.dep_id IN (".$dep.")";
  }
  if($r || $g || $d ){
    $query = "SELECT * FROM ".$tablenames." WHERE ";
	$statistics_query = "SELECT *, COUNT(sentence_id) as value FROM ".$tablenames." WHERE ";
    if($r && $g && $d){
      $query = $query.$rel_w." AND ".$gov_w." AND ".$dep_w;
	  $statistics_query = $statistics_query.$rel_w." AND ".$gov_w." AND ".$dep_w;
    }
    else if($r && $g){
      $query = $query.$rel_w." AND ".$gov_w;
	  $statistics_query = $statistics_query.$rel_w." AND ".$gov_w;
    }
    else if($r && $d){
      $query = $query.$rel_w." AND ".$dep_w;
	  $statistics_query = $statistics_query.$rel_w." AND ".$dep_w;
    }
    else if($g && $d){
      $query = $query."((".$gov_w." AND ".$dep_w.") OR ";
	  $query = $query." (dependency.dep_id IN (".$gov.") AND dependency.gov_id IN (".$dep."))) ";
	  $statistics_query = $statisticsquery."((".$gov_w." AND ".$dep_w.") OR ";
	  $statistics_query = $statistics_query." (dependency.dep_id IN (".$gov.") AND dependency.gov_id IN (".$dep."))) ";
    }
    else if ($r){
        $query = $query.$rel_w;
		$statistics_query = $statistics_query.$rel_w;
    }
    else if ($g){
        $query = $query." (".$gov_w;
		$query = $query." OR dependency.dep_id IN (".$gov.")) ";
		$statistics_query = $statistics_query." (".$gov_w;
		$statistics_query = $statistics_query." OR dependency.dep_id IN (".$gov.")) ";
	}
    else{
        $query = $query." (".$dep_w;
		$query = $query." OR dependency.gov_id IN (".$dep.")) ";
		$statistics_query = $statistics_query." (".$dep_w;
		$statistics_query = $statistics_query." OR dependency.gov_id IN (".$dep.")) ";
    }
    $query = $query." AND dependency_id = dependency.id ";
    $query = $query.$where.";";
	//statistics
	$statistics_query = $statistics_query."AND dependency_id = dependency.id ";
    $statistics_query = $statistics_query.$where;
	if($getStatistics){
	    global $rel_result, $gov_result, $dep_result;
	     $t1 = time();
		  $relationship_query = $statistics_query." GROUP BY(dependency.relation_id) ORDER BY value DESC;";
		  $gov_query = $statistics_query." GROUP BY(dependency.gov) ORDER BY value DESC;";
		  $dep_query = $statistics_query." GROUP BY(dependency.dep) ORDER BY value DESC;";
	     $rel_result = mysql_query($relationship_query);
	     $gov_result = mysql_query($gov_query);
	     $dep_result = mysql_query($dep_query);
	     $t = time() - $t1;
	  }
  }else if($withinSentence){
		$query = "SELECT * from dependency_xref_sentence WHERE sentence_id in (".$within.");";
  }
 // Finally, query the database
  $result = mysql_query($query);
  return $result;
}


function relationshipIDList($words){
  if(strlen($words) > 0){
  $exploded = explode(' ', trim($words));
  $listformat = "";
  $i = 0;
  foreach($exploded as $word){
    if($i==0){
      $listformat = $listformat.getRelationID($word);
    }else{
      $listformat = $listformat.", ".getRelationID($word)." ";
    }
    $i+=1;
  }
  return $listformat;
  }else{
    return "";
  }
}

/**
Converts a list of words to a list of word ID's
*/
function wordIDList($words){
    if(strlen($words) > 0){
		$exploded = explode(' ', trim($words));
		if(strpos($words, ',')){
			$exploded = explode(',',trim($words));
		}
	    $listformat = "";
	    $i = 0;
	    foreach($exploded as $word){
	      if($i==0){
	        $listformat = $listformat.getWordID($word);
	      }else{
	        $listformat = $listformat.", ".getWordID($word)." ";
	      }
	      $i+=1;
	    }
	    return $listformat;
    }else{
      return "";
    }
}

/**
	a.k.a join(', ', $words)
	my bad.
*/
function listFormat($words){
  if(strlen($words) > 0){
  $exploded = explode(' ', trim($words));
  $listformat = "";
  $i = 0;
  foreach($exploded as $word){
    if($i == 0){
      $listformat = $listformat."'".$word."'";
    }else{
      $listformat = $listformat.", '".$word."' ";
    }
    $i += 1;
  }
  return $listformat;
  }else{
    return "";
  }
}

function numberList($numbers){
  if(strlen($numbers) > 0){
  $exploded = explode(' ', trim($numbers));
  $listformat = "";
  $i = 0;
  foreach($exploded as $word){
    if($i==0){
      $listformat = $listformat.$word;
    }else{
      $listformat = $listformat.", ".$word." ";
    }
    $i+=1;
  }
  return $listformat;
  }else{
    return "";
  }
}




$STOPWORDS =  explode(" ", "the and so are for be but this what 's did had they doth a to is that was as are at an of with . , ; ? ' \" : `");
$STOPS = "say 'twas twas go am come go tell say does let were see thee thou thy mine make enter been give take  comes think know hath tis the and so are for be but this what 's did had they do have be doth a to is that was as are at an of with . , ; ? ' \" : `";
$MYSQL_STOPWORDS = "a's	able	about	above	according
accordingly	across	actually	after	afterwards
again	against	ain't	all	allow
allows	almost	alone	along	already
also	although	always	am	among
amongst	an	and	another	any
anybody	anyhow	anyone	anything	anyway
anyways	anywhere	apart	appear	appreciate
appropriate	are	aren't	around	as
aside	ask	asking	associated	at
available	away	awfully	be	became
because	become	becomes	becoming	been
before	beforehand	behind	being	believe
below	beside	besides	best	better
between	beyond	both	brief	but
by	c'mon	c's	came	can
can't	cannot	cant	cause	causes
certain	certainly	changes	clearly	co
com	come	comes	concerning	consequently
consider	considering	contain	containing	contains
corresponding	could	couldn't	course	currently
definitely	described	despite	did	didn't
different	do	does	doesn't	doing
don't	done	down	downwards	during
each	edu	eg	eight	either
else	elsewhere	enough	entirely	especially
et	etc	even	ever	every
everybody	everyone	everything	everywhere	ex
exactly	example	except	far	few
fifth	first	five	followed	following
follows	for	former	formerly	forth
four	from	further	furthermore	get
gets	getting	given	gives	go
goes	going	gone	got	gotten
greetings	had	hadn't	happens	hardly
has	hasn't	have	haven't	having
he	he's	hello	help	hence
her	here	here's	hereafter	hereby
herein	hereupon	hers	herself	hi
him	himself	his	hither	hopefully
how	howbeit	however	i'd	i'll
i'm	i've	ie	if	ignored
immediate	in	inasmuch	inc	indeed
indicate	indicated	indicates	inner	insofar
instead	into	inward	is	isn't
it	it'd	it'll	it's	its
itself	just	keep	keeps	kept
know	known	knows	last	lately
later	latter	latterly	least	less
lest	let	let's	like	liked
likely	little	look	looking	looks
ltd	mainly	many	may	maybe
me	mean	meanwhile	merely	might
more	moreover	most	mostly	much
must	my	myself	name	namely
nd	near	nearly	necessary	need
needs	neither	never	nevertheless	new
next	nine	no	nobody	non
none	noone	nor	normally	not
nothing	novel	now	nowhere	obviously
of	off	often	oh	ok
okay	old	on	once	one
ones	only	onto	or	other
others	otherwise	ought	our	ours
ourselves	out	outside	over	overall
own	particular	particularly	per	perhaps
placed	please	plus	possible	presumably
probably	provides	que	quite	qv
rather	rd	re	really	reasonably
regarding	regardless	regards	relatively	respectively
right	said	same	saw	say
saying	says	second	secondly	see
seeing	seem	seemed	seeming	seems
seen	self	selves	sensible	sent
serious	seriously	seven	several	shall
she	should	shouldn't	since	six
so	some	somebody	somehow	someone
something	sometime	sometimes	somewhat	somewhere
soon	sorry	specified	specify	specifying
still	sub	such	sup	sure
t's	take	taken	tell	tends
th	than	thank	thanks	thanx
that	that's	thats	the	their
theirs	them	themselves	then	thence
there	there's	thereafter	thereby	therefore
therein	theres	thereupon	these	they
they'd	they'll	they're	they've	think
third	this	thorough	thoroughly	those
though	three	through	throughout	thru
thus	to	together	too	took
toward	towards	tried	tries	truly
try	trying	twice	two	un
under	unfortunately	unless	unlikely	until
unto	up	upon	us	use
used	useful	uses	using	usually
value	various	very	via	viz
vs	want	wants	was	wasn't
way	we	we'd	we'll	we're
we've	welcome	well	went	were
weren't	what	what's	whatever	when
whence	whenever	where	where's	whereafter
whereas	whereby	wherein	whereupon	wherever
whether	which	while	whither	who
who's	whoever	whole	whom	whose
why	will	willing	wish	with
within	without	won't	wonder	would
wouldn't	yes	yet	you	you'd
you'll	you're	you've	your	yours
yourself	yourselves	zero";
$MYSQL_STOPWORDS_LIST = preg_split("/\s/", $MYSQL_STOPWORDS);
?>
