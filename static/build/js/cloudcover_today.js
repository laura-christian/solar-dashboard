"use strict";

let ctx_line = $('#cloud-cover-chart').get(0).getContext('2d');
let cloudChart;

function showCloudCover(results) {
    console.dir(results);
    cloudChart = new Chart(ctx_line, {
    type: 'line',
    data: {
      labels: results.labels,
      datasets: [{
      label: '% cloudy',
      backgroundColor: "rgba(3, 88, 106, 0.3)",
      borderColor: "rgba(3, 88, 106, 0.70)",
      pointBorderColor: "rgba(3, 88, 106, 0.70)",
      pointBackgroundColor: "rgba(3, 88, 106, 0.70)",
      pointHoverBackgroundColor: "#fff",
      pointHoverBorderColor: "rgba(151,187,205,1)",
      pointBorderWidth: 1,
      data: results.primary_data
      }]
    },
    options: {
      scales: {
        yAxes: [{
          scaleLabel: {
            display: true,
            labelString: 'Percentage'
          }
        }]
      }     
    }
  });
}

function getCloudCoverToday() {
    $.get('/cloudcover_today.json', {'comparative': false}, showCloudCover);
    console.log("AJAX call sent");
}


$(document).ready(function(){
  getCloudCoverToday();
});

$('#today-button').on('click', getCloudCoverToday);