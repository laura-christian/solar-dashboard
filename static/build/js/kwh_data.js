"use strict";

let ctx_bar = $('#kWhBarChart').get(0).getContext('2d');
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

function getkWhDataToday() {
    $.get('/solaroutput.json', {'timeframe': 'today'}, showkWhData);
    console.log("AJAX call sent");
}


$(document).ready(function(){
  getkWhDataToday();
  $('#today-button').addClass('active')
});