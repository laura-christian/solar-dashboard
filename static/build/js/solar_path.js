"use strict";

let ctx_bar = $('#kWhBarChart').get(0).getContext('2d');


function renderBarGraph(results) {
  console.dir(results); // yay debugging!
  let kWhChart = new Chart(ctx_bar, {
    type: 'bar',
    data: {
      labels: results.labels,
      datasets: [{
        label: 'kwH',
        data: results.data,
        lineTension: 0,
        backgroundColor: "#26B99A"
      }]
    },
    options: {
      scales: {
        yAxes: [{
          ticks: {
            beginAtZero: true
          }
        }]
      },
      legend: {
        display: false,
      }
    }
  });
}


function getSolarPathData() {
    $.get('/solaroutput.json', {'timeframe': 'today'}, renderBarGraph);
    console.log("AJAX call sent");
}


getBarGraphData()