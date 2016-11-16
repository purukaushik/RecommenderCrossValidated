var w = window,
    d = document,
    e = d.documentElement,
    g = d.getElementsByTagName('body')[0],
    x = w.innerWidth || e.clientWidth || g.clientWidth,
    y = w.innerHeight || e.clientHeight || g.clientHeight;

var margin = {
        top: 20,
        right: 20,
        bottom: 20,
        left: 20
    },
    width = (x - margin.right - margin.left),
    height = .8 * (y - margin.top - margin.bottom);

var root;
var names;
var rows;

var diameter = Math.max(Math.min(height, width), 100),
    format = d3.format("0.00f");

var galaxy = d3.layout.galaxy()
    .size([width, height])
    .spread(4)
    //    .initialAngle(0) // radians from down
    .value(function(d) {
        return d.size;
    });

function main(file) {

    d3.text(file,
        function(error, txtdata) {
            rows = d3.csv.parseRows(txtdata,
                function(d, i) {
                    if (i == 0) {
                        names = d;
                        return null;
                    } else {
                        d[d.length - 1] = +d[d.length - 1];
                        return d;
                    }
                });

            rows.forEach(function(r, i, a) {
                var rnames = {};
                for (var j = 0; j < r.length - 1; j++) {
                    if (rnames[r[j].toLowerCase()]) {
                        r[j] = '';
                    }
                    rnames[r[j].toLowerCase()] = true;
                }
            });

            root = unflatten(rows, "Regression");

            var lines = d3.svg.line(); // unused !
            var nodes = galaxy.nodes(root);
            var links = galaxy.links(nodes);

            var link = svg.selectAll(".link")
                .data(links)
                .enter().append("line")
                .attr("class", "link")
                .style("stroke-width", function(d) {
                    return Math.sqrt(d.value);
                })
                .call(truncated_line);

            function truncated_line(l) {
                function len(d) {
                    return Math.sqrt(Math.pow((d.target.y - d.source.y), 2) +
                        Math.pow((d.target.x - d.source.x), 2));
                }
                l.attr('x1', function(d) {
                    return d.source.x +
                        (d.target.x - d.source.x) * d.source.r / len(d);
                });
                l.attr('y1', function(d) {
                    return d.source.y +
                        (d.target.y - d.source.y) * d.source.r / len(d);
                });
                l.attr('x2', function(d) {
                    return d.target.x +
                        (d.source.x - d.target.x) * d.target.r / len(d);
                });
                l.attr('y2', function(d) {
                    return d.target.y +
                        (d.source.y - d.target.y) * d.target.r / len(d);
                });
            }

            var node = svg.datum(root).selectAll(".node")
                .data(nodes)
                .enter().append("g")
                .attr("class", function(d) {
                    return d.children ? "node" : "leaf node";
                })
                .attr("transform", function(d) {
                    return "translate(" + d.x + "," + d.y + ")";
                });
            node.append("title")
                .text(function(d) {
                    return d.name + ": " + format(d.value) + "";
                });
            node.append("circle")
                .attr("r", function(d) {
                    return d.r;
                });
            node.append("text")
                .attr("dy", ".3em")
                .style("text-anchor", "middle")
                .text(function(d) {
                    return d.name;
                });

        });
} //main

var svg = d3.select(".chart")
    .attr("width", width + margin.right + margin.left)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


function unflatten(rows, rootName) {
    //    console.log("foo:", rows);
    var root = {
        name: rootName,
        children: [],
        childmap: {},
        value: 0,
        depth: 0
    };
    var allnodes = [];
    for (var i = 0; i < rows.length; i++) { // rows
        var row = rows[i];

        for (var c = 0, parent = root; c < names.length - 1; c++) { //cols
            var node, label = row[c];
            if (parent.name == row[c]) {
                console.log(parent.name);
                continue;
            }
            if (!parent.childmap[label]) {
                node = {
                    name: label,
                    children: [],
                    childmap: {},
                    parent: parent,
                    value: 0,
                    depth: parent.depth + 1
                };
                allnodes.push(node);
                if (!!label) {
                    parent.childmap[label] = node;
                    parent.children.push(node);
                }
            }
            if (c == names.length - 2) { // last column of names
                node.value = row[row.length - 1];
                // add value to all parents value;
                for (var p = parent; p; p = p.parent) {
                    p.value += node.value;
                }
            }
            if (!!label) {
                parent = parent.childmap[label];
            }
        }
    }
    // remove the children of leaf nodes
    allnodes.forEach(function(n, i, a) {
        if (n.children.length === 0) {
            n.size = n.value;
            delete n.children;
        }
    });
    return root;
};

//Raphael(function () {
//	  var r = Raphael("chart");
//    var galaxySet = r.set();
//    var circle = r.circle(50,50,20);
//    galaxySet.push(circle);
//});
