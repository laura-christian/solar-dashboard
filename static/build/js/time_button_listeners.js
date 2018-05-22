"use strict";

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


///////////////////////////  Ajax calls for all graph updates  //////////////////////////

// function getSolarPathData(evt) {

// 	let payload3 = {
// 	  'timeframe': $(this).val()
// 	  };
// 	  console.dir(payload);

//   $.get('/solarpath.json', payload, updateSolarPathData);

// }




$(document).on('click', '.time-button', function() {
    
    let buttonVal = $(this).attr('value');
    console.log(buttonVal)
    let payload = {
    	'timeframe': buttonVal
    	};
    
    $.get('/solaroutput.json', payload, updatekWhData);
    $.get('/cloudcover_averages.json', payload, updateCloudCover);

});