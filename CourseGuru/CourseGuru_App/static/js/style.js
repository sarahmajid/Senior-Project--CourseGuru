$(document).ready(function() {
    $("#test").html("Testing!"); 

	$("#NQ").keydown(function(e) {
        if(e.which == 13) {
            this.form.submit();
        }
	});
	
/*	$('#submit').click(function(){ */
	$('#inp').keydown(function(e) {
		if(e.which == 13) {
			var input = $('textarea').val();
			var history = $('#CWindow').html();		
			$('#CWindow').html(history + '<p>' + input + '</p>');
		}
	});
});



