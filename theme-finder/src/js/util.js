/** remove whitespace from the start and end of a string**/
String.prototype.trim = function () {
	return this.replace(/^\s*/, "").replace(/\s*$/, "");
}

/** append a list of elements to the end of an array**/
Array.prototype.append = function(elements){
	for(var i = 0; i < elements.length; i++ ){
		this.push(elements[i]);
	}
	return this;
}

Array.prototype.remove = function(s){
    for(i=0;i < this.length; i++){
        if(s==this[i]) this.splice(i, 1);
    }
}

/** check if an array <a> contains an object <obj>**/
Array.prototype.contains = function(obj) {
	var i = this.length;
	while (i--) {
		if (this[i] === obj) {
			return true;
		}
	}
	return false;
}

/*calculates spacing between words based on the presence of punctuation*/
function spaceBetweenWords(word1, word2){
    if(word1 && word2){
	    var prev = word1.substring(word1.length-1);
    	var next = word2.substring(0, 1);
    	var alphabet = "abcdefghijklmnopqrstuvwxyz&1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    	var no_space_before=".!,``)?;:%\"'";
    	var no_space_after='\'"``(';
    	if(next=="."){
    	    return "";
    	}
    	else if(no_space_before.indexOf(next) > 0){
    		return '';
    	}else if(no_space_after.indexOf(prev) > 0){
    		return '';
    	}else{
    		return ' ';
    	}
	}else{
	    return " "
	}	
}

/* generates a permutation of the numbers between 0 and the given number **/
function permuteIndices(size) {
    var permutation = [];
    var original = [];
    for(var i = 0; i < size; i++){
        original.push(i);
    }
    while(original.length > 0){
        var randomIndex = Math.floor(Math.random()*original.length);
        permutation.push(original[randomIndex]);
        original.splice(randomIndex, 1);
    }
    return permutation;
}