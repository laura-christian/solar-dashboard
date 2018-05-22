"use strict";

let ctx_line = $('#cloudCoverChart').get(0).getContext('2d');
let cloudChart;

function showCloudCover(results) {
    console.dir(results);
    cloudChart = new Chart(ctx_line, {
    type: 'line',
    data: {
      labels: results.labels,
      datasets: [{
      label: "% cloudcover",
      backgroundColor: "rgba(3, 88, 106, 0.3)",
      borderColor: "rgba(3, 88, 106, 0.70)",
      pointBorderColor: "rgba(3, 88, 106, 0.70)",
      pointBackgroundColor: "rgba(3, 88, 106, 0.70)",
      pointHoverBackgroundColor: "#fff",
      pointHoverBorderColor: "rgba(151,187,205,1)",
      pointBorderWidth: 1,
      data: results.data
      }]
    },
    // options: {
    //   scales: {
    //     xAxes: [{
    //       type: 'time',
    //         ticks: {
    //             autoSkip: true
    //         }
    //     }]
    //   }
    // }
  });
}

function getCloudCoverToday() {
    $.get('/cloudcover_today.json', showCloudCover);
    console.log("AJAX call sent");
}


$(document).ready(function(){
  getCloudCoverToday();
});

$('#today-button').on('click', getCloudCoverToday)