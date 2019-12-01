//---------------------------------------------------------------------------------------------------------------------
// Validation Plot: Actual Target versus Predicted Target
//---------------------------------------------------------------------------------------------------------------------
function plot_validation(divId, targetName, yActual, yPredicted) {
    var new_plot = (yPredicted.length === 0);
    var plot_div = document.getElementById(divId);
    var trace1 = {x: [Math.min.apply(null, yActual),Math.max.apply(null, yActual)],
                  y:[Math.min.apply(null, yActual),Math.max.apply(null, yActual)],
                  mode: 'lines', line:{color:'gray', width:1}};
    if ( !new_plot )
        var trace2 = {x: yActual, y: yPredicted, type: 'scatter', mode: 'markers', name: "",
                    marker:{color: 'green', size:5}};
    var data = new_plot ? [trace1] : [trace1, trace2];
    var layout = {margin: {r:20}, showlegend: false, plot_bgcolor: 'lightyellow'};
    setPlotTitle(layout, "Actual "+targetName+" versus Predicted "+targetName);
    setXAxis(layout, "Actual "+targetName);
    setYAxis(layout, "Predicted "+targetName);
    Plotly.newPlot(plot_div, data, layout, {displayModeBar: false});
}

function plot_split_scores(divId, nSplits, trainScores, testScores) {
    var plot_div = document.getElementById(divId);
    var x_values = [];
    for (var i = 1; i <= nSplits; i++) x_values.push(i);
    if (trainScores == null) trainScores = new Array(nSplits);
    if (testScores == null) testScores = new Array(nSplits);
    var trace1 = {x: x_values, y: trainScores, name:'Training '};
    var trace2 = {x: x_values, y: testScores, name:'Validation'};
    var data =[trace1, trace2];
    var layout = {
      margin: {r:10, pad:0}, showlegend: true, plot_bgcolor: 'lightyellow',
      legend: {x: 1.05, y: 0.7, font: {size: 10}}
    };
    setPlotTitle(layout, "Scores at each split");
    setXAxis(layout, "Split #");
    setYAxis(layout, "Score");
    Plotly.newPlot(plot_div, data, layout, {displayModeBar: false});
}

function plot_column_histogram(divId, columnName, columnValues) {
    let plot_div = document.getElementById(divId);
    let trace = {
        x: columnValues, type: 'histogram',
        marker:{color:"rgba(100, 200, 102, 0.6)", line:{color:"rgba(100, 200, 102, 1.0)", width:1}},
    };
    var layout = {
        margin: {r:10, l:10, pad:0}, showlegend: false, bargap: 0.08, plot_bgcolor: 'lightyellow'
    };
    setPlotTitle(layout, "Histogram of Column Data");
    setXAxis(layout, columnName);
    Plotly.newPlot(plot_div, [trace], layout, {displayModeBar: false});
}

function plot_correlation_heatmap(divId, columnNames, corrMatrix) {
    var plot = document.getElementById(divId);
    var colorScaleValues = [[0, 'darkred'], [0.5, 'white'], [1.0, 'black']];
    var data = [{type: 'heatmap', z: corrMatrix, x: columnNames, y: columnNames,
         colorscale: colorScaleValues, zmin: -1.0, zmax: 1.0}];
    var layout = {margin: {l:'auto', r:'auto', b:'auto'}};
    setPlotTitle(layout, "Correlation Coefficients Heat Map")
    Plotly.newPlot(divId, data, layout, {displayModeBar: false});

    plot.on("plotly_click", function(data){
        var xName = data.points[0].x;
        var yName = data.points[0].y;
        var xValues = getColumnValues(xName);
        var yValues = getColumnValues(yName);
        plot_covariance("covariance_plot", xName, yName, xValues, yValues);
    });
}

function plot_covariance(divId, xName, yName, xValues, yValues) {
    var trace1 = {x: xValues, y: yValues, type: 'scatter', mode: 'markers'};
    var data = [trace1];
    var layout = {margin:{r:10}, showlegend: false, plot_bgcolor: 'lightyellow'};
    setPlotTitle(layout, "Variation of " +  yName + " with " + xName);
    setXAxis(layout, xName);
    setYAxis(layout, yName);
    Plotly.newPlot(divId, data, layout, {displayModeBar: false});
}

/**
 * Utility functions
 */
function setPlotTitle(layout, title) {
    if (layout == null) layout = {};
    layout.title = {text: '<b>'+title+'</b>', font: {family:"Arial", size: 15}};
    layout.margin.t = 36;
    return layout;
}

function setXAxis(layout, xtitle) {
    if (layout == null) layout = {};
    layout.xaxis = {linecolor: '#666', linewidth: 1, mirror: true, ticks:"outside", zerolinecolor: "#999",
        zerolinewidth: 2, tickfont:{size:10}};
    layout.xaxis.title = {text: xtitle, font: {size: 12}, standoff: 10};
    layout.margin.b = 50;
    return layout;
}

function setYAxis(layout, ytitle) {
    if (layout == null) layout = {};
    layout.yaxis = {linecolor: '#666', linewidth: 1, mirror: true, ticks:"outside", zerolinecolor: "#999",
        zerolinewidth: 2, tickfont:{size:10}};
    layout.yaxis.title = {text: ytitle, font: {size: 12}, standoff: 10};
    return layout;
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
