"use strict";

function showWeather(results) {

  console.dir(results)

  // First update values in weather widget
  let currentConditions = results.current.icon;
  let currentTemp = Math.round(results.current.temperature);
  let currentCloudCover = Math.round(results.current.cloudCover*100);

  let weatherSummaries = [[currentConditions, currentTemp, currentCloudCover]];

  for (let i = 0; i < 6; i += 1) {
    let icon = results.forecast[i].icon;
    let tempHigh = Math.round(results.forecast[i].temperatureHigh);
    let cloudCover = Math.round(results.forecast[i].cloudCover*100);
    weatherSummaries.push([icon, tempHigh, cloudCover]);
  }
  console.log(weatherSummaries); //For debugging purposes

  // For today's weather description, transform icon tag to simple summary 
  // (i.e., remove hyphens and capitalize)
  let mainDayConditions = weatherSummaries[0][0];
  mainDayConditions = mainDayConditions.split('-');
  for (var i = 0; i < mainDayConditions.length; i++) {
    mainDayConditions[i] = mainDayConditions[i].charAt(0).toUpperCase() + mainDayConditions[i].slice(1);
    }
  mainDayConditions = mainDayConditions.join(' ');
  $("#main-day-weather").html('<i>' + mainDayConditions + '</i>');

  // Now update forecast values
  $("#main-day-temp").html(weatherSummaries[0][1]+'&#176;');
  $("#main-day-cloudcover").html(weatherSummaries[0][2]+'&#37;');

  $("#day1-high").html(weatherSummaries[1][1]);
  $("#clcov-day1").html(weatherSummaries[1][2]+'&#37;');

  $("#day2-high").html(weatherSummaries[2][1]);
  $("#clcov-day2").html(weatherSummaries[2][2]+'&#37;');

  $("#day3-high").html(weatherSummaries[3][1]);
  $("#clcov-day3").html(weatherSummaries[3][2]+'&#37;');

  $("#day4-high").html(weatherSummaries[4][1]);
  $("#clcov-day4").html(weatherSummaries[4][2]+'&#37;');

  $("#day4-high").html(weatherSummaries[5][1]);
  $("#clcov-day4").html(weatherSummaries[5][2]+'&#37;');

  $("#day5-high").html(weatherSummaries[5][1]);
  $("#clcov-day5").html(weatherSummaries[5][2]+'&#37;');

  $("#day6-high").html(weatherSummaries[6][1]);
  $("#clcov-day6").html(weatherSummaries[6][2]+'&#37;');     

  // Finally, set weather icons and "press play"
  let weatherIcons = new Skycons({"color": "#73879C"});

  weatherIcons.set("main-weather-icon", weatherSummaries[0][0]);
  weatherIcons.set("icon-day1", weatherSummaries[1][0]);
  weatherIcons.set("icon-day2", weatherSummaries[2][0]);
  weatherIcons.set("icon-day3", weatherSummaries[3][0]);
  weatherIcons.set("icon-day4", weatherSummaries[4][0]);
  weatherIcons.set("icon-day5", weatherSummaries[5][0]);
  weatherIcons.set("icon-day6", weatherSummaries[6][0]);

  weatherIcons.play();
}

//This function polls DarkSky weather API via app server
function getWeather() {
    $.get('/weather.json', showWeather);
    console.log("AJAX call sent");
}

// Moment.js bases its notion of "today" on local host's clock; this function would
// potentially need to be modified if deployed on a server in a different timezone
function updateDays() {

  let mainDay = moment().format('dddd');
  mainDay = mainDay.toUpperCase()
  $("#main-weather-day").html('<b>' + mainDay + '</b>');

  let weatherDay1 = moment().add(1, 'days').format('ddd');
  $("#weather-day1").html(weatherDay1);

  let weatherDay2 = moment().add(2, 'days').format('ddd');
  $("#weather-day2").html(weatherDay2);

  let weatherDay3 = moment().add(3, 'days').format('ddd');
  $("#weather-day3").html(weatherDay3);

  let weatherDay4 = moment().add(4, 'days').format('ddd');
  $("#weather-day4").html(weatherDay4);

  let weatherDay5 = moment().add(5, 'days').format('ddd');
  $("#weather-day5").html(weatherDay5);

  let weatherDay6 = moment().add(6, 'days').format('ddd');
  $("#weather-day6").html(weatherDay6);

}

// Initialization function
$(document).ready(function(){
  updateDays();
  getWeather();
});
