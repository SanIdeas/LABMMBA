function reload_setup(setup){
	$.ajax({
		url: setup_link.replace('999', setup),
		method: 'POST',
		beforeSend: function(xhr){
			xhr.setRequestHeader("X-CSRFToken", csrf_token);
		}
	}).done(function(html){
		$('#setup').children().remove();
		$('#setup').append(html);
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

	$('.setup-accept-box').click(function(){
		$.ajax({
			url: activate.replace('999', $(this).attr('user-id')),
			type: 'GET',
		}).done(function(){
			reload_setup('users');
		});
	});
	$('.setup-delete-box').click(function(){
		$('#modal-user-img').css('background-image', 'url(' + $(this).attr('user-img') + ')');
		$('#modal-user-name').text($(this).attr('user-full-name'));
		$('#modal-user-count').text($(this).attr('user-count'));
		$('#modal-confirm').attr('user-id', $(this).attr('user-id'));
		$('#modal-delete-confirm').removeClass('modal-hidden').addClass('modal-visible');
		$('#modal-curtain').removeClass('curtain-hidden').addClass('curtain-visible');
	});
	$('#modal-cancel').click(function(){
		$('#modal-delete-confirm').addClass('modal-hidden').removeClass('modal-visible');
		$('#modal-curtain').addClass('curtain-hidden').removeClass('curtain-visible');
	});
	$('#modal-confirm').click(function(){
		console.log("asd");
		$.ajax({
			url: remove.replace('999', $(this).attr('user-id')),
			type: 'GET',
		}).done(function(){
			reload_setup('users');
		});		
	});
	$('.setup-block-box').click(function(){
		$.ajax({
			url: block.replace('999', $(this).attr('user-id')),
			type: 'GET',
		}).done(function(){
			reload_setup('users');
		});
	});
	$('.setup-unblock-box').click(function(){
		$.ajax({
			url: unblock.replace('999', $(this).attr('user-id')),
			type: 'GET',
		}).done(function(){
			reload_setup('users');
		});
	});
}