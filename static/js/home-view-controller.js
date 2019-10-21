$().ready(function() {

    $("#glass_pane").hide();
    if ($("#msg_text").text() !== "None") $('#msg_box').show();
    else $("#msg_box").hide();


    $("#msg_box_close").on('click', function () {
        $("#msg_box").hide();
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
   });
}

