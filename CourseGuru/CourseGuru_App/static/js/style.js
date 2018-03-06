$(document).ready(function() {
	
    $("#test").html("Test!"); 

	$("#NQ").keydown(function(e) {
        if(e.which == 13) {
            this.form.submit();
        }
	});
	
	$('#voteUp').click(function(e) { 
		//$('#voteUpImg').addClass('glyphicon-thumbs-down').removeClass('glyphicon-thumbs-up');
		$('#voteDownImg').removeClass('votedDown');
		$('#voteUpImg').addClass('votedUp');
	});
	
	$('#voteDown').click(function(e) { 
		$('#voteUpImg').removeClass('votedUp');
		$('#voteDownImg').addClass('votedDown');
	});
	
/*	$('#submit').click(function(){ */
	$('#inp').keydown(function(e) {
		if(e.which == 13) {
			
			$("#inp").prop("readonly", true);
			
			var input = $('input#inp').val();
			$('#inp').val('');
			var history = $('#CWindow').html();	
			$('#CWindow').html(history + '<div class="msgContainer" align="right"><p>' + input + '</p><br><div class="msgLabel">You</div></div>');
			function loadGif() {
				$('#CWindow').html(history + '<div class="msgContainer" align="right"><p>' + input + '</p><br><div class="msgLabel">You</div></div>' + '<div class="botmsgContainer"><img src="http://www.witchdoctorcomic.com/wp-content/plugins/funny-chat-bot/images/load.gif" style="max-height: 50px; max-width: 50px;" /></div>');
				div = $('#CWindow');
				div.scrollTop(div.prop('scrollHeight'))
			}
			function grabAnswer() {
				$.get('/chatAnswer/', {"question": input}, function(data) {	
					$('#CWindow').html(history + '<div class="msgContainer" align="right"><p>' + input + '</p><br><div class="msgLabel">You</div></div>' + '<div class="botmsgContainer"><p >' + data + '</p><br><div class="msgBotLabel">Chatbot</div></div>');			
					div = $('#CWindow');
					div.scrollTop(div.prop('scrollHeight'))
					$("#inp").prop("readonly", false);
				});			
			}
			setTimeout(loadGif, 500);
			setTimeout(grabAnswer, 1000);
			
			div = $('#CWindow');
			div.scrollTop(div.prop('scrollHeight'))
		}
	});
});

// Hide or show account drop down
function profileFunc() {
    document.getElementById("profileDropdown").classList.toggle("show");
}

// Close the account drop down when click is made outside of content
window.onclick = function(event) {
  if (!event.target.matches('.dropbtn')) {

    var accElements = document.getElementsByClassName("profile-content");
    var i;
    
    for (i = 0; i < accElements.length; i++) {
      var elem = accElements[i];
      if (elem.classList.contains('show')) {
    	  elem.classList.remove('show');
      }
    }
  }
}
