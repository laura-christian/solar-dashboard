"use strict";

function updateSolarGauge(results) {
	sunGauge.value = results.elevation
}

function updateSolarArcGraph(results) {
	
	let newLabels = [];
  for (let dt of results.labels) {
    newLabels.push(moment(dt).format(results.format))
  }
  console.log(newLabels)

	let newData = results.data;
	let newXAxisFormat = results.format
	let newYAxisLabel = results.yAxisLabel

	solarArcGraph.data.labels = newLabels;
	solarArcGraph.data.datasets[0].data = newData;
	solarArcGraph.options.scales.yAxes[0].scaleLabel.labelString = newYAxisLabel;
	solarArcGraph.update();

}

function updateCloudCover(results) {

	let newLabels = results.labels;
	let newData = results.data;

	cloudChart.data.labels = newLabels;
	cloudChart.data.datasets[0].data = newData;
	cloudChart.update()

}

function updatekWhData(results) {
  updateBarGraph(results);
  updateTiles(results);
}

	function updateBarGraph(results) {
		
		let newLabels = results.labels;
		let newData = results.data;

		kWhChart.data.labels = newLabels;
		kWhChart.data.datasets[0].data = newData;
		kWhChart.update();

	}

$(document).on('click', '.time-button', function() {
    
    let buttonVal = $(this).attr('value');
    console.log(buttonVal)
    let payload = {
    	'timeframe': buttonVal
    	};

    if (buttonVal === 'today') {
    	$.get('/solaroutput.json', payload, updatekWhData);
    	$.get('/cloudcover_today.json', updateCloudCover);
    	$.get('/solar_arc.json', payload, showSolarArcGraph);
    }
    else {
	    $.get('/solaroutput.json', payload, updatekWhData);
	    $.get('/cloudcover_averages.json', payload, updateCloudCover);
	    $.get('/solar_arc.json', payload, updateSolarArcGraph);    	
    }
});

$('#compare-button').on('click', function() {
	$('#compare-button').toggleClass('active');	
});