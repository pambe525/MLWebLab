/**
 * Function to be called when document is loaded
 */
function initialize() {
    $("#glass_pane").hide();
    if ( $("#msg_text").text() !== "None" ) showMsgBox();
    $("#msg_box_close").on( 'click', hideMsgBox );
    $("select[name='data_file']").on( 'change', fileSelectionChanged );
    $("#select_btn").on( 'click', selectButtonClicked );

    // NOT TESTED YET!
    $("#column_name_select").on('change', function(e){
        update_selected_column_summaries(data_summary, data_frame);
    });

    $("#train_btn").on('click', function (e) {
        $("#glass_pane").show();
    });

    $("select[name='n_splits']").on('change', function(e){
        set_training_summaries();
    })
}

function hideMsgBox() {
    $("#msg_box").addClass("invisible");
}

function showMsgBox() {
    $('#msg_box').removeClass("invisible");
}

function ajax_form_get(formId, successHandler) {
    var form = $("#"+formId);
    $.ajax({
        url: form.attr('action'),
        type: "POST",
        data: form.serialize(),
        dataType: 'json',
        success: successHandler
    });
}

function fileSelectionChanged() {
    if ($("#source_file").text() === $("select[name='data_file']").val() )
        $("#home_container").removeClass("invisible");
    else $("#home_container").addClass("invisible");
}

function selectButtonClicked() {
    if ($("select[name='data_file']")[0].selectedIndex !== 0) {
        $("#glass_pane").show();
        //ajax_form_get("file_select_form", loadFileData);
    }
}

function loadFileData(data) {
    alert("Hi");
}

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
                set_training_summaries(response);
            }
        },
   });
}

function update_selected_column_summaries(data_summary, data_frame) {
    var column_index = $("#column_name_select option:selected").val();
    var column_name = $("#column_name_select option:selected").text();
    load_selected_column_stats(column_index, data_summary);
    load_selected_column_head(column_name, data_frame);
    plot_column_histogram("column_histogram", column_name, data_frame);
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

function set_training_summaries(response) {
    var n_splits = parseInt($("#n_splits_select option:selected").text());
    var target_name = $("#target_feature").text();
    var mean_train_score = (response == null) ? "" : response["mean_train_score"].toFixed(2);
    var mean_test_score  = (response == null) ? "" : response["mean_test_score"].toFixed(2);
    var train_score_stdev = (response == null) ? "" : response["train_scores_stdev"].toFixed(2);
    var test_score_stdev  = (response == null) ? "" : response["test_scores_stdev"].toFixed(2);

    var train_scores = (response == null) ? null : response["train_scores"];
    var test_scores  = (response == null) ? null : response["test_scores"];
    var target_summary = data_summary[data_summary.length-1];
    var y_actual = (response == null) ? [target_summary['min'], target_summary['max']] : response["y"];
    var y_predict = (response == null) ? [] : response["y_predict"];
    $("#train_score").text(mean_train_score);
    $("#test_score").text(mean_test_score);
    $("#train_scores_stdev").text(train_score_stdev);
    $("#test_scores_stdev").text(test_score_stdev);

    plot_split_scores("cv_scores_plot", n_splits, train_scores, test_scores);
    plot_validation("validation_plot", target_name, y_actual, y_predict);
}
