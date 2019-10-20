$().ready(function() {

    if ($("#msg_text").text() !== "None") $('#msg_box').show();
    else $("#msg_box").hide();
    $("#glass_pane").hide();

    $("#msg_box_close").on('click', function () {
        $("#msg_box").hide();
    });

    $("#datafile_form").on('submit', function () {
        if ($(document.activeElement).attr('name') === "train_btn") $("#glass_pane").show();
    });

    $("#sidebar_form").on('submit', function (e) {
        if ($(document.activeElement).attr('name') === "train_btn") $("#glass_pane").show();
    });

})

function ajaxTrainRequest() {
    var form = $("#sidebar_form");
    try {
        $.ajax({
            url: form.attr('action'),
            type: "GET",
            data: form.serialize(),
            dataType: 'json',
            success: function(response) {
                if (response["error_message"] != "None") {
                    $("#msg_text").text(response["error_message"]);
                    $("#msg_box").show();
                } else {
                    target_name = $("#target_feature").text();
                    $("#train_score").text(response["train_score"].toFixed(2));
                    $("#test_score").text(response["test_score"].toFixed(2));
                    $("#train_scores_stdev").text(response["train_scores_stdev"].toFixed(2));
                    $("#test_scores_stdev").text(response["test_scores_stdev"].toFixed(2));
                    plot_validation("validation_plot", target_name, response["y"], response["y_predict"]);
                    $("#nav-validate-tab").removeClass('disabled');
                    $("#nav-validate-tab").click();
                }
            },
            error: function(xhr, status, error) {
                alert(xhr.responseText);
            }
       });
    } catch(e) {
        alert(e);
    }
}

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
        font: {family:'Helvetica', size: 16},
      },
      xaxis: {
        title: {
          text: '<b>Actual ' + target_name + '</b>',
          font: {size: 12},
        },
        linecolor: '#666', linewidth: 2, mirror: true,
        ticks:"outside",
          zerolinecolor: "#999",
          zerolinewidth: 2
      },
      yaxis: {
        title: {
          text: '<b>Predicted ' + target_name + '</b>',
          font: {size: 12},
        },
        linecolor: '#666', linewidth: 2, mirror: true,
        ticks:"outside",
        zerolinecolor: "#999",
        zerolinewidth: 2
      },
      margin: {l:80, r:10, t:50, b:50, pad:0},
      showlegend: false,
    };
    Plotly.newPlot(plot_div, data, layout, {displayModeBar: false});
}