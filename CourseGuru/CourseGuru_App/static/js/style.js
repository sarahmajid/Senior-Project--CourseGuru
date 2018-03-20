$(document).ready(function() {

    //Submits a form on enter key press
	$("#NQ").keydown(function(e) {
        if(e.which == 13) {
            this.form.submit();
        }
	});
	
	//Changes color of upvote and rating number when clicked
	$(".ratingArea").find("#voteUp").click(function(e) {
		rateDiv = $(this).closest("div");
		downBtn = rateDiv.find("#voteDown");
		
		rateEl = rateDiv.find("#rating")
		curRate = parseInt(rateEl.html());
		if (downBtn.hasClass('votedDown')){
			rateEl.html(curRate+2);
		}
		else if (!($(this).hasClass('votedUp')) && !(downBtn.hasClass('votedDown'))){
			rateEl.html(curRate+1);
		}
		
		downBtn.removeClass('votedDown');
		$(this).addClass('votedUp');
		
	});
	
	//Changes color of downvote and rating number when clicked
	$(".ratingArea").find("#voteDown").click(function(e) {
		rateDiv = $(this).closest("div");
		upBtn = rateDiv.find("#voteUp");
		
		rateEl = rateDiv.find("#rating")
		curRate = parseInt(rateEl.html());
		if (upBtn.hasClass('votedUp')){
			rateEl.html(curRate-2);
		}
		else if (!($(this).hasClass('votedDown')) && !(upBtn.hasClass('votedUp'))){
			rateEl.html(curRate-1);
		}
		
		upBtn.removeClass('votedUp');
		$(this).addClass('votedDown');
	});
	
	/*HTMLEscape a string*/
	function escape(value) {
	      return value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
	}
	
	
/*	$('#submit').click(function(){ */
	$('#inp').keydown(function(e) {
		if(e.which == 13) {
			
			$("#inp").prop("readonly", true);
			
			var input = escape($('input#inp').val());
			$('#inp').val('');
			var history = $('#CWindow').html();	
			$('#CWindow').html(history + '<div class="msgContainer" align="right"><p>' + input + '</p><br><div class="msgLabel">You</div></div>');
			function loadGif() {
				$('#CWindow').html(history + '<div class="msgContainer" align="right"><p>' + input + '</p><br><div class="msgLabel">You</div></div>' + '<div class="botmsgContainer"><img src="http://www.witchdoctorcomic.com/wp-content/plugins/funny-chat-bot/images/load.gif" style="max-height: 50px; max-width: 50px;" /></div>');
				div = $('#CWindow');
				div.scrollTop(div.prop('scrollHeight'))
			}
			/*Extracts url parameters*/
			$.urlParam = function(name){
				var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
				return results[1] || 0;
			}
			function grabAnswer() {
				
				var cid = $.urlParam('cid');
				$.get('/chatAnswer/', {"question": input, "cid": cid}, function(data) {	
					$('#CWindow').html(history + '<div class="msgContainer" align="right"><p>' + input + '</p><br><div class="msgLabel">You</div></div>' + '<div class="botmsgContainer"><p >' + data + '</p><br><div class="msgBotLabel">Chatbot</div></div>');			
					div = $('#CWindow');
					div.scrollTop(div.prop('scrollHeight'))
					$("#inp").prop("readonly", false);
				});			
			}
			setTimeout(loadGif, 500);
			setTimeout(grabAnswer, 500);
			
			div = $('#CWindow');
			div.scrollTop(div.prop('scrollHeight'))
		}
	});
	
	//Warns user uploading a syllabus that the previous will be replaced.
	$("#chkType").click(function() {
		if($('#docType').find(":selected").text() == "Syllabus") {
			if(confirm("Only one syllabus is allowed per course. If uploading multiple syllabi, the previous will always be replaced.")){
		        return true;
		    }
		    else{
		    	return false;
		    }
		}
	});
});

// Hide or show account drop down
function profileFunc() {
    document.getElementById("profileDropdown").classList.toggle("show");
}

//Ajax call to voting function and changes rating number on page
function vote(elem, rating, answerID, userID) { 
	$.get('/voting/', {"rating": rating, "answer": answerID, "user": userID}, function(data) {		
//		rateDiv = $(elem).closest("div");
//		rating = rateDiv.find("#rating");
//		rating.html(data);
	});	
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