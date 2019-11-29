//---------------------------------------------------------------------------------------------------------------------
// Validation Plot: Actual Target versus Predicted Target
//---------------------------------------------------------------------------------------------------------------------
function plot_validation(div_id, target_name, y_actual, y_predicted) {
    var new_plot = (y_predicted.length === 0);
    var plot_div = document.getElementById(div_id);
    var trace1 = {x: [Math.min.apply(null, y_actual),Math.max.apply(null, y_actual)],
                  y:[Math.min.apply(null, y_actual),Math.max.apply(null, y_actual)],
                  mode: 'lines', line:{color:'gray', width:1}};
    if ( !new_plot )
        var trace2 = {x: y_actual, y: y_predicted, type: 'scatter', mode: 'markers', name: "",
                    marker:{color: 'green', size:5}};
    var data = new_plot ? [trace1] : [trace1, trace2];
    var layout = {
      title: {
        text: '<b>Actual ' + target_name + " versus Predicted " + target_name +'</b>',
        font: {family:"Helvetica", size: 15}
      },

      xaxis: {
          title: {text: '<b>Actual ' + target_name + '</b>', font: {size: 11}}, linecolor: '#666',
          linewidth: 2, mirror: true, ticks:"outside", zerolinecolor: "#999", zerolinewidth: 2,
          tickfont:{size:10}
      },
      yaxis: {
          title: {text: '<b>Predicted ' + target_name + '</b>', font: {size: 11}}, linecolor: '#666',
          linewidth: 2, mirror: true, ticks:"outside", zerolinecolor: "#999", zerolinewidth: 2,
          tickfont:{size:10}
      },
      margin: {l:70, r:20, t:50, b:60}, showlegend: false,
      plot_bgcolor: 'lightyellow', paper_bgcolor: '#eee',
    };
    Plotly.newPlot(plot_div, data, layout, {displayModeBar: false});
}

function plot_split_scores(div_id, n_splits, train_scores, test_scores) {
    var plot_div = document.getElementById(div_id);
    var x_values = [];
    for (var i = 1; i <= n_splits; i++) x_values.push(i);
    if (train_scores == null) train_scores = new Array(n_splits);
    if (test_scores == null) test_scores = new Array(n_splits);
    var trace1 = {x: x_values, y: train_scores, name:'Training '};
    var trace2 = {x: x_values, y: test_scores, name:'Validation'};
    var data =[trace1, trace2];
    var layout = {
      xaxis: {
          title: {text: 'Split #', font: {size: 10}}, linecolor: '#666',
          linewidth: 1, mirror: true, ticks:"outside", zerolinecolor: "#999", zerolinewidth: 2,
          tickfont:{size:8}
      },
      yaxis: {
          title: {text: 'Score', font: {size: 10}}, linecolor: '#666',
          linewidth: 1, mirror: true, ticks:"outside", zerolinecolor: "#999", zerolinewidth: 2,
          tickfont:{size:8}
      },
      margin: {l:40, r:10, t:10, b:30, pad:0}, showlegend: true, plot_bgcolor: 'white',
      legend: {x: 1.05, y: 0.7, font: {size: 10}}
    };
    Plotly.newPlot(plot_div, data, layout, {displayModeBar: false});
}

function plot_column_histogram(div_id, column_name, column_values) {
    var plot_div = document.getElementById(div_id);
    var trace = {
        x: column_values, type: 'histogram',
        marker:{color:"rgba(100, 200, 102, 0.6)", line:{color:"rgba(100, 200, 102, 1.0)", width:1}},
    };
    var layout = {
        xaxis: {linecolor: '#888', linewidth: 1, mirror: true, ticks:"outside", tickfont:{size: 9},
                title: {text: column_name, font: {size: 12}}},
        yaxis: {linecolor: '#888', linewidth: 1, mirror: true, ticks:"outside", tickfont:{size: 9}},
        margin: {l:40, r:10, t:5, b:40, pad:0}, showlegend: false, bargap: 0.08, plot_bgcolor: 'lightyellow'
    };
    Plotly.newPlot(plot_div, [trace], layout, {displayModeBar: false});
}

function plot_correlation_heatmap(div_id, column_names, corr_matrix) {
    var plot = document.getElementById(div_id);
    var colorScaleValues = [[-1.0, "blue"], [0.0, 'white'], [1.0, 'orange']];
    var data = [{z: corr_matrix, x: column_names, y: column_names,
        type: 'heatmap', colorscale: colorScaleValues}];
    var layout = {
        margin: {l:120, t:30, r:5, b:'auto'}, autosize: true, width: 500,
        title: {text: 'Correlation Coefficients Heat Map', font: {family:"Arial", size: 20}},
    };
    Plotly.newPlot(div_id, data, layout, {displayModeBar: false});

    plot.on("plotly_click", function(data){
        var xName = data.points[0].x;
        var yName = data.points[0].y;
        var xValues = getColumnValues(xName);
        var yValues = getColumnValues(yName);
        plot_covariance("covariance_plot", xName, yName, xValues, yValues);
    });
}

function plot_covariance(div_id, xName, yName, xValues, yValues) {
    var trace1 = {x: xValues, y: yValues, type: 'scatter', mode: 'markers'};
    // if ( !new_plot )
    //     var trace2 = {x: y_actual, y: y_predicted, type: 'scatter', mode: 'markers', name: "",
    //                 marker:{color: 'green', size:5}};
    var data = [trace1];
    var layout = {
      title: {
        text: '<b>Variation of ' +  yName + ' with ' + xName + '</b>',
        font: {family:"Helvetica", size: 15}
      },

      xaxis: {
          title: {text: '<b>' + xName + '</b>', font: {size: 11}}, linecolor: '#666',
          linewidth: 2, mirror: true, ticks:"outside", zerolinecolor: "#999", zerolinewidth: 2,
          tickfont:{size:10}
      },
      yaxis: {
          title: {text: '<b>' + yName + '</b>', font: {size: 11}}, linecolor: '#666',
          linewidth: 2, mirror: true, ticks:"outside", zerolinecolor: "#999", zerolinewidth: 2,
          tickfont:{size:10}
      },
      margin: {l:70, r:20, t:50, b:60}, showlegend: false,
      plot_bgcolor: 'lightyellow', paper_bgcolor: '#eee',
    };
    Plotly.newPlot(div_id, data, layout, {displayModeBar: false});
}

/*
class PlotlyPlot {
    constructor() {
        this.layout = this.setLayout()
    }
    title(title, fontSize) {

    }
    xAxis(title, fontSize) {

    }
    yAxis(title, fontSize) {

    }
    legend(x, y, fontSize) {

    }
    addHistogram(x) {

    }
    addLinePlot(x, y, linecolor) {

    }
    addScatter(x, y, marker) {

    }
    newPlot(divId) {

    }
    updatePlot(divID) {

    }
}
*/
