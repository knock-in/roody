const Chart = require('chart.js');
const $ = require('jquery');
const moment = require('moment');
const annotations = require('chartjs-plugin-annotation');
const draggable = require('chartjs-plugin-draggable');
const _ = require('lodash');
require('semantic-ui-offline/semantic.min.css');
require('semantic-ui-offline/semantic.min.js');


moment.locale('de');

const timeoutMs = 3000;
const HOST = process.env.HOST || '192.168.43.103';

let lastUpdate = moment(moment().valueOf() - (1000 * 60));

function updateThread(charts) {
	// not a thread but anyways
	update(lastUpdate)
	.done(function(newest) {
		// We only want to update our lastUpdate if we actually had some new data
		lastUpdate = newest;
	})
	.always(function() {
		setTimeout(updateThread, timeoutMs);
	});
}

const common = {
	type: 'line',
	plugins: [annotations, draggable],
	data: {
		labels: [
		],
		datasets: [
			{
				label: 'Label',
				data: [],
				backgroundColor: 'rgba(255,255, 255,0.8)',
				pointBorderColor: 'rgba(0, 0, 0, 0.2)',
				fill: true,
				pointRadius: 3
			}
		]
	},
	options: {
		annotation: {
			annotations: [
				{
					type: 'line',
					mode: 'horizontal',
					scaleID: 'y-axis-0',
					value: 10,
					borderWith: 5,
					borderColor: 'white',
					draggable: true,
					onDrag: function(event) {
						updateLimit(event.subject.chart._key, event.subject.config.value);
					},
					onDragEnd: function(event) {
						updateLimit(event.subject.chart._key, event.subject.config.value, true);
					},
					label: {
						content: 'Notify',
						fontFamily: "Lato, 'Helvetica Neue', Arial, Helvetica, sans-serif",
						enabled: true
					}
				}
			]
		},
		responsive: false,
		legend: {
			labels: {
				fontFamily: "Lato, 'Helvetica Neue', Arial, Helvetica, sans-serif",
				fontColor: 'rgba(255, 255, 255, 0.8)',
				fontSize: 20,
				usePointStyle: true
			}
		},
		scales: {
			yAxes: [{
				ticks: {
					fontColor: 'rgba(255, 255, 255, 0.8)',
					fontFamily: "Lato, 'Helvetica Neue', Arial, Helvetica, sans-serif",
					fontSize: 14,
					callback: function(value, index, values) {
						return value + '°';
					},
					suggestedMin: 0,
					suggestedMax: 100
				}
			}],
			xAxes: [{
				type: 'time',
				distribution: 'linear',
				time: {
					max: moment(),
					min: moment() - 1000 * 60,
					round: true,
					minUnit: 'second',
					unit: 'second',
					stepSize: 5,
					tooltipFormat: 'HH:mm:ss',

				},
				ticks: {
					fontColor: 'rgba(255, 255, 255, 0.8)',
					fontFamily: "Lato, 'Helvetica Neue', Arial, Helvetica, sans-serif",
					fontSize: 14,			
				}
			}]
		}
	}
};

const chartsCfg = {
	temperature: {
		$el: $('#temperature'),
		options: {
			data: {
				datasets: [{
					label: 'Temperature',
					backgroundColor: 'rgba(255,0,0,0.8)'
				}]
			},
			options: {
				scales: {
					yAxes: [{
						ticks: {
							callback: function(value, index, values) {
								return value + 'C';
							},
							suggestedMin: -20,
							suggestedMax: 75
						}
					}]
				}
			}
		}
	},
	humidity: {
		$el: $('#humidity'),
		options: {
			data: {
				datasets: [{
					label: 'Humidity',
					backgroundColor: 'rgba(79,172,254,1)'
				}]
			},
			options: {
				scales: {
					yAxes: [{
						ticks: {
							callback: function(value, index, values) {
								return value + '%';
							},
							suggestedMin: 0,
							suggestedMax: 100
						}
					}]
				}
			}
		}

	},
	carbonous: {
		$el: $('#carbonous'),
		options: {
			data: {
				datasets: [{
					label: 'Carbonous',
					backgroundColor: 'rgba(189, 145, 101, 0.57)'
				}]
			},
			options: {
				scales: {
					yAxes: [{
						ticks: {
							callback: function(value, index, values) {
								return value + 'ppm';
							},
							suggestedMin: 0,
							suggestedMax: 150
						}
					}]
				}
			}
		}
	},
	smoke: {
		$el: $('#smoke'),
		options: {
			data: {
				datasets: [{
					label: 'Smoke',
					backgroundColor: 'rgba(255,255,255,1)'
				}]
			},
			options: {
				scales: {
					yAxes: [{
						ticks: {
							callback: function(value, index, values) {
								return value + 'ppm';
							},
							suggestedMin: 0,
							suggestedMax: 150
						}
					}]
				}
			}
		}
	}
};

function toCharts(config) {
	return new Chart(config.$el, _.defaultsDeep({}, config.options, common));
}

function update(since) {
	const deferred = $.Deferred();
	$.ajax({
		url: 'http://' + HOST + ':5000' + '?since=' + since.toISOString()
	}).done(function(data) {
		const newest = _
			.chain(data)
			.forEach(function(entry) {
				_.forEach(chartsCfg, function(value, key) {
					charts[key].data.datasets[0].data.push({ x: moment.utc(entry.time_stamp).utcOffset(1), y: entry[key] });				
				});
			})
			.last()
			.value();
		
		const min = moment() - (1000 * 60);
		const max = moment();
		_.forEach(chartsCfg, function(value, key) {
			charts[key].options.scales.xAxes[0].time.min = min;
			charts[key].options.scales.xAxes[0].time.max = max;
			charts[key].update(0);
		});


		if(!data.length) {
			return deferred.reject();
		}

		delete data;
		return deferred.resolve(moment.utc(newest.time_stamp).utcOffset(1));
	});

	return deferred.promise();
}

function updateLimit(chart, limit, sync) {
	const value = limit.toFixed(2);
	charts[chart].config.options.annotation.annotations[0].value = value;
	charts[chart].config.options.annotation.annotations[0].label.content = 'Notify at: ' + value;

	if (!sync) {
		return
	}
	$.ajax({
		type: 'PUT',
		url: 'http://' + HOST + ':5000/limits',
		contentType: 'application/json',
		data: JSON.stringify({ [chart]: value })
	}).then(function(res) {
		console.log(res);
	});
}

const charts = _
	.chain(chartsCfg)
	.mapValues(toCharts)
	.forEach(function(chart, key) {
		chart.canvas.style.display = 'inline';
		chart._key = key;
	})
	.value();

$('.menu .item').tab();


$.ajax({ url: 'http://' + HOST + ':5000/limits' })
.done(function(limits) {
	_.forEach(limits, function(limit, chart) {
		updateLimit(chart, limit, false);
	});
	console.log(charts);
	updateThread();
});


