var baseURL = "http://ec2-52-43-158-164.us-west-2.compute.amazonaws.com:3000"
$(document).ready(function(){
    $("#initialSearchText").hide();
    $('input[type="range"]').rangeslider({
        polyfill: false,
        onInit: function() {},
        onSlide: function(position, value) {},
        onSlideEnd: function(position, value) {}
    });            
                   
    $.ajax({
        url: baseURL + "/topicsList", 
        jsonp: true
    }).done(function(responseData) {                
        var availableTags = responseData.topics.map(function(topic) { 
            return {"label" : topic.replace("-", " "), "value" : topic} 
        });
        $("#searchText, #initialSearchText").autocomplete({
            source: function(request, response) {
                    var results = $.ui.autocomplete.filter(availableTags, request.term);
                    results = results.slice(0, 10)
                    if(results.length == 0) {
                        results.push({label: "Sorry No Match :(", value: ""})
                    } 
                    response(results);
                },
            select: function( event, ui ) {
                if(ui.item.value != "") {
                    loadRecommendations(ui.item.value); 
                    $("#myModal").modal('hide')                 
                }                
            }
        });        
        $("#loadingGif").hide();
        $("#initialSearchText").show();
    });                
    $("#myModal").modal({show: true, backdrop: 'static', keyboard: false})
});

function loadRecommendations(topic) {
    $("#contentPane h1").text(topic.replace("-", " "));
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
        topics = responseData;
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
    loadDescription(topic, false)
}
var currentTopic;
function loadDescription(topic, addTopicToHeading){
    if(currentTopic != topic) {
        currentTopic = topic;
        $.ajax({
            url: baseURL + "/description?topic="+topic, 
            jsonp: true
        }).done(function(responseData) {                
            var heading = "Description" + (addTopicToHeading ?  "- " + camelize(topic) : "");
            $("#descriptionHeading").html(heading);            
            $("#description").html(responseData.description);
        }); 
    }    
}

function camelize(str) {
    return str.replace(/(?:^\w|[A-Z]|\b\w|\s+)/g, function(match, index) {
        if (+match === 0) return ""; // or if (/\s+/.test(match)) for white spaces
        return index == 0 ? match.toLowerCase() : match.toUpperCase();
    });
}