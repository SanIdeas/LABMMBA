// Users View
function reload_setup(msg){
	$.ajax({
		url: reload,
		method: 'POST',
		beforeSend: function(xhr){
			xhr.setRequestHeader("X-CSRFToken", csrf_token);
		}
	}).done(function(html){
		if(html.redirect)
			window.location.href = html.redirect;
		else{
			$('#users-setup').children().remove();
			$('#users-setup').append(html);

			if(msg != null)
				$('#invitation-error').text(msg);
		}

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
		window.location.href = $(this).attr('data-target');
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
			reload_setup();
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

// Areas View
function reload_area_setup(msg){
	$.ajax({
		url: reload,
		method: 'POST',
		beforeSend: function(xhr){
			xhr.setRequestHeader("X-CSRFToken", csrf_token);
		}
	}).done(function(html){
		if(html.redirect)
			window.location.href = html.redirect;
		else{
			$('#areas-setup').children().remove();
			$('#areas-setup').append(html);

			if(msg != null)
				$('#add-area-error').text(msg);
		}

	});
}

function areas(){
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
	$('.setup-delete-box').click(function(){
		$('#modal-area-name').text($(this).attr('area-name'));
		$('#modal-user-count').text($(this).attr('area-count'));
		$('#modal-confirm').attr('area-id', $(this).attr('area-id'));
		$('#modal-delete-confirm').removeClass('modal-hidden').addClass('modal-visible');
		$('#modal-curtain').removeClass('curtain-hidden').addClass('curtain-visible');
	});
	$('#modal-cancel').click(function(){
		$('#modal-delete-confirm').addClass('modal-hidden').removeClass('modal-visible');
		$('#modal-curtain').addClass('curtain-hidden').removeClass('curtain-visible');
	});
	$('#modal-confirm').click(function(){
		$.ajax({
			url: remove.replace('999', $(this).attr('area-id')),
			type: 'GET'
		}).done(function(){
			reload_area_setup();
		});
	});
	$('#add-area-form').submit(function(e){
		$.ajax({
			url: reload,
			type: 'POST',
			data: $(this).serialize(),
			beforeSend: function(xhr){
				xhr.setRequestHeader("X-CSRFToken", csrf_token);
				e.preventDefault();

				if($('#add-area-name').val().length <= 0)	// Abort if email is empty
					xhr.abort();
				else {
					$('#add-area-submit').val("Agregando...").attr("disabled", true);
					$('#add-area-error').text("");
				}
			}
		}).done(function(data){
			reload_area_setup(data['message']);
		});
	});
}

// Webpage View
function reload_webpage_setup(id){
	$.ajax({
		url: reload,
		method: 'POST',
		data: {'id': id},
		beforeSend: function(xhr){
			xhr.setRequestHeader("X-CSRFToken", csrf_token);
		}
	}).done(function(html){
		if(html.redirect)
			window.location.href = html.redirect;
		else{
			// Remove TinyMCE Editor instances
			tinymce.execCommand('mceRemoveEditor', true, 'spanish-title-edit');
			tinymce.execCommand('mceRemoveEditor', true, 'spanish-body-edit');
			tinymce.execCommand('mceRemoveEditor', true, 'english-title-edit');
			tinymce.execCommand('mceRemoveEditor', true, 'english-body-edit');

			$('#webpage-setup').children().remove();
			$('#webpage-setup').append(html);
		}
	});
}

function webpage(){
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

	$('.body').bind('scroll', function(){
		if ($('.body').scrollTop() > 172){
			$('.setup-webpage-list').addClass('fixed');
			$(this).css('z-index', '100');
		}
		else{
			$('.setup-webpage-list').removeClass('fixed');
			$(this).css('z-index', '');
		}
	});

	$('#spanish-edit-box').click(function(){
		tinyMCE.get('spanish-title-edit').setMode('design');
		tinyMCE.get('spanish-body-edit').setMode('design');
		$(this).parent(0).addClass('setup-hidden');
		$('#spanish-accept-box').parent(0).removeClass('setup-hidden');
		$('#spanish-cancel-box').parent(0).removeClass('setup-hidden');
	});

	$('#english-edit-box').click(function(){
		tinyMCE.get('english-title-edit').setMode('design');
		tinyMCE.get('english-body-edit').setMode('design');
		$(this).parent(0).addClass('setup-hidden');
		$('#english-accept-box').parent(0).removeClass('setup-hidden');
		$('#english-cancel-box').parent(0).removeClass('setup-hidden');
	});

	$('#spanish-accept-box').click(function(){
		var spanish_title_edit = tinyMCE.get('spanish-title-edit');
		var spanish_body_edit = tinyMCE.get('spanish-body-edit');

		spanish_title_edit.setMode('readonly');
		spanish_body_edit.setMode('readonly');

		$.ajax({
			url: edit.replace('999', $(this).attr('section-id')),
			method: 'POST',
			data: {
				'spanish-title': spanish_title_edit.getContent(),
				'spanish-body': spanish_body_edit.getContent()
			},
			beforeSend: function(xhr){
				xhr.setRequestHeader("X-CSRFToken", csrf_token);
			}
		}).done(function(html){
			if(html.redirect)
				window.location.href = html.redirect;
			else{
				$('#spanish-edit-box').parent(0).removeClass('setup-hidden');
				$('#spanish-accept-box').parent(0).addClass('setup-hidden');
				$('#spanish-cancel-box').parent(0).addClass('setup-hidden');
			}
		});
	});

	$('#spanish-cancel-box').click(function(){
		var spanish_title_edit = tinyMCE.get('spanish-title-edit');
		var spanish_body_edit = tinyMCE.get('spanish-body-edit');

		spanish_title_edit.getBody().innerHTML = spanish_title_edit.startContent;
		spanish_body_edit.getBody().innerHTML = spanish_body_edit.startContent;
		spanish_title_edit.setMode('readonly');
		spanish_body_edit.setMode('readonly');

		$('#spanish-edit-box').parent(0).removeClass('setup-hidden');
		$('#spanish-accept-box').parent(0).addClass('setup-hidden');
		$('#spanish-cancel-box').parent(0).addClass('setup-hidden');
	});

	$('#english-accept-box').click(function(){
		var english_title_edit = tinyMCE.get('english-title-edit');
		var english_body_edit = tinyMCE.get('english-body-edit');

		english_title_edit.setMode('readonly');
		english_body_edit.setMode('readonly');

		$.ajax({
			url: edit.replace('999', $(this).attr('section-id')),
			method: 'POST',
			data: {
				'english-title': english_title_edit.getContent(),
				'english-body': english_body_edit.getContent()
			},
			beforeSend: function(xhr){
				xhr.setRequestHeader("X-CSRFToken", csrf_token);
			}
		}).done(function(html){
			if(html.redirect)
				window.location.href = html.redirect;
			else{
				$('#english-edit-box').parent(0).removeClass('setup-hidden');
				$('#english-accept-box').parent(0).addClass('setup-hidden');
				$('#english-cancel-box').parent(0).addClass('setup-hidden');
			}
		});
	});

	$('#english-cancel-box').click(function(){
		var english_title_edit = tinyMCE.get('english-title-edit');
		var english_body_edit = tinyMCE.get('english-body-edit');

		english_title_edit.getBody().innerHTML = english_title_edit.startContent;
		english_body_edit.getBody().innerHTML = english_body_edit.startContent;
		english_title_edit.setMode('readonly');
		english_body_edit.setMode('readonly');

		$('#english-edit-box').parent(0).removeClass('setup-hidden');
		$('#english-accept-box').parent(0).addClass('setup-hidden');
		$('#english-cancel-box').parent(0).addClass('setup-hidden');
	});

	/* TinyMCE Editors */
	// Title Editors
	$('#spanish-title-edit, #english-title-edit').tinymce({
		force_br_newlines : false,
		force_p_newlines : false,
		forced_root_block : 'h1',
		menubar: false,
		statusbar: false,
		content_css: tinymce_css,
		toolbar: 'undo redo | bold italic underline | alignleft aligncenter alignright outdent indent',
		readonly: true,
		language: 'es',
		setup: function(ed){
			ed.on('loadContent', function(){    // Avoid to loose <h1> class when everything is deleted
				$(ed.getBody()).bind("DOMNodeInserted", function(e){
					var element = e.target;
					if(element.tagName == 'H1')
						$(element).addClass('c12');
				});
			})
		}
	});

	// Body Editors
	$('#spanish-body-edit, #english-body-edit').tinymce({
		height: 400,
		content_css: tinymce_css,
		plugins: [
			'advlist autolink lists link image charmap preview hr anchor pagebreak',
			'searchreplace wordcount visualblocks visualchars fullscreen',
			'insertdatetime media nonbreaking save table contextmenu directionality',
			'paste textcolor colorpicker textpattern imagetools'
		],
		toolbar1: 'insertfile undo redo | bold italic underline | alignleft aligncenter alignright alignjustify | bullist numlist',
		toolbar2: 'outdent indent | link image | preview media | forecolor backcolor |',
		readonly: true,
		language: 'es',
		setup: function(ed){
			ed.on('loadContent', function(){    // Avoid to loose <p> class when everything is deleted
				$(ed.getBody()).bind('DOMNodeInserted', function(e){
					var element = e.target;
					if(element.tagName == 'P')
						$(element).addClass('s3 c9');
				});
			})
		}
	});
}

function webpage_init(){
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
	$('#section-select').change(function(){
		reload_webpage_setup(this.value);
	});
}