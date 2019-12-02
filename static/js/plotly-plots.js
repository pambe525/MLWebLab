/**--------------------------------------------------------------------------------------------------------------------
 * Validation Plot: Actual Target versus Predicted Target
 */
function plotValidation(divId, targetName, yActual, yPredicted) {
    var newPlot = (yPredicted.length === 0);
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

/**--------------------------------------------------------------------------------------------------------------------
 * Plot of K-Fold Split scores for each split
 */
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

/**--------------------------------------------------------------------------------------------------------------------
 * Histogram Plot for values in a Data Column
 */
function plotHistogram(divId, columnName, columnValues) {
    var plot = new PlotlyPlot(divId);
    plot.setTitle("Histogram of Column Data");
    plot.setXAxis(columnName);
    plot.setYAxis("Count");
    plot.addHistogram(columnValues);
    plot.show();
 }

 /**--------------------------------------------------------------------------------------------------------------------
 * Heatmap of correlation coefficients of data columns matrix
 */
function plotCorrelationHeatmap(divId, columnNames, corrMatrix) {
    var plot = new PlotlyPlot(divId);
    plot.setTitle("Correlation Coefficients Heat Map");
    var colorScaleValues = [[0, 'darkred'], [0.5, 'white'], [1.0, 'darkblue']];
    plot.addHeatMap(columnNames, columnNames, corrMatrix, colorScaleValues);
    plot.show();

    plot.plotDiv.on("plotly_click", function(data){
        var xName = data.points[0].x;
        var yName = data.points[0].y;
        var xValues = getColumnValues(xName);
        var yValues = getColumnValues(yName);
        plotCovariance("covariance_plot", xName, yName, xValues, yValues);
        $("#corr_coeff").text(data.points[0].z.toFixed(2));
    });
}

/**--------------------------------------------------------------------------------------------------------------------
 * Scatter plot of variance betwene two data columns
 */
function plotCovariance(divId, xName, yName, xValues, yValues) {
    var plot = new PlotlyPlot(divId);
    plot.setTitle("Variation of " +  yName + " with " + xName);
    plot.setXAxis(xName);
    plot.setYAxis(yName);
    plot.addScatterPlot(xValues, yValues);
    plot.show();
}

/**-----------------------------------------------------------------------------------------------------------------
 * CLASS: PlotlyPlot
 */
class PlotlyPlot {
    constructor(divId) {
        this.plotDiv = document.getElementById(divId);
        this.layout = {};
        this.data = [];
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
    addHistogram(xValues) {
        var trace = {x: xValues, type: 'histogram'};
        trace.marker = {color:"rgba(100, 200, 102, 0.6)", line:{color:"rgba(100, 200, 102, 1.0)", width:1}};
        this.data.push(trace);
        this.layout.bargap = 0.08;
        this.layout.margin.l = xValues.length.toString().length * 10 + 20;
    }
    addLinePlot(xArray, yArray, lineColor, name="", hasPoints=false) {
        var trace = {x: xArray, y: yArray, mode: 'lines', line:{color:lineColor, width:2}, name:name};
        if (hasPoints) trace.mode = 'lines+markers';
        this.data.push(trace);
        this.layout.margin.l = this._getMaxCharsInNumbers(yArray)*6 + 15;
    }
    addScatterPlot(xArray, yArray, markerColor) {
        var trace = {x: xArray, y: yArray, type: 'scatter', mode: 'markers',
            name: "", marker:{color: markerColor, size:5}};
        this.data.push(trace);
        this.layout.margin.l = this._getMaxCharsInNumbers(yArray)*6 + 15;
    }
    addHeatMap(xNames, yNames, zMatrix, colorScaleValues) {
        var trace = {type: 'heatmap', z: zMatrix, x: xNames, y: yNames, colorscale: colorScaleValues,
            zmin: -1.0, zmax: 1.0};
        trace.colorbar = {thickness: 20, tickfont:{size:10}};
        this.data = [trace];
        var maxCharCount = this._getMaxCharsInNames(yNames);
        this.layout.margin.l = maxCharCount * 6 + 12;
        this.layout.margin.b = maxCharCount * 4 + 15;
        this.layout.xaxis = this._getAxisDefault();
        this.layout.yaxis = this._getAxisDefault();
    }
    show() {
        Plotly.newPlot(this.plotDiv, this.data, this.layout, {displayModeBar: false});
    }
    _getAxisDefault() {
        return {linecolor: '#666', linewidth: 1, mirror: true, ticks:"outside", zerolinecolor: "#999",
            zerolinewidth: 2, tickfont:{size:10}, fixedrange: true};
    }
    _getMaxCharsInNames(namesArray) {
        var charCount = 0;
        for (let i = 0; i < namesArray.length; i++)
            if (namesArray[i].length > charCount) charCount = namesArray[i].length;
        return charCount;
    }
    _getMaxCharsInNumbers(numArray) {
        var maxCharCount = 6, charCount = 0;
        for (var i = 0; i < numArray.length; i++) {
            var len = (numArray[i]) ? numArray[i].toString().length : 0;
            if (charCount < len) charCount = len;
            if (charCount > maxCharCount) charCount = maxCharCount;
            if (charCount === maxCharCount) break;
        }
    }
}