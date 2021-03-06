"use strict";

function updateSolarArcGraph(results) {
  
  let newLabels = [];
  for (let dt of results.labels) {
    newLabels.push(moment(dt).format(results.format));
  }

  let newData = results.data;
  let newXAxisFormat = results.format;
  let newYAxisLabel = results.yAxisLabel;

  solarArcGraph.data.labels = newLabels;
  solarArcGraph.data.datasets[0].data = newData;
  solarArcGraph.options.scales.yAxes[0].scaleLabel.labelString = newYAxisLabel;
  solarArcGraph.update();
}

function pushPullCloudCover(results) {
  console.dir(results);
  let newLabels = results.labels
  let priorYearData = results.prior_y_data;
  let secondDataset = {
        label: "Prior Year",
        backgroundColor: "#CFD4D8",
        borderColor: "#BDC3C7",
        pointBorderColor: "#BDC3C7",
        pointBackgroundColor: "#BDC3C7",
        pointHoverBackgroundColor: "#fff",
        pointHoverBorderColor: "#BDC3C7",
        pointBorderWidth: 1,
        data: priorYearData
        };

  if ($('#compare-button').hasClass('active') && cloudChart.data.datasets.length === 1) {
    cloudChart.data.labels = newLabels;
    cloudChart.data.datasets[0].label = 'Curr Selection';
    cloudChart.data.datasets.push(secondDataset);
    cloudChart.options.legend.display = true
  }
  else if (!$('#compare-button').hasClass('active') && cloudChart.data.datasets.length === 2) {
    cloudChart.data.datasets.pop();
    cloudChart.options.legend.display = false;
    cloudChart.data.datasets[0].label = '';
  }
  cloudChart.update();
}

function pushPullkWhData(results) {
  console.dir(results);
  let newLabels = results.labels
  let priorYearData = results.prior_y_data;
  let secondDataset = {
        label: 'Prior Year',
        backgroundColor: "#03586A",
        data: priorYearData
        };
  console.dir(secondDataset);

  if ($('#compare-button').hasClass('active') && kWhChart.data.datasets.length === 1) {
    kWhChart.data.labels = newLabels;
    kWhChart.data.datasets[0].label = 'Curr Selection';
    kWhChart.data.datasets.push(secondDataset);
    kWhChart.options.legend.display = true;
  }
  else if (!$('#compare-button').hasClass('active')) {
    kWhChart.data.datasets.pop();
    kWhChart.options.legend.display = false;
    kWhChart.data.datasets[0].label = '';
  }
  kWhChart.update(); 
}

function updateCloudCover(results) {
  console.dir(results)

  let newLabels = results.labels;
  let newData = results.primary_data;
  let secondDatasetData = results.prior_y_data

  cloudChart.data.labels = newLabels;
  cloudChart.data.datasets[0].data = newData;
  if ($('#compare-button').hasClass('active') && cloudChart.data.datasets.length === 2) {
    cloudChart.data.datasets[1].data = secondDatasetData;
  } 
  cloudChart.update();
}

function updatekWhData(results) {
  console.dir(results)
  updateBarGraph(results);
  updateTiles(results);
}

  function updateBarGraph(results) {
    
    let newLabels = results.labels;
    let newData = results.primary_data;
    let secondDatasetData = results.prior_y_data

    kWhChart.data.labels = newLabels;
    kWhChart.data.datasets[0].data = newData;
    if ($('#compare-button').hasClass('active') && kWhChart.data.datasets.length === 2) {
      kWhChart.data.datasets[1].data = secondDatasetData;
    }
    kWhChart.update();

  }

function refreshData() {

    let comparative;
    if ($('#compare-button').hasClass('active')) {
      comparative = 'true';
    }
    else {
      comparative = 'false';
    }
    let buttonVal = $('.time-button.active').attr('value');
    console.log(buttonVal);
    let payload = {
      'timeframe': buttonVal, 'comparative': comparative
      };

    if (event.target.id === 'compare-button') {
      console.log(event.target.id)
      if (buttonVal === 'today') {
        $.get('/solaroutput.json', payload, pushPullkWhData);
        $.get('/cloudcover_today.json', payload, pushPullCloudCover);
      }
      else {
        $.get('/solaroutput.json', payload, pushPullkWhData);
        $.get('/cloudcover_averages.json', payload, pushPullCloudCover);     
      }      
    }
    else {
      if (buttonVal === 'today') {
        console.dir(payload)
        $.get('/solaroutput.json', payload, updatekWhData);
        $.get('/cloudcover_today.json', payload, updateCloudCover);
        $.get('/solar_arc.json', payload, showSolarArcGraph);
      }
      else {
        $.get('/solaroutput.json', payload, updatekWhData);
        $.get('/cloudcover_averages.json', payload, updateCloudCover);
        $.get('/solar_arc.json', payload, updateSolarArcGraph);     
      }
    }
}

$('.time-button').on('click', function(evt) {
    $('.time-button').removeClass('active');
    $(this).addClass('active')
    refreshData();
});

$('#compare-button').on('click', function() {
  $('#compare-button').toggleClass('active');
  console.log('compare-button clicked');
  refreshData();
});