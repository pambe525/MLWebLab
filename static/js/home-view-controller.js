$().ready(function() {

    $("#glass_pane").hide();
    if ($("#msg_text").text() !== "None") $('#msg_box').removeClass("invisible");
    else $("#msg_box").addClass("invisible");

    $("#msg_box_close").on('click', function () {
        $("#msg_box").addClass("invisible");
    });

    $("#column_name_select").on('change', function(e){
        update_selected_column_summaries(data_summary, data_frame);
    });

    $("#train_btn").on('click', function (e) {
        $("#glass_pane").show();
    });

})

function ajaxTrainRequest() {
    var form = $("#sidebar_form");
    $.ajax({
        url: form.attr('action'),
        type: "GET",
        data: form.serialize(),
        dataType: 'json',
        success: function(response) {
            $("#glass_pane").hide();
            if (response["error_message"] !== "None") {
                $("#msg_text").text(response["error_message"]);
                $("#msg_box").removeClass("invisible");
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
   });
}

function update_selected_column_summaries(data_summary, data_frame) {
    var column_index = $("#column_name_select option:selected").val();
    var column_name = $("#column_name_select option:selected").text();
    load_selected_column_stats(column_index, data_summary);
    load_selected_column_head(column_name, data_frame);
    plot_column_histogram("column_histogram", column_name, data_frame)
}

function load_selected_column_stats(column_index, data_summary) {
    $("#column_type").text(data_summary[column_index]['type']);
    $("#column_min").text(data_summary[column_index]['min']);
    $("#column_max").text(data_summary[column_index]['max']);
    $("#column_mean").text(data_summary[column_index]['mean']);
    $("#column_std").text(data_summary[column_index]['stdev']);
}

function load_selected_column_head(column_name, data_frame) {
    $("#col_row1").text(data_frame[column_name][0]);
    $("#col_row2").text(data_frame[column_name][1]);
    $("#col_row3").text(data_frame[column_name][2]);
    $("#col_row4").text(data_frame[column_name][3]);
    $("#col_row5").text(data_frame[column_name][4]);
}