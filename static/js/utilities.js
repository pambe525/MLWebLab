$().ready(function() {

  if ($("#msg_text").text() !== "None") $('#msg_box').show();
  else $("#msg_box").hide();
  $("#glass_pane").hide();

  $("#msg_box_close").on('click', function() {
      $("#msg_box").hide();
  });

  $("#datafile_form").on('submit', function() {
      if ( $(document.activeElement).attr('name') === "train_btn") $("#glass_pane").show();
  });

  $("#sidebar_form").on('submit', function(e) {
      if ( $(document.activeElement).attr('name') === "train_btn") $("#glass_pane").show();
  });

})

