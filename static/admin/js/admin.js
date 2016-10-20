function reload_setup(msg){
	$.ajax({
		url: reload,
		method: 'POST',
		beforeSend: function(xhr){
			xhr.setRequestHeader("X-CSRFToken", csrf_token);
		}
	}).done(function(html){
		$('#users-setup').children().remove();
		$('#users-setup').append(html);

		if(msg != null)
			$('#invitation-error').text(msg);
	});
}

function users(){
	/*if(/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) && $this.attr('setup-action') =='users') {
		$('.asd').click(function(){
			touched = $(this);
			$(this).addClass('setup-user-row-expand-rsp');
		});
		$(window).on('click', function(e){
			console.log(touched);
			if(!(touched.is(e.target) || touched.children().is(e.target))){
				touched.removeClass('setup-user-row-expand-rsp');		
			}
		});			
	}*/
	$('.setup-view-box').click(function(){
		window.open($(this).attr('data-target'), '_blank');
	});
	$('.setup-delete-box').click(function(){
		$('#modal-user-img').css('background-image', 'url(' + $(this).attr('user-img') + ')');
		$('#modal-user-name').text($(this).attr('user-full-name'));
		$('#modal-user-count').text($(this).attr('user-count'));
		$('#modal-confirm').attr('user-id', $(this).attr('user-id'));
		$('#modal-delete-confirm').removeClass('modal-hidden').addClass('modal-visible');
		$('#modal-curtain').removeClass('curtain-hidden').addClass('curtain-visible');
	});
	$('.setup-delete-invitation-box').click(function(){
		$.ajax({
			url: remove.replace('999', $(this).attr('user-id')),
			type: 'GET',
		}).done(function(){
			reload_setup();
		});
	});
	$('#modal-cancel').click(function(){
		$('#modal-delete-confirm').addClass('modal-hidden').removeClass('modal-visible');
		$('#modal-curtain').addClass('curtain-hidden').removeClass('curtain-visible');
	});
	$('#modal-confirm').click(function(){
		$.ajax({
			url: remove.replace('999', $(this).attr('user-id')),
			type: 'GET',
		}).done(function(){
			reload_setup();
		});		
	});
	$('.setup-block-box').click(function(){
		$.ajax({
			url: block.replace('999', $(this).attr('user-id')),
			type: 'GET',
		}).done(function(){
			reload_setup();
		});
	});
	$('.setup-unblock-box').click(function(){
		$.ajax({
			url: unblock.replace('999', $(this).attr('user-id')),
			type: 'GET',
		}).done(function(){
			reload_setup();
		});
	});
	$('.setup-forward-box').click(function(){
		$.ajax({
			url: invitation,
			type: 'POST',
			data: {'email': $(this).attr('user-email')},
			beforeSend: function(xhr){
				xhr.setRequestHeader("X-CSRFToken", csrf_token);

				$('.setup-forward-box').children().removeClass('fa fa-mail-forward').addClass('fa fa-repeat');
				$('.setup-forward-box').attr("disabled", true);
			}
		}).done(function(){
			reload_setup('');
		});
	});
	$('#invitation-form').submit(function(e){
		$.ajax({
			url: invitation,
			type: 'POST',
			data: $(this).serialize(),
			beforeSend: function(xhr){
				xhr.setRequestHeader("X-CSRFToken", csrf_token);
				e.preventDefault();

				if($('#email-invitation').val().length <= 0)	// Abort if email is empty
					xhr.abort();
				else {
					$('#submit-invitation').val("Enviando...").attr("disabled", true);
					$('#invitation-error').text("");
				}
			}
		}).done(function(data){
			reload_setup(data['message']);
		});
	});
}