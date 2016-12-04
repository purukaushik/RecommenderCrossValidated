var baseURL = "http://ec2-52-43-158-164.us-west-2.compute.amazonaws.com:3000"
$(document).ready(function(){
    $('input[type="range"]').rangeslider({
        polyfill: false,
        onInit: function() {},
        onSlide: function(position, value) {},
        onSlideEnd: function(position, value) {}
    });            
                   
    $.ajax({
        url: baseURL + "/topicslist", 
        jsonp: true
    }).done(function(responseData) {                
        var availableTags = responseData.topics
        $("#searchText").autocomplete({
            source: function(request, response) {
                    var results = $.ui.autocomplete.filter(availableTags, request.term);
                    response(results.slice(0, 10));
                },
            select: function( event, ui ) {
                //loadRecommendations(ui.item.value);
                loadRecommendations("likert");                        
            }
        });
    });            

});

function loadRecommendations(topic) {
    $("#contentPane h1").text(camelize(topic.replace("-", " ")));
    var view = $("#averageViewInput").val(),
    rating = $("#averageRatingInput").val(),
    support = $("#supportInput").val(),
    recommendationCount = $("#recommendationCountInput").val(),
    contentCount = $("#recommendationTypeCountInput").val(),
    collabCount = recommendationCount - contentCount;
    $.ajax({
        //url: baseURL + "/recommendations?topic="+topic+"&view="+view+"&upvotes="+rating+"&support="+support+"&collabCount="+collabCount+"&contentCount="+contentCount, 
        url: baseURL + "/collabf?topic="+topic, 
        jsonp: true
    }).done(function(responseData) {                
        topics = responseData.related_topics;
        topics.sort(function(a,b) {return (a.value < b.value) ? 1 : ((b.value < a.value) ? -1 : 0);} );
        topics = topics.filter(function(element) { return element.name != topic && element.value > 0});
        if(topics.length > 10) {
            topics = topics.slice(0, 20);   
        }
        var graph = {}
        var nodes = { 1: {radius: 50, type: 'R', name: topic, fixed: true}}
        var rootEdges = {}
        for(i=0; i<topics.length; i++) {
            nodes[i+2] = {radius: 50, type: 'C', name: topics[i].name}
            rootEdges[i+2] = {weight: (10 - i/2)}
        }
        graph["nodes"] = nodes
        graph["edges"] = {}
        graph["edges"][1] = rootEdges
        if($("div#contentPane #graph")) {
            $("div#contentPane #graph").remove()
            $("div#contentPane").append("<canvas id='graph' width='660' height='600'></canvas>")
        }
        loadGraph(graph)
    });
}
function loadDescription(topic, addTopicToHeading){
    $("#descriptionHeading").html("Description - " + camelize(topic));
    /*
    $.ajax({
        url: baseURL + "/description?topic="+topic, 
        jsonp: true
    }).done(function(responseData) {                
        var desc = "Description" + (addTopicToHeading ?  "- " + camelize(topic) : "");
        $("#descriptionHeading").html(desc);            
        $("#description").html(responseData.description);
    }); 
    */
}

function camelize(str) {
    return str.replace(/(?:^\w|[A-Z]|\b\w|\s+)/g, function(match, index) {
        if (+match === 0) return ""; // or if (/\s+/.test(match)) for white spaces
        return index == 0 ? match.toLowerCase() : match.toUpperCase();
    });
}