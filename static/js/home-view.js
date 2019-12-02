/**
 * Function to be called when document is loaded
 */

var dataFrame = null;
var columnSummary = null;
$().ready(initialize);

function initialize() {
    $("#glass_pane").hide();
    if ($("#msg_text").text() !== "None") showMsgBox();
    $("#msg_box_close").on( 'click', hideMsgBox );
    $("select[name='data_file']").on('change', fileSelectionChangeHandler);
    $("#select_btn").on( 'click', selectButtonClickHandler);
    $("select[name='n_splits']").on('change', splitSelectionChangeHandler)
    $("#train_btn").on('click', trainButtonClickHandler)
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

function sendAjaxFormRequest(formId, successHandler) {
    var form = $("#"+formId);
    $.ajax({
        url: form.attr('action'),
        data: form.serialize(),
        dataType: 'json',
        success: successHandler
    });
}

function fileSelectionChangeHandler() {
    if ($("#source_file").text() === $("select[name='data_file']").val() )
        $("#home_container").removeClass("invisible");
    else $("#home_container").addClass("invisible");
}

function selectButtonClickHandler() {
    if ($("select[name='data_file']")[0].selectedIndex !== 0) {
        $("#glass_pane").show();
        sendAjaxFormRequest("file_select_form", displayFileData);
    }
    return false;
}

function splitSelectionChangeHandler() {
    initializeTrainingMetrics();
    initializeTrainingPlots();
}

function trainButtonClickHandler() {
    $("#glass_pane").show();
    sendAjaxFormRequest("sidebar_form", displayTrainingSummary);
    return false;
}

function displayFileData(response) {
    $("#glass_pane").hide();
    if ( errorOccurred(response) )
        showMsgBox(response["error_message"]);
    else {
        try {
            hideMsgBox();
            dataFrame = JSON.parse(response['data_frame']);
            columnSummary = response['column_summary'];
            updateDataFileSummary(response);
            setClickableRowHandler("column_stats_table", plotHistogramOnClick);
            $("#target_feature").text(response["target_feature"]);
            displayHeatMap(response);
            initializeTrainingMetrics();
            initializeTrainingPlots();
            $("#column_stats_table tr[class='clickable-row']")[0].click();
            $("#nav-summary-tab").click();
            $("#home_container").removeClass("invisible");
        } catch(e) {
            alert(e);
        }
    }
}

function updateDataFileSummary(response) {
    $("#source_file").text(response['file_name']);
    $("#source_rows").text(response['data_file_rows']);
    $("#source_cols").text(response['data_file_cols']);
    loadColumnStatsTable();
}

function loadColumnStatsTable() {
    $("#column_stats_table tr[class*='clickable-row']").remove();
    var tbody = $("#column_stats_table tbody");
    for (var i=0; i < columnSummary.length; i++) {
        var row = document.createElement("tr");
        row.setAttribute('class','clickable-row');
        row.appendChild( getCell(columnSummary[i]['name']) );
        row.appendChild( getCell(columnSummary[i]['type']) );
        row.appendChild( getCell(columnSummary[i]['min']) );
        row.appendChild( getCell(columnSummary[i]['max']) );
        row.appendChild( getCell(columnSummary[i]['mean']) );
        row.appendChild( getCell(columnSummary[i]['stdev']) );
        tbody.append(row);
    }
}

function setClickableRowHandler(tableID, onClickHandler) {
    $("#"+tableID+" tr[class='clickable-row']").on('click', function(){
        if( !$(this).hasClass("highlight") ) {
            $(this).addClass("highlight").siblings().removeClass("highlight");
            onClickHandler($(this));
        }
    });
}

function plotHistogramOnClick(rowElement) {
    var columnName = rowElement.children()[0].innerHTML;
    var columnValues = getColumnValues(columnName);
    plot_column_histogram("column_histogram", columnName, columnValues);
}

function getColumnValues(columnName) {
    var nRecords = Object.keys(dataFrame[columnName]).length;
    var columnValues = [];
    for (var i = 0; i < nRecords; i++)
        columnValues[i] = (dataFrame[columnName][i.toString()]);
    return columnValues;
}

function getCell(content) {
    var cell = document.createElement("td");
    cell.setAttribute('class','info-cell');
    cell.innerHTML = content;
    return cell;
}

function displayHeatMap(response) {
    var corrMatrix = response['correlation_matrix'];
    var columnNames = Object.keys(dataFrame);
    plotCorrelationHeatmap("covariance_heatmap", columnNames, corrMatrix)
}

function initializeTrainingMetrics() {
    $("#train_score").text("");
    $("#test_score").text("");
    $("#train_scores_stdev").text("");
    $("#test_scores_stdev").text("");
}

function initializeTrainingPlots() {
    var nSplits = parseInt($("#n_splits_select option:selected").text());
    var targetName = $("#target_feature").text();
    plotSplitScores("cv_scores_plot", nSplits, null, null);
    var targetSummary = columnSummary[columnSummary.length-1];
    var yActual = [targetSummary['min'], targetSummary['max']];
    plotValidation("validation_plot", targetName, yActual, []);
}

function displayTrainingSummary(response) {
    $("#glass_pane").hide();
    if ( errorOccurred(response) ) showMsgBox(response["error_message"]);
    else setTrainingSummaries(response);
}

function setTrainingSummaries(response) {
    $("#train_score").text(response["mean_train_score"].toFixed(2));
    $("#test_score").text(response["mean_test_score"].toFixed(2));
    $("#train_scores_stdev").text(response["train_scores_stdev"].toFixed(2));
    $("#test_scores_stdev").text(response["test_scores_stdev"].toFixed(2));
    var nSplits = parseInt($("#n_splits_select option:selected").text());
    var targetName = $("#target_feature").text();
    var yActual = response["y"];
    var yPredict = response["y_predict"];
    plotSplitScores("cv_scores_plot", nSplits, response["train_scores"], response["test_scores"]);
    plotValidation("validation_plot", targetName, yActual, yPredict);
}
