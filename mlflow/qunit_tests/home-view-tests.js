/**
 * QUnit tests for Home page
 */
const { test } = QUnit;

QUnit.module("initialize", {
    beforeEach: function() { _addWidgetsTo("qunit-fixture"); },
    afterEach: function() {
        $("#qunit-fixture").empty();
        sinon.restore();
    }
});

test( "hides glass pane", function( assert ) {
    initialize();
    assert.ok($("#glass_pane").is(":hidden"));
});

test( "hides message box by default", function( assert ) {
    initialize();
    assert.ok($("#msg_box").not(":visible"));
});

test( "shows message box when message is present", function( assert ) {
    $('#msg_text').text('Some message');
    initialize();
    assert.ok($("#msg_box").not(":hidden"));
});

test( "closes message box on close button click", function( assert ) {
    $('#msg_text').text('Some message');
    initialize();
    $("msg_box_close").click();
    assert.ok($("#msg_box").not(":visible"));
});

test( "hides content area when file selection changes", function( assert ) {
    initialize();
    var dataFileSelector = $("select[name='data_file']");
    var contentDiv = $("#home_container");
    dataFileSelector.val('1');
    contentDiv.removeClass('invisible');
    dataFileSelector.val('2').trigger('change');
    assert.ok(contentDiv.hasClass("invisible"));
});

test( "shows content of last loaded file it is re-selected", function( assert ) {
    initialize();
    var dataFileSelector = $("select[name='data_file']");
    var contentDiv = $("#home_container");
    /* Simulate option 2 loaded in content area */
    $("#source_file").text("2");
    dataFileSelector.val('2').trigger('change');
    contentDiv.removeClass("invisible");
    /* Change selection to hide content area */
    dataFileSelector.val('1').trigger('change');
    assert.ok(contentDiv.hasClass("invisible"));
    /* Re-select previous option */
    dataFileSelector.val('2').trigger('change');
    assert.ok( contentDiv.hasClass("invisible") === false );
});

test( "ignores default selection when select button is clicked", function( assert ) {
    initialize();
    mockAjax = sinon.stub($, "ajax");
    $("select[name='data_file']").val('0');
    $('#select_btn').click();
    assert.ok($("#home_container").hasClass("invisible"));
    assert.ok($("#glass_pane").is(":hidden"));
    sinon.assert.notCalled(mockAjax);
});

test( "shows glass pane when select button is clicked with file selected", function( assert ) {
    initialize();
    $("select[name='data_file']").val('1');
    $('#select_btn').click();
    assert.ok( $("#glass_pane").is(":visible") );
});

test( "sends ajax request when select button is clicked", function( assert ) {
    assert.expect(0);
    mockAjax = sinon.stub($, "ajax");
    initialize();
    $("select[name='data_file']").val('1');
    $('#select_btn').click();
    sinon.assert.called(mockAjax);
    var expectedArgs = {url:"load_file", data:"data_file=1", dataType:"json", success: loadFileData};
    sinon.assert.calledWith(mockAjax, expectedArgs);
});

/**=======================================================================================================
 * UTILITY FUNCTIONS
 */
function _addWidgetsTo(divID) {
    var glassPane = document.createElement('div');
    var msgBox = document.createElement('div');
    var msgText = document.createElement('span');
    var msgBoxClose = document.createElement('button');
    var homeContainer = document.createElement('div');
    var selectDropdown = document.createElement('select');
    var selectBtn = document.createElement('button');
    var sourceFile = document.createElement('span');
    var fileSelectForm = document.createElement('form');
    glassPane.setAttribute('id','glass_pane');
    msgBox.setAttribute('id', 'msg_box');
    msgBox.setAttribute('class', 'invisible');
    msgText.setAttribute('id', 'msg_text');
    msgBoxClose.setAttribute('id', 'msg_box_close')
    homeContainer.setAttribute('id', 'home_container');
    homeContainer.setAttribute('class', 'invisible');
    selectDropdown.setAttribute('name', 'data_file');
    selectBtn.setAttribute('id', 'select_btn');
    sourceFile.setAttribute('id', "source_file");
    fileSelectForm.setAttribute('id', 'file_select_form');
    fileSelectForm.setAttribute('action', 'load_file');
    for (var i = 0; i <= 2; i++) {
        var opt = document.createElement('option');
        opt.setAttribute('value', ""+i);
        opt.textContent = "option"+i;
        selectDropdown.append(opt);
    }
    fileSelectForm.append(selectDropdown, selectBtn);
    $("#"+divID).append(glassPane, sourceFile, fileSelectForm).append(msgBox, msgText, msgBoxClose)
            .append(homeContainer);
}