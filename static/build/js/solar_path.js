"use strict";

function showSolarPathData(results) {
  console.dir(results); // For debugging purposes
  
  $('#sunrise').text(results.sunrise);
  $('#sunset').text(results.sunset);
  $('#daylight').text(results.daylength);

  let zenith = results.zenith;
  zenith = zenith.toFixed(2);
  $('#zenith').html(zenith + '&#176;');

  $('#solar-noon').text(results.solar_noon);

  //Define solar 'gauge' settings
  let gaugeSettings = {
      angle: 0,
      lineWidth: 0.4,
      pointer: {
        length: 0.75,
        strokeWidth: 0.042,
        color: '#1D212A'
      },
      limitMax: 'false',
      colorStart: '#1ABC9C',
      colorStop: '#1ABC9C',
      strokeColor: '#F0F3F3',
      generateGradient: true,
      renderTicks: {
        divisions: 2,
        divWidth: 1.1,
        divLength: 0.7,
        divColor: '#333333',
        subDivisions: 2,
        subLength: 0.5,
        subWidth: 0.6,
        subColor: '#666666'
      },
      staticLabels: {
        font: "10px sans-serif",  // Specifies font
        labels: [0],  // Print labels at these values
        color: "#000000",  // Optional: Label text color
      },      
  };

  // Render solar 'gauge'
  let sunGaugeElement = document.getElementById('sun-gauge');
  let sunGauge = new Gauge(sunGaugeElement).setOptions(gaugeSettings);

  sunGauge.maxValue = 90;
  sunGauge.setMinValue(-90)
  sunGauge.animationSpeed = 32;
  sunGauge.set(results.elevation);
  sunGauge.setTextField(document.getElementById('gauge-text'));
  }

function getSolarPathDataToday() {
    $.get('/solarpath.json', {'timeframe': 'today'}, showSolarPathData);
    console.log("AJAX call sent");
}


$(document).ready(function(){
  getSolarPathDataToday();
});