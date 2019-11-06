
QUnit.test( "first test", function( assert ) {
    btn = $('<input type="button" value="new button" />');
    $("#qunit-fixture").append(btn);
    assert.equal(btn.val(), "new button", );
    // $("#qunit-fixture").clear();
});
QUnit.test( "second test", function( assert ) {
    // btn = $('<input type="button" value="new button" />');
    // $("#qunit-fixture").append(btn);
    assert.equal(btn.val(), "new button", );
});