(function($){

  var Renderer = function(canvas){
    var canvas = $(canvas).get(0)
    var ctx = canvas.getContext("2d");
    var particleSystem

    var that = {
      init:function(system){        
        particleSystem = system
        particleSystem.screenSize(canvas.width, canvas.height) 
        particleSystem.screenPadding(80)         
        that.initMouseHandling()
      },
      
      redraw:function(){        
        ctx.fillStyle = "white"
        ctx.fillRect(0,0, canvas.width, canvas.height)
        
        particleSystem.eachEdge(function(edge, pt1, pt2){          
          ctx.strokeStyle = "rgba(0,0,0, .8)"          
          ctx.lineWidth = edge.data.weight
          ctx.beginPath()
          ctx.moveTo(pt1.x, pt1.y)
          ctx.lineTo(pt2.x, pt2.y)
          ctx.stroke()
        })

        particleSystem.eachNode(function(node, pt){          
          var w = 10 //+ Math.random() * 30
          ctx.fillStyle = (node.data.type == 'R') ? "#333" : (node.data.type == 'C') ? "#F7B32B" : "#8BD854"
          //ctx.fillRect(pt.x-w/2, pt.y-w/2, w,w)
          ctx.beginPath();
          radius = node.data.radius
          ctx.arc(pt.x, pt.y, radius, 0, 2 * Math.PI, false);              
          ctx.closePath();      
          ctx.fill();     
          ctx.fillStyle = (node.data.type == 'R') ? "White" : "black";     
          if(node.data.type == 'R') 
            ctx.fillText(node.data.name, pt.x, pt.y);          
          else
            ctx.fillText(node.data.name, pt.x-(radius/2) - 12, pt.y);
        })    			
      },
      
      initMouseHandling:function(){
        // no-nonsense drag and drop (thanks springy.js)
        var dragged = null;

        // set up a handler object that will initially listen for mousedowns then
        // for moves and mouseups while dragging
        var handler = {
          clicked:function(e){

            var pos = $(canvas).offset();
            _mouseP = arbor.Point(e.pageX-pos.left, e.pageY-pos.top)
            dragged = particleSystem.nearest(_mouseP);
            alert(dragged.node.data.name);
            
            if (dragged && dragged.node !== null){
               dragged.node.fixed = true
            }

            $(canvas).bind('mousemove', handler.dragged)
            $(window).bind('mouseup', handler.dropped)
            
            return false
          },
          dragged:function(e){
            var pos = $(canvas).offset();
            var s = arbor.Point(e.pageX-pos.left, e.pageY-pos.top)
            if (dragged && dragged.node !== null){
              var p = particleSystem.fromScreen(s)
              dragged.node.p = p
            }
            return false
          },

          dropped:function(e){
            if (dragged===null || dragged.node===undefined) return
            if (dragged.node !== null) dragged.node.fixed = false
            dragged.node.tempMass = 1000
            dragged = null
            $(canvas).unbind('mousemove', handler.dragged)
            $(window).unbind('mouseup', handler.dropped)
            _mouseP = null
            return false
          }
        }
        
        $(canvas).mousedown(handler.clicked);

      },
      
    }
    return that
  }    

  $(document).ready(function(){
    var sys = arbor.ParticleSystem(1000, 600, 0.5) // create the system with sensible repulsion/stiffness/friction
    sys.parameters({gravity:true}) // use center-gravity to make the graph settle nicely (ymmv)
    sys.renderer = Renderer("#graph") // our newly created renderer will have its .init() method called shortly by sys...
/*
    sys.addEdge('a','b')
    sys.addEdge('a','c')
    sys.addEdge('a','d')
    sys.addEdge('a','e')
    sys.addEdge('a','f')
*/
    sys.graft({
       nodes:{
        a: {radius: 45, type: 'R', name: 'R'},
        b: {radius: 25, type: 'C', name: 'Anova'},
        c: {radius: 35, type: 'S', name: 'Time-Series'},
        d: {radius: 25, type: 'S', name: 'Big Data'},
        e: {radius: 40, type: 'C', name: 'Statistics'},
        f: {radius: 40, type: 'C', name: 'Regression'},
        g: {radius: 50, type: 'S', name: 'Mixed-Model'},
        h: {radius: 35, type: 'S', name: 'lme4-nlme'},
        i: {radius: 50, type: 'C', name: 'Logistic'},
        j: {radius: 45, type: 'C', name: 'Machine-Learning'},
      }, 
      edges:{
        a:{ b:{weight: 1},
            c:{weight: 3},
            d:{weight: 2},
            e:{weight: 2},
            f:{weight: 4},            
            g:{weight: 4},
            h:{weight: 5},
            i:{weight: 5},
            j:{weight: 6},            
          }
        }
     })

  })

})(this.jQuery)