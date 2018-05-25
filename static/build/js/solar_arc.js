"use strict";

let ctx_line2 = $('#solar-arc-graph').get(0).getContext('2d');
let solarArcGraph;

function showSolarArcGraph(results) {
    console.dir(results);

    let labels = [];

    for (let dt of results.labels) {
      labels.push(moment(dt).format(results.format))
    }
    console.log(labels)

    solarArcGraph = new Chart(ctx_line2, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
      label: 'Elevation (Degrees)',
      backgroundColor: "rgba(38, 185, 154, 0.31)",
      borderColor: "rgba(38, 185, 154, 0.7)",
      pointBorderColor: "rgba(38, 185, 154, 0.7)",
      pointBackgroundColor: "rgba(38, 185, 154, 0.7)",
      pointHoverBackgroundColor: "#fff",
      pointHoverBorderColor: "rgba(220,220,220,1)",
      pointBorderWidth: 1,
      data: results.data
      }]
    },
    options: {
      scales: {
        yAxes: [{
          scaleLabel: {
            display: true,
            labelString: results.yAxisLabel
          }
        }]
      }     
    }
  });
}

function getSolarArcDataToday() {
    $.get('/solar_arc.json', {'timeframe': 'today'}, showSolarArcGraph);
    console.log("AJAX call sent");
}

$(document).ready(function(){
  getSolarArcDataToday();
});