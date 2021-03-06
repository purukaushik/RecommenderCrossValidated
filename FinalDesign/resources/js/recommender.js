var baseURL = "http://ec2-52-43-158-164.us-west-2.compute.amazonaws.com:3000"
$(document).ready(function(){
    $("#initialSearchText").hide();
    $('input[type="range"]').rangeslider({
        polyfill: false,
        onInit: function() {},
        onSlide: function(position, value) { },
        onSlideEnd: function(position, value) { loadRecommendations(localStorage.getItem("topic"));     }
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
                        results.push({"label" : "Sorry No Match :(", "value" : ''})
                    } 
                    response(results.sort(function(a,b) {return (a.label > b.label) ? 1 : ((b.label > a.label) ? -1 : 0);} ));
                },
            select: function( event, ui ) {                
                if(ui.item.value != "Sorry No Match :(") {
                    loadRecommendations(ui.item.value); 
                    $("#myModal").modal('hide')                 
                } else {
                    $(event.target).val("")
                }           
            }
        });        
        $("#loadingGif").hide();
        $("#initialSearchText").show();
    });                

    $("#questionSortOrder").on("change", function(event){
        loadQuestions(localStorage.getItem("topic")) 
    })
    $("#myModal").modal({show: true, backdrop: 'static', keyboard: false})
});

function loadQuestions(topic) {
    $.ajax({
        url: baseURL + "/recommendedQuestion?topic=" + 
            topic + "&sortOrder=" +  $("#questionSortOrder").val(), 
        jsonp: true
    }).done(function(responseData) {
        if(responseData.question.length == 0) {
            $("#postRecommendations").html("No recommendation available. Try other sorting lists.")
        } else {
            var content = ""
            for(i=0; i<responseData.question.length; i++) {
                content += '<a href="'+responseData.question[i].Link+'" target="_blank">'
                +responseData.question[i].Title+'</a>';
            }
            $("#postRecommendations").html(content);
        }
    }); 
}

function loadRecommendations(topic) {
    $("#contentPane h1").text(topic.replace("-", " "));
    var view = $("#averageViewInput").val(),
    rating = $("#averageRatingInput").val(),
    support = $("#supportInput").val(),
    recommendationCount = $("#recommendationCountInput").val(),
    contentCount = Math.floor(($("#recommendationTypeCountInput").val() / 10.0) * recommendationCount),
    collabCount = recommendationCount - contentCount;  
    localStorage.setItem("topic", topic);  
    $.ajax({
        url: baseURL + "/recommendation?topic="+topic+"&view="+view+"&upvotes="+rating+"&support="+support+"&collabCount="+collabCount+"&cosineCount="+contentCount,         
        jsonp: true
    }).done(function(responseData) {                
        var NODE_RADIUS = [40, 50, 60]
        var graph = {}
        var nodes ={}
        nodes[topic] = {radius: 50, type: 'R', name: topic, fixed: true}
        var rootEdges = {}
        
        function structureNodes(nodesList, type) {
            var START_EDGE_WEIGHT = 2;
            let set = new Set();
            for(i=0; i<nodesList.length; i++) {
                set.add(nodesList[i].value);
            }
            var edgeWeightList = Array.from(set).sort(),
            step = 8 / edgeWeightList.length;
            for(i=0; i<nodesList.length; i++) {
                var node = nodes[nodesList[i].name],
                index = edgeWeightList.indexOf(nodesList[i].value),
                edgeWeight = START_EDGE_WEIGHT + index * step;
                if(node) {
                    node.type = 'B'                    
                    node.radius = node.radius < NODE_RADIUS[nodesList[i].weight-1] ? NODE_RADIUS[nodesList[i].weight-1] : node.radius
                    rootEdges[nodesList[i].name].weight = rootEdges[nodesList[i].name].weight < edgeWeight ? edgeWeight : rootEdges[nodesList[i].name].weight
                } else {
                    nodes[nodesList[i].name] = {radius: NODE_RADIUS[nodesList[i].weight-1], type: type, name: nodesList[i].name}
                    rootEdges[nodesList[i].name] = { weight: edgeWeight }
                }                
            }
        }
        
        if(responseData.collab.length > 0) {
            structureNodes(responseData.collab, 'S')
        }

        if(responseData.cosine.length > 0) {
            structureNodes(responseData.cosine, 'C')
        }

        graph["nodes"] = nodes
        graph["edges"] = {}
        graph["edges"][topic] = rootEdges
        if($("div#contentPane #graph")) {
            $("div#contentPane #graph").remove()
            var width = $(window).width(), 
            height = $(window).height();
            width = (width < 500) ? width - 20 : width * 0.48
            height = ($(window).width() <= 500) ? 500 : height - 150
            $("div#contentPane").append("<canvas id='graph' width='"+width+"' height='"+height+"'></canvas>")
        }
        loadGraph(graph)
    });
    loadDescription(topic, false)
    loadQuestions(topic)
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
            if(responseData.description) {
                $("#description").html(responseData.description);
            } else {
                $("#description").html("Description unavailable.");
            }              
        }); 
    }    
}

function camelize(str) {
    return str.replace(/(?:^\w|[A-Z]|\b\w|\s+)/g, function(match, index) {
        if (+match === 0) return ""; // or if (/\s+/.test(match)) for white spaces
        return index == 0 ? match.toLowerCase() : match.toUpperCase();
    });
}