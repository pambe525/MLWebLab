//---------------------------------------------------------------------------------------------------------------------
// Validation Plot: Actual Target versus Predicted Target
//---------------------------------------------------------------------------------------------------------------------
function plot_validation(div_id, target_name, y_actual, y_predicted) {
    plot_div = document.getElementById(div_id);
    var trace1 = {x: y_actual, y: y_predicted, type: 'scatter', mode: 'markers', name: ""};
    var trace2 = {x: [Math.min.apply(null, y_actual),Math.max.apply(null, y_actual)],
                  y:[Math.min.apply(null, y_actual),Math.max.apply(null, y_actual)],
                  mode: 'lines', line:{color:'green', width:1}};
    var data = [trace1, trace2];
    var layout = {
      title: {
        text: '<b>Actual ' + target_name + " versus Predicted " + target_name +'</b>',
        font: {size: 16},
      },
      xaxis: {
          title: {text: '<b>Actual ' + target_name + '</b>', font: {size: 12}}, linecolor: '#666',
          linewidth: 2, mirror: true, ticks:"outside", zerolinecolor: "#999", zerolinewidth: 2
      },
      yaxis: {
          title: {text: '<b>Predicted ' + target_name + '</b>', font: {size: 12}}, linecolor: '#666',
          linewidth: 2, mirror: true, ticks:"outside", zerolinecolor: "#999", zerolinewidth: 2
      },
      margin: {l:80, r:10, t:50, b:50, pad:0}, showlegend: false
    };
    Plotly.newPlot(plot_div, data, layout, {displayModeBar: false});
}