"use strict";

let sunGauge;

function showDaylightDeets(results) { 
  console.dir(results); // For debugging purposes
  showDaylightStats(results)
  renderSolarGauge(results)
}

  function showDaylightStats(results) {
    
    $('#sunrise').text(results.sunrise);
    $('#sunset').text(results.sunset);
    $('#daylight').text(results.daylength);

    let zenith = results.zenith;
    zenith = zenith.toFixed(2);
    $('#zenith').html(zenith + '&#176;');

    $('#solar-noon').text(results.solar_noon);

  }

function renderSolarGauge(results) {
  sunGauge = new RadialGauge({
      renderTo: 'sun-gauge',
      width: 160,
      height: 160,
      minValue: -90,
      startAngle: 90,
      ticksAngle: 180,
      valueBox: true,
      maxValue: 90,
      majorTicks: [
          "-90",
          "-45",
          "0",
          "45",
          "90"
      ],
      minorTicks: 2,
      strokeTicks: true,
      highlights: [
          {
              "from": -90,
              "to": 0,
              "color": "#73879C"
          }
      ],
      colorPlate: "#fff",
      borderShadowWidth: 0,
      borders: false,
      needleType: "arrow",
      needleWidth: 2,
      needleCircleSize: 7,
      needleCircleOuter: true,
      needleCircleInner: false,
      animationDuration: 1500,
      animationRule: "linear",
      animationTarget: "plate"
  }).draw(); 

  sunGauge.value = results.elevation
}

function getDaylightDeetsToday() {
    $.get('/daylight_deets.json', {'timeframe': 'today'}, showDaylightDeets);
    console.log("AJAX call sent");
}

$(document).ready(function(){
  getDaylightDeetsToday();
});

setInterval(function(){$.get('/daylight_deets.json', {'timeframe': 'today'}, updateSolarGauge)}, 3000);