

// Scroll to specific values
// scrollTo is the same

// A $( document ).ready() block.
$( document).ready(function() {
    $('#thedrdu, #thedrdu2')
        .delay(1500)
        .queue(function (next) {
            $(this).css('visibility', 'visible');
        });
});
