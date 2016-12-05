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
                    response(results);
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
        //url: baseURL + "/collabf?topic="+topic, 
        jsonp: true
    }).done(function(responseData) {                
        var NODE_RADIUS = [40, 50, 60]
        var graph = {}
        var nodes ={}
        nodes[topic] = {radius: 50, type: 'R', name: topic, fixed: true}
        var rootEdges = {}
        
        function structureNodes(nodesList, type) {
            for(i=0; i<nodesList.length; i++) {
                node = nodes[nodesList[i].name]
                if(node) {
                    node.type = 'B'
                    node.radius = node.radius < NODE_RADIUS[nodesList[i].weight] ? NODE_RADIUS[nodesList[i].weight] : node.radius
                } else {
                    nodes[nodesList[i].name] = {radius: NODE_RADIUS[nodesList[i].weight], type: type, name: nodesList[i].name}
                    rootEdges[nodesList[i].name] = {weight: (10 - i/2)}
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
            $("div#contentPane").append("<canvas id='graph' width='660' height='600'></canvas>")
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