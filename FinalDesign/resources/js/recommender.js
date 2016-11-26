function makeRecommendation(nodeArray) {
	var selectedTopic = nodeArray[nodeArray.length-1].name;
	document.getElementById("questionRecommendationHeading").innerHTML = "Top Recommendation for "  + selectedTopic.toUpperCase() + ":";	
	document.getElementById("activityHeading").innerHTML = "Activity in "  + selectedTopic.toUpperCase() + ":";	
	var content = "<div class='recommendation-bg'> <a herf='#'> Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</a> </div>";
	var count = Math.ceil(Math.random()*5);
	var htmlContent = '';
	for(i=0; i<count; i++) {
		htmlContent +=  content;
	}
	document.getElementById("questionRecommendations").innerHTML = htmlContent;
	document.getElementById("moreCharts").style.display = "block";
	loadLineGraph();
}

function loadLineGraph() {
	var m = [80, 80, 80, 80]; // margins
    var w = 500 - m[1] - m[3]; // width
    var h = 400 - m[0] - m[2]; // height
    
    var data = [];
   	for(i=0; i<7; i++) {
   		data.push(Math.ceil(Math.random()*12))
   	}

    var x = d3.scale.linear().domain([new Date(2010, 0, 1, 0), new Date(2016, 0, 1, 0)]).range([0, w]),
    tick = x.ticks(d3.timeYear),
    y = d3.scale.linear().domain([0, 12]).range([h, 0]),
    line = d3.svg.line()
      .x(function(d,i) {         
        return x(i) + 10; 
      })
      .y(function(d) { 
        return y(d); 
      })

    tick.map(x.tickFormat("%Y"))

    document.getElementById("lineGraph").innerHTML = "";

    var graph = d3.select("#lineGraph").append("svg:svg")
        .attr("width", w + m[1] + m[3])
        .attr("height", h + m[0] + m[2])
        .append("svg:g")
        .attr("transform", "translate(" + m[3] + "," + m[0] + ")");

    var xAxis = d3.svg.axis().scale(x).tickSize(-h).tickSubdivide(false);
    graph.append("svg:g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + h + ")")
        .call(xAxis);


    var yAxisLeft = d3.svg.axis().scale(y).ticks(4).orient("left");
    graph.append("svg:g")
            .attr("class", "y axis")
            .attr("transform", "translate(-25,0)")
            .call(yAxisLeft);
      
    graph.append("svg:path").attr("d", line(data));
}