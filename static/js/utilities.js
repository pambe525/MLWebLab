$(document).ready(function(){
    if (errorMessage != null) $('#messageBox').modal("show");
    $("#glass_pane").hide();
    $("#datafile_form").on('submit', function() {
        if ( $(document.activeElement).attr('name') === "train_btn") $("#glass_pane").show();
    })
     $("#sidebar_form").on('submit', function(e) {
        if ( $(document.activeElement).attr('name') === "train_btn") $("#glass_pane").show();
    })
})
