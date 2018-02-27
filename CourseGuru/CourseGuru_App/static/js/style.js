$(document).ready(function() {
    $("#test").html("Test!"); 

	$("#NQ").keydown(function(e) {
        if(e.which == 13) {
            this.form.submit();
        }
	});
	
/*	$('#submit').click(function(){ */
	$('#inp').keydown(function(e) {
		if(e.which == 13) {
			var input = $('input#inp').val();
			$('input').val('');
			var history = $('#CWindow').html();		
			$('#CWindow').html(history + '<p>' + input + '</p>');
		}
	});
});



