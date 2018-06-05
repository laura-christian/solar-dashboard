"use strict";

let ctx_bar = $('#kWh-bar-chart').get(0).getContext('2d');
let kWhChart;

function showkWhData(results) {
    renderBarGraph(results);
    updateTiles(results);
}

  function updateTiles(results) {

    let totalkWh = results['total_kWh'];

    let treesPlanted = totalkWh*.019;
      if (treesPlanted < 1) {
        treesPlanted = treesPlanted.toFixed(1);    
    } else {
        treesPlanted = Math.round(treesPlanted);
    }
    $("#trees-planted").html(treesPlanted);

    let milesDriven = totalkWh*1.8;
    milesDriven = Math.round(milesDriven);
    $("#miles-driven").text(milesDriven);

    let gallonsGas = totalkWh*.084;
    gallonsGas = Math.round(gallonsGas);
    $("#gallons-gas").text(gallonsGas);

    let poundsCoal = totalkWh*.814;
    poundsCoal = Math.round(poundsCoal);
    $("#pounds-coal").text(poundsCoal);
  }

  function renderBarGraph(results) {
    console.dir(results); // yay debugging!
    kWhChart = new Chart(ctx_bar, {
      type: 'bar',
      data: {
        labels: results.labels,
        datasets: [{
          label: '',
          data: results.primary_data,
          lineTension: 0,
          backgroundColor: "#26B99A"
        }]
      },
      options: {
        legend: {
          display: false,
        },
        scales: {
          yAxes: [{
            ticks: {
              beginAtZero: true
            }
          }]
        },
        tooltips: {
          callbacks: {
            label: function(tooltipItem, data) {
              let label = data.datasets[tooltipItem.datasetIndex].label || '';
              if (label) {
                  label += ': ';
              }
              label += tooltipItem.yLabel + ' kWh';
              return label;
            }
          }
        }
      }
    });
  }

function getkWhDataToday() {
    $.get('/solaroutput.json', {'timeframe': 'today', 'comparative': false}, showkWhData);
    console.log("AJAX call sent");
}


$(document).ready(function(){
  getkWhDataToday();
  $('#today-button').addClass('active');
});