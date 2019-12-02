//---------------------------------------------------------------------------------------------------------------------
// Validation Plot: Actual Target versus Predicted Target
//---------------------------------------------------------------------------------------------------------------------
function plotValidation(divId, targetName, yActual, yPredicted) {
    var newPlot = (yPredicted.length == 0);
    var plot = new PlotlyPlot(divId);
    plot.setTitle("Actual "+targetName+" versus Predicted "+targetName);
    plot.setXAxis("Actual "+targetName);
    plot.setYAxis("Predicted "+targetName);
    var xPoints = [Math.min.apply(null, yActual), Math.max.apply(null, yActual)];
    var yPoints = [Math.min.apply(null, yActual), Math.max.apply(null, yActual)];
    plot.addLinePlot(xPoints, yPoints, "gray");
    if ( !newPlot ) plot.addScatterPlot(yActual, yPredicted, "green");
    plot.show();
}

function plotSplitScores(divId, nSplits, trainScores, testScores) {
    var plot = new PlotlyPlot(divId);
    plot.setTitle("Scores at each split", 12);
    plot.setXAxis("Split #", 10);
    plot.setYAxis("Score", 10);
    var x_values = [];
    for (let i = 1; i <= nSplits; i++) x_values.push(i);
    if (trainScores == null) trainScores = new Array(nSplits);
    if (testScores == null) testScores = new Array(nSplits);
    plot.addLinePlot(x_values, trainScores, "lightblue", "Training", true);
    plot.addLinePlot(x_values, testScores, "orange", "Validation", true);
    plot.setLegend(1.05, 0.8);
    plot.show();
}

function plot_column_histogram(divId, columnName, columnValues) {
    let plotDiv = document.getElementById(divId);
    let trace = {
        x: columnValues, type: 'histogram',
        marker:{color:"rgba(100, 200, 102, 0.6)", line:{color:"rgba(100, 200, 102, 1.0)", width:1}},
    };
    var layout = {
        margin: {r:10, l:10, pad:0}, showlegend: false, bargap: 0.08, plot_bgcolor: 'lightyellow'
    };
    setPlotTitle(layout, "Histogram of Column Data");
    setXAxis(layout, columnName);
    Plotly.newPlot(plotDiv, [trace], layout, {displayModeBar: false});
}

function plotCorrelationHeatmap(divId, columnNames, corrMatrix) {
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
        plotCovariance("covariance_plot", xName, yName, xValues, yValues);
        $("#corr_coeff").text(data.points[0].z.toFixed(2));
    });
}

function plotCovariance(divId, xName, yName, xValues, yValues) {
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
        zerolinewidth: 2, tickfont:{size:10}, fixedrange: true};
    layout.xaxis.title = {text: xtitle, font: {size: 12}, standoff: 10};
    layout.margin.b = 50;
    return layout;
}

function setYAxis(layout, ytitle) {
    if (layout == null) layout = {};
    layout.yaxis = {linecolor: '#666', linewidth: 1, mirror: true, ticks:"outside", zerolinecolor: "#999",
        zerolinewidth: 2, tickfont:{size:10}, fixedrange: true};
    layout.yaxis.title = {text: ytitle, font: {size: 12}, standoff: 10};
    return layout;
}

/**-----------------------------------------------------------------------------------------------------------------
 * CLASS: PlotlyPlot
 */
class PlotlyPlot {
    constructor(divId) {
        this.plotDiv = document.getElementById(divId);
        this.layout = {};
        this.data = [];
        this.layout.yaxis = {title: {font:{size:0}}};
        this.layout.margin = {r:10, l:"auto"};
        this.layout.showlegend = false;
        this.layout.plot_bgcolor = "lightyellow";
    }
    setTitle(title, fontSize=15) {
        this.layout.title = {text: '<b>'+title+'</b>', font: {family:"Arial", size: fontSize}};
        this.layout.margin.t = 20 + fontSize;
    }
    setXAxis(xTitle, fontSize=12) {
        this.layout.xaxis = this._getAxisDefault();
        this.layout.xaxis.title = {text: xTitle, font: {size: fontSize}, standoff: 10};
        this.layout.margin.b = 38 + fontSize;
    }
    setYAxis(yTitle, fontSize=12) {
        this.layout.yaxis = this._getAxisDefault();
        this.layout.yaxis.title = {text: yTitle, font: {size: fontSize}, standoff: 10};
    }
    setLegend(xOffset, yOffset, fontSize=10) {
        this.layout.showlegend = true;
        this.layout.legend = {x: xOffset, y: yOffset, font: {size: fontSize}};
    }
    addHistogram(x) {

    }
    addLinePlot(xArray, yArray, lineColor, name="", hasPoints=false) {
        var trace = {x: xArray, y: yArray, mode: 'lines', line:{color:lineColor, width:2}, name:name};
        if (hasPoints) trace.mode = 'lines+markers';
        this.data.push(trace);
    }
    addScatterPlot(xArray, yArray, markerColor) {
        var trace = {x: xArray, y: yArray, type: 'scatter', mode: 'markers',
            name: "", marker:{color: markerColor, size:5}};
        this.data.push(trace);
    }
    show() {
        Plotly.newPlot(this.plotDiv, this.data, this.layout, {displayModeBar: false});
    }
    _getAxisDefault() {
        return {linecolor: '#666', linewidth: 1, mirror: true, ticks:"outside", zerolinecolor: "#999",
            zerolinewidth: 2, tickfont:{size:10}, fixedrange: true};
    }
}


