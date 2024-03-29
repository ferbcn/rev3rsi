var width = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
var height = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
var text_size;

if (width>1200)
  text_size = "200px";
else if (width > 600)
  text_size = "90px";
else
  text_size = "40px";

//var text_color = "#495057";
var text_color = "white";
var color = "white";
const svg = d3.select('#svg');
var run = true;
var circle;
var myText;
var colors = ["white", "white", "white", "blue", "green"]

var text_content = "rev3rsi"

document.addEventListener('DOMContentLoaded', () => {
  window.setTimeout(function(){run = false;move_text();window.setTimeout(function(){svg.selectAll("circle").remove();}, 1000);}, 2000);});

window.onclick = () => {
  if (!run){
    run = true;
    window.setTimeout(function(){run = false;window.setTimeout(function(){svg.selectAll("circle").remove();}, 1000);}, 2000);
  }
};

window.onresize = () => {

  width = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
  height = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
  if (width>1200)
    text_size = "200px";
  else if (width > 600)
    text_size = "100px";
  else
    text_size = "60px";
  if (!run){
    run = true;
    window.setTimeout(function(){run = false;move_text();window.setTimeout(function(){svg.selectAll("circle").remove();}, 1000);}, 2000);
  }
  else {
    svg.selectAll("*").remove()
    window.setTimeout(function(){run = false;move_text();window.setTimeout(function(){svg.selectAll("circle").remove();}, 1000);}, 2000);
  }
};

const frameRate = 100;
const refreshRate = 1000/frameRate;
window.setInterval(() => {
  if (run){
    create();
    move();
  }
}, refreshRate);


function create(){
  myText =  svg.append("text")
    .attr("y", height / 2)//magic number here
    .attr("x", width / 2)
    .attr('text-anchor', 'middle')
    .attr("class", "myLabel")//easy to style with CSS
    .text(text_content)
    .style('fill', text_color)
    .style("font-weight", "bold")
    .style("text-shadow", "100px")
    .style("font-size", "0px");

    x_pos = Math.floor((Math.random() * width) + 1);
    y_pos = Math.floor((Math.random() * height) + 1);
    size = Math.floor((Math.random() * 50) + 1);
    circle = svg.append('circle')
       .attr('cx', width/2)
       .attr('cy', height/2)
       .attr('r', 1)
       .attr('real_size', size)
       .style('fill', colors[Math.floor((Math.random() * 4) + 1)]);

}

function move_text() {
  myText.transition()
   .duration(1000)
   .style("font-size", text_size);
}

function move() {
    //color = "#"+((1<<24)*Math.random()|0).toString(16).slice(-6);
    //x_pos = Math.floor((Math.random() * width) + 1);
    //y_pos = Math.floor((Math.random() * height) + 1);
    //r = R * sqrt(random())
    a = Math.random() * 2 * Math.PI;
    r = Math.max(width, height);
    // If you need it in Cartesian coordinates
    x_pos = Math.floor(width/2 + r * Math.cos(a));
    y_pos = Math.floor(height/2 + r * Math.sin(a));

    var size = parseInt(circle.attr('real_size'));

    circle.transition()
     .duration(2000)
     .attr('cx', x_pos)
     .attr('cy', y_pos)
     .attr('r', size)
     .style('fill', color);
 }
