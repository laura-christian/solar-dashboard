"use strict";

function showWeather(results) {
    console.dir(results)
    // renderBarGraph(results);
    // updateTiles(results);
}

  // function updateTiles(results) {

  //   let totalkWh = results['total_kWh']

  //   let treesPlanted = totalkWh*.019
  //     if (treesPlanted < 1) {
  //       treesPlanted = treesPlanted.toFixed(1);    
  //   } else {
  //       treesPlanted = Math.round(treesPlanted);
  //   }
  //   $("#trees-planted").html(treesPlanted)

  //   let milesDriven = totalkWh*1.8
  //   milesDriven = milesDriven.toFixed(1)
  //   $("#miles-driven").html(milesDriven)

  //   let gallonsGas = totalkWh*.084
  //   gallonsGas = gallonsGas.toFixed(1)
  //   $("#gallons-gas").html(gallonsGas)

  //   let poundsCoal = totalkWh*.814
  //   poundsCoal = poundsCoal.toFixed(1)
  //   $("#pounds-coal").html(poundsCoal)
  // }

  // function renderBarGraph(results) {
  //     console.dir(results); // yay debugging!
  //     let kWhChart = new Chart(ctx_bar, {
  //       type: 'bar',
  //       data: {
  //         labels: results.labels,
  //         datasets: [{
  //           label: 'kwH',
  //           data: results.data,
  //           lineTension: 0,
  //           backgroundColor: "#26B99A"
  //         }]
  //       },
  //       options: {
  //         scales: {
  //           yAxes: [{
  //             ticks: {
  //               beginAtZero: true
  //             }
  //           }]
  //         },
  //         legend: {
  //           display: false,
  //         }
  //       }
  //     });

  // }

function getWeather() {
    $.get('/weather.json', showWeather);
    console.log("AJAX call sent");
}


getWeather()