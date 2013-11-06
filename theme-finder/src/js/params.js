/***** Here are all the variables that maintain 
***** the state of this program 
****/


/*** Part 1: Viewing a narrative and selecting patterns
***/
var highlighter = false;
var highlightedSentence = -1;
var highlightStart = -1;
var highlightEnd = -1;
var highlightPosition = -1;
var textPattern = ""; // the string of text that's highlighted
var detected = []; // the dependencies within the selected text.
var highlighted = false; // the highligted document element.
var narrativeID = -1;
var startSentence = -1;
var startPosition = -1;
var endSentence = -1;
var endPosition = -1;

/** Part 1.a: Highlighting a pattern in the text
***/
var type = "text";
var narratives = [];
var narrativeFrames = {};
var highlightStartY = -1;

/*** Part 2: Search results
**/
var w = 150; // the width of the frequency graph
var h = 250; // the height of the frequency graph
var fontSize = "12";// font size of labels in the frequency graph
var maxNum = 20;
var graphs = [];
var graphData = [];
var page = 0;
var currentGov = "";
var currentDep = "";
var currentRel = "";
var currentQ = "";
var minGraphSize = 1; // how many data points before you draw a graph?

/** Part 2b: The random sentence graphics
**/

var randomSentence = "";
var randomDependencies = "";

/*** Part 3: Saving patterns
***/
var saved = [];

/** Part 3b: Annotating narratives**/
var highlightID = -1;
var oldNote = "";
var oldTags = "";
var allTags = "";

/** Part 3c: Word menu*/
var currentParagraph = -1;
var numSalientWords = 15;
var heatMapURL = "heatmap.php?filter=all&unit=sentence&words="
var heatMapQuery = "";
var heatMapGrammaticalQuery = "";
var searchURL = "index.php?grammatical=on&collection=all&results=&page=0&pagelength=100&gov=";

//toy data
var data_gov = [];
var data_dep = [];

/*** Part 4: Heat map
***/
var narrativeIDList = [];
var selectionInfo = {narrativeID:-1, section:-1}
var heatMapWidth = 800;
var heatMapHeight = 450;
var paper = {}; // Raphael("heatmap", heatMapWidth, heatMapHeight);
var granularity = 100;
var overlay = false;
var markColors = ["red", "fuchsia"]
var currentMarkColor;
var oldColor;
var blockWidth;
var blockHeight;
var sentencesPerBlock = 1; // sentences per block
var paragraphsPerBlock = 2; // paragraphs per block
var minBlockHeight = 5; // the smallest block height
var minBlockWidth = 3; // the smallest block width
var maxBlockWidth = 16; // the maximum block width
var unit;
var concordanceLength = 7; // number of words on each side.
windowLoaded = false;
//heat map colors
var overlapRegister = {}; // register of overlapping segments
var ovelapColor = "white"; // color when multiple searches match the same segment
var baseFillOpacity = [0.7, 0.6]; // shades of grey for columns
var highlightFillOpacity = 0.5; // shade of grey for hovered column.
var heatMapColors = ["#61B7CF", "#FFBA73", "#8E6DD7", "#FFEB73"];
var currentHeatMapColor = 0;


/*** Part 5: Word tree
***/
var defaultWordTreeSliderValue = 100;
_register = {};// objects that are associated with various passages

/*** Part 6: Similar Sentences
****/

//word suggestions:
var suggestions = {'search':[], 'Nouns':[], 'Verbs':[], 'Adjectives':[], 'Nouns-Vector':[], 'Verbs-Vector':[], 'Adjectives-Vector':[], 'Bad':[], 'Bad-Vector':[] };