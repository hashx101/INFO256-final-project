TASK_PARAMS = {
	interfaces : [ "search" , "relevance-control", "relevance-feedback"],
	interface_orders : [
		[0, 1, 2],
		[0, 2, 1],
		[1, 0, 2],
		[1, 2, 0],
		[2, 0, 1],
		[2, 1, 0]
	],
	collections : ["shakespeare"],
	theme_orders : [
		[0, 1, 2],
		[0, 2, 1],
		[1, 0, 2],
		[1, 2, 0],
		[2, 0, 1],
		[2, 1, 0],
	],
	themes : {
			shakespeare : [
				{
					number : 0,
					code : "shakes-green-as-inexperience",
					title : "The word 'green' used as inexperience, innocence, and youth.",
					example_0 : "My salad days, When I was green in judgement: cold in blood, To say as I said then!",
					example_1 : "I will not praise thy wisdom, <br> Which, like a bourn, a pale, a shore, confines <br> Thy spacious and dilated parts: here's Nestor; <br> Instructed by the antiquary times, <br> He must, he is, he can not but be wise: <br> But pardon, father Nestor, were your days <br> As green as Ajax' and your brain so tempered, <br> You should not have the eminence of him, <br> But be as Ajax.",
					relevant_ids : [8899, 60998],
					relevant_query: "green",
				},
				{
					number : 1,
					code : "shakes-excessive-grief",
					title : "Excessive mourning or grief, especially for the dead.",
					example_0: " Tis sweet and commendable in your nature, Hamlet, To give these mourning duties to your father: But, you must know, your father lost a father; That father lost, lost his, and the survivor bound In filial obligation for some term To do obsequious sorrow: but to persever In obstinate condolement is a course Of impious stubbornness;' tis unmanly grief; It shows a will most incorrect to heaven, A heart unfortified, or mind impatient, An understanding simple and unschooled: For what we know must be and is as common As any the most vulgar thing to sense, Why should we in our peevish opposition Take it to heart?",
					example_1: "O, she that hath a heart of that fine frame To pay this debt of love but to a brother, How will she love, when the rich golden shaft Hath killed the flock of all affections else That live in her; when liver, brain and heart, These sovereign thrones, are all supplied, and filled Her sweet perfections with one self king!",
					relevant_ids : [19212, 62412],
					relevant_query: "grief",
				},
				{
					number : 2,
					code: "shakes-world-as-stage",
					title: "The world as a stage.",
					example_0 : "All the world's a stage, <br> And all the men and women merely players: <br>They have their exits and their entrances; <br> And one man in his time plays many parts, <br> His acts being seven ages.",
					example_1 : "Life's but a walking shadow, a poor player <br> That struts and frets his hour upon the stage <br> And then is heard no more: it is a tale <br>Told by an idiot, full of sound and fury, <br> Signifying nothing.",
					relevant_ids : [12922, 32715],
					relevant_query: "stage",
				},
		
			],
			crane : [
				{
					number : 0,
					code : "crane-scale-shifts",
					title : "Shifts in scale, between the petty and the grand; miniatures and toys, especially as contrasted with the cosmic.",
					example_0 : "Horace was undergoing changes of feeling so rapidly that he was merely moved hither and then thither like a kite.",
					example_1 : "Little Jim was, for the time, engine Number 26, and he was making the run between Syracuse and Rochester.",
				},
				{
					number : 1,
					code : "crane-flashes-of-light",
					title : "Flashes of light, chiaroscuro, contrast between light and shadow, especially as a figure for sudden apprehension, perception, or understanding.",
					example_0 : "Suddenly there was another swish and another long flash of bluish light, and this time it was alongside the boat, and might almost have been reached with an oar.",
					example_1 : "Occasionally a face, as if illumined by a flash of light, would shine out, ghastly and marked with pink spots.",
				},
				{
					number : 2,
					code : "crane-lines",
					title : "Rows, lines, and columns, especially people lined up in rows.",
					example_0 : "When the door below was opened, a thick stream of men forced a way down the stairs, which were of an extraordinary narrowness and seemed only wide enough for one at a time. Yet they somehow wend down almost three abreast.",
					example_1 : "Once there came a man <br> Who said, <br> Range me all men of the world in rows.",
				},		
			]
		}
}