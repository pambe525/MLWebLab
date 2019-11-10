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
    $("#train_btn").on('click', function (e) {
        $("#glass_pane").show();
    });

    $("select[name='n_splits']").on('change', function(e){
        set_training_summaries();
    });
}

function errorOccurred(response) {
    return (response["error_message"] !== null);
}

function hideMsgBox() {
    $("#msg_box").addClass("invisible");
}

function showMsgBox(message) {
    if (message !== null) $("#msg_text").text(message);
    $('#msg_box').removeClass("invisible");
}

function ajax_form_get(formId, successHandler) {
    var form = $("#"+formId);
    $.ajax({
        url: form.attr('action'),
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
        ajax_form_get("file_select_form", displayFileData);
    }
    return false;
}

function displayFileData(response) {
    $("#glass_pane").hide();
    if ( errorOccurred(response) )
        showMsgBox(response["error_message"]);
    else {
        hideMsgBox();
        updateDataFileSummary(response);
        $("#nav-summary-tab").click();
        $("#home_container").removeClass("invisible");
    }
}

function updateDataFileSummary(response) {
    $("#source_file").text(response['file_name']);
    $("#source_rows").text(response['data_file_rows']);
    $("#source_cols").text(response['data_file_cols']);
    //loadColumnStats(response['column_summary']);
    // plot_column_histogram("column_histogram", column_name, data_frame);
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
            if (response["error_message"] !== null) {
                $("#msg_text").text(response["error_message"]);
                $("#msg_box").removeClass("invisible");
            } else {
                set_training_summaries(response);
            }
        },
   });
}

function loadColumnStats(column_summary) {
    $("#column_stats_table tr[class='clickable-row']").remove();
    var table = $("#column_stats_table")
    for (var i=0; i < column_summary.length; i++) {
        var row = document.createElement("tr");
        row.setAttribute('class','clickable-row');
        row.append( getCell(column_summary[i]['name']) );
        row.append( getCell(column_summary[i]['type']) );
        row.append( getCell(column_summary[i]['min']) );
        row.append( getCell(column_summary[i]['max']) );
        row.append( getCell(column_summary[i]['mean']) );
        row.append( getCell(column_summary[i]['stdev']) );
        table.append(row);
    }
    $("#column_stats_table tr[class='clickable-row']").on('click', function(){
        if( !$(this).hasClass("highlight") )
            $(this).addClass("highlight").siblings().removeClass("highlight");
    });
}

function getCell(content) {
    var cell = document.createElement("td");
    cell.setAttribute('class','info-cell');
    cell.innerHTML = content;
    return cell;
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
