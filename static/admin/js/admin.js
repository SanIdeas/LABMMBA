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
			type: 'GET'
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
			type: 'GET'
		}).done(function(){
			reload_setup();
		});
	});
	$('.setup-block-box').click(function(){
		$.ajax({
			url: block.replace('999', $(this).attr('user-id')),
			type: 'GET'
		}).done(function(){
			reload_setup();
		});
	});
	$('.setup-unblock-box').click(function(){
		$.ajax({
			url: unblock.replace('999', $(this).attr('user-id')),
			type: 'GET'
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

				if(!$('#email-invitation').val().trim())	// Abort if email is empty
					xhr.abort();
				else {
					$('#submit-invitation').val(gettext("Enviando...")).attr("disabled", true);
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

	$(window).unbind('ready').unbind('resize');

	function checkResponsiveButtons(){
        var minBox = $('#areas-setup .intranet.box').first();

        var maxTitle = $('.setup-areas-subtitle h3').sort(function(s1, s2){
            return $(s1).width() < $(s2).width();
        }).first();

        var delta = minBox.width() - maxTitle.width();

        if(delta < 126){
            $('.setup-areas-subtitle').css('display', 'block');
            $('.setup-areas-container').css('padding-left', '0');
            $('.setup-areas-container .setup-areas-box').css('margin', '0 auto');
            $('.setup-areas-container .setup-areas-box:nth-child(3)').css('width', 'auto');
            $('.setup-areas-subtitle h3').css('white-space', 'normal');
        }
        else{
            $('.setup-areas-subtitle').css('display', 'flex');
            $('.setup-areas-container').css('padding-left', '5px');
            $('.setup-areas-container .setup-areas-box').css('margin', 'auto');
            $('.setup-areas-container .setup-areas-box:nth-child(3)').css('width', '100%');
            $('.setup-areas-subtitle h3').css('white-space', 'nowrap');
        }
	}

	$(window).resize(function(){
        checkResponsiveButtons();
    });

	$(window).ready(function(){
        checkResponsiveButtons();
    });
	// Subareas
	$('.setup-subarea-box .setup-delete-box').click(function(){
		$('#subarea-modal-delete-confirm #modal-subarea-name').text($(this).attr('subarea-name'));
		$('#subarea-modal-delete-confirm #modal-confirm').attr('subarea-id', $(this).attr('subarea-id'));
		$('#subarea-modal-delete-confirm').removeClass('modal-hidden').addClass('modal-visible');
		$('#modal-curtain').removeClass('curtain-hidden').addClass('curtain-visible');
	});
    $('.setup-subarea-box .setup-edit-box').click(function(){
        $('#subarea-modal-edit-confirm #modal-confirm').attr('subarea-id', $(this).attr('subarea-id'));
        $('#subarea-modal-edit-confirm #modal-confirm').attr('subarea-name', $(this).attr('subarea-name'));
        $('#subarea-modal-edit-confirm #modal-subarea-name').val($(this).attr('subarea-name'));
        $('#subarea-modal-edit-confirm').removeClass('modal-hidden').addClass('modal-visible');
        $('#modal-curtain').removeClass('curtain-hidden').addClass('curtain-visible');
        $('#subarea-modal-edit-confirm #modal-error').text("");
    });
	$('#subarea-modal-delete-confirm #modal-cancel').click(function(){
		$('#subarea-modal-delete-confirm').addClass('modal-hidden').removeClass('modal-visible');
		$('#modal-curtain').addClass('curtain-hidden').removeClass('curtain-visible');
	});
	$('#subarea-modal-edit-confirm #modal-cancel').click(function(){
        $('#subarea-modal-edit-confirm').addClass('modal-hidden').removeClass('modal-visible');
        $('#modal-curtain').addClass('curtain-hidden').removeClass('curtain-visible');
    });
	$('#subarea-modal-delete-confirm #modal-confirm').click(function(){
		$.ajax({
			url: remove_subarea.replace('999', $(this).attr('subarea-id')),
			type: 'GET'
		}).done(function(){
			reload_area_setup();
		});
	});
    $('#subarea-modal-edit-confirm #modal-confirm').click(function(){
        $.ajax({
            url: edit_subarea.replace('999', $(this).attr('subarea-id')),
            type: 'POST',
            data: {'subarea_name': $('#subarea-modal-edit-confirm #modal-subarea-name').val()},
            beforeSend: function(xhr){
                xhr.setRequestHeader("X-CSRFToken", csrf_token);

                if(!$('#subarea-modal-edit-confirm #modal-subarea-name').val().trim()) {	// Abort if name is empty
                    xhr.abort();
                    $('#subarea-modal-edit-confirm #modal-error').text(gettext("El nombre de la subárea no puede estar vacío"));
                }
                else if($('#subarea-modal-edit-confirm #modal-subarea-name').val() == $('#subarea-modal-edit-confirm #modal-confirm').attr('subarea-name')){	// Abort if no changes were made
                    xhr.abort();
                    $('#subarea-modal-edit-confirm #modal-error').text(gettext("No ha hecho ningún cambio"));
				}
                else {
                    $('#subarea-modal-edit-confirm #modal-error').text("");
                }
            }
        }).done(function(response){
			if(response['error'])
                $('#subarea-modal-edit-confirm #modal-error').text(response['message']);
			else
				reload_area_setup();
        });
    });
    $('.setup-areas-box a.add').click(function(){
        $('#subarea-modal-add #modal-area-name').text($(this).attr('area-name'));
        $('#subarea-modal-add #modal-confirm').attr('area-id', $(this).attr('area-id'));
        $('#subarea-modal-add').removeClass('modal-hidden').addClass('modal-visible');
        $('#modal-curtain').removeClass('curtain-hidden').addClass('curtain-visible');
    });
    $('#subarea-modal-add #modal-cancel').click(function(){
        $('#subarea-modal-add').addClass('modal-hidden').removeClass('modal-visible');
        $('#modal-curtain').addClass('curtain-hidden').removeClass('curtain-visible');
    });
    $('#subarea-modal-add #modal-confirm').click(function(){
        $.ajax({
            url: reload,
            type: 'POST',
            data: {'subarea_name': $('#subarea-modal-add #add-subarea-name').val(), 'area_id': $('#subarea-modal-add #modal-confirm').attr('area-id')},
            beforeSend: function(xhr){
                xhr.setRequestHeader("X-CSRFToken", csrf_token);

                if(!$('#subarea-modal-add #add-subarea-name').val().trim()) {	// Abort if name is empty
                    xhr.abort();
                    $('#subarea-modal-add #modal-error').text(gettext("El nombre de la subárea no puede estar vacío"));
                }
                else {
                    $('#subarea-modal-add #modal-error').text("");
                }
            }
        }).done(function(response){
            if(response['error'])
                $('#subarea-modal-add #modal-error').text(response['message']);
            else
                reload_area_setup();
        });
    });

    // Areas
    $('.setup-areas-box a.delete').click(function(){
        $('#area-modal-delete-confirm #modal-area-name').text($(this).attr('area-name'));
        $('#area-modal-delete-confirm #modal-confirm').attr('area-id', $(this).attr('area-id'));
        $('#area-modal-delete-confirm').removeClass('modal-hidden').addClass('modal-visible');
        $('#modal-curtain').removeClass('curtain-hidden').addClass('curtain-visible');
    });
    $('.setup-areas-box a.edit').click(function(){
        $('#area-modal-edit-confirm #modal-confirm').attr('area-id', $(this).attr('area-id'));
        $('#area-modal-edit-confirm #modal-confirm').attr('area-name', $(this).attr('area-name'));
        $('#area-modal-edit-confirm #modal-area-name').val($(this).attr('area-name'));
        $('#area-modal-edit-confirm').removeClass('modal-hidden').addClass('modal-visible');
        $('#modal-curtain').removeClass('curtain-hidden').addClass('curtain-visible');
        $('#area-modal-edit-confirm #modal-error').text("");
    });
    $('#area-modal-delete-confirm #modal-cancel').click(function(){
        $('#area-modal-delete-confirm').addClass('modal-hidden').removeClass('modal-visible');
        $('#modal-curtain').addClass('curtain-hidden').removeClass('curtain-visible');
    });
    $('#area-modal-edit-confirm #modal-cancel').click(function(){
        $('#area-modal-edit-confirm').addClass('modal-hidden').removeClass('modal-visible');
        $('#modal-curtain').addClass('curtain-hidden').removeClass('curtain-visible');
    });
    $('#area-modal-delete-confirm #modal-confirm').click(function(){
        $.ajax({
            url: remove_area.replace('999', $(this).attr('area-id')),
            type: 'GET'
        }).done(function(){
            reload_area_setup();
        });
    });
    $('#area-modal-edit-confirm #modal-confirm').click(function(){
        $.ajax({
            url: edit_area.replace('999', $(this).attr('area-id')),
            type: 'POST',
            data: {'area_name': $('#area-modal-edit-confirm #modal-area-name').val()},
            beforeSend: function(xhr){
                xhr.setRequestHeader("X-CSRFToken", csrf_token);

                if(!$('#area-modal-edit-confirm #modal-area-name').val().trim()) {	// Abort if name is empty
                    xhr.abort();
                    $('#area-modal-edit-confirm #modal-error').text(gettext("El nombre del área no puede estar vacío"));
                }
                else if($('#area-modal-edit-confirm #modal-area-name').val() == $('#area-modal-edit-confirm #modal-confirm').attr('area-name')){	// Abort if no changes were made
                    xhr.abort();
                    $('#area-modal-edit-confirm #modal-error').text(gettext("No ha hecho ningún cambio"));
                }
                else {
                    $('#area-modal-edit-confirm #modal-error').text("");
                }
            }
        }).done(function(response){
            if(response['error'])
                $('#area-modal-edit-confirm #modal-error').text(response['message']);
            else
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

				if(!$('#add-area-name').val().trim())	// Abort if email is empty
					xhr.abort();
				else {
					$('#add-area-submit').val(gettext("Agregando...")).attr("disabled", true);
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
		data: {'section_id': id},
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

function reload_webpage_subsection_setup(id){
    $.ajax({
        url: reload,
        method: 'POST',
        data: {'subsection_id': id},
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

            $('#webpage-subsection-setup').children().remove();
            $('#webpage-subsection-setup').append(html);
        }
    });
}

function webpage(){
	var imgIndex = 0;
	var src = '';
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

	/*
	// Keep editors title on scroll
	$('.body').bind('scroll', function(){
		if ($('.body').scrollTop() > 1000 && $(document).width() > 1100){
            var parent = $('.editor-box');
            var width = parent.css('width').replace('px', '') - 2;
			$('.setup-webpage-list').addClass('fixed');
            $('.setup-webpage-list').css('width', width);
			$(this).css('z-index', '100');

            $(window).resize(function(){
                var parent = $('.editor-box');
                var width = parent.css('width').replace('px', '') - 2;
                $('.setup-webpage-list').css('width', width);
            });
		}
		else{
            $(window).unbind('resize');
			$('.setup-webpage-list').removeClass('fixed');
            $('.setup-webpage-list').css('width', '110%');
			$(this).css('z-index', '');
		}
	});
	*/

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
        $('#modal-curtain').removeClass('curtain-hidden').addClass('curtain-visible');
        $.fancybox.showLoading();

        var submitContent = function(urls){
        	if(urls != null){
                var images = $('#spanish-body-edit_ifr').contents().find('img[image-id]');
                images.each(function(i, image){
                    var url = urls[$(image).attr('image-id')];
                    $(image).attr('src', url);
                    $(image).attr('data-mce-src', url);
                    $(image).attr('image-id', null);
                });
			}

			var edit_url = '';
        	var $this = $('#spanish-accept-box');
            if($this.attr('section-id'))
                edit_url = edit.replace('999', $this.attr('section-id'));
            else
                edit_url = edit_subsection.replace('999', $this.attr('subsection-id'));

            $.ajax({
                url: edit_url,
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
                    spanish_title_edit.startContent = spanish_title_edit.getContent();
                    spanish_body_edit.startContent = spanish_body_edit.getContent();
                    $.fancybox.hideLoading();
                    $('#modal-curtain').removeClass('curtain-visible').addClass('curtain-hidden');
                }
            });
        };

        // Get editor new images
        var images = $('#spanish-body-edit_ifr').contents().find('img[image-id]');
        submitSectionImages(images, submitContent, $('#section-select').val(), spanish_title_edit, spanish_body_edit);
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
        $('#modal-curtain').removeClass('curtain-hidden').addClass('curtain-visible');
        $.fancybox.showLoading();

        var submitContent = function(urls){
            if(urls != null){
                var images = $('#english-body-edit_ifr').contents().find('img[image-id]');
                images.each(function(i, image){
                    var url = urls[$(image).attr('image-id')];
                    $(image).attr('src', url);
                    $(image).attr('data-mce-src', url);
                    $(image).attr('image-id', null);
                });
            }

            var edit_url = '';
            var $this = $('#english-accept-box');
            if($this.attr('section-id'))
                edit_url = edit.replace('999', $this.attr('section-id'));
            else
                edit_url = edit_subsection.replace('999', $this.attr('subsection-id'));

            $.ajax({
                url: edit_url,
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
                    english_title_edit.startContent = english_title_edit.getContent();
                    english_body_edit.startContent = english_body_edit.getContent();
                    $.fancybox.hideLoading();
                    $('#modal-curtain').removeClass('curtain-visible').addClass('curtain-hidden');
                }
            });
        };

        // Get editor new images
        var images = $('#english-body-edit_ifr').contents().find('img[image-id]');
        submitSectionImages(images, submitContent, $('#section-select').val(), english_title_edit, english_body_edit);
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
		language: current_lang,
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
		language: current_lang,
		setup: function(ed){
			ed.on('loadContent', function(){    // Avoid to loose <p> class when everything is deleted
				$(ed.getBody()).bind('DOMNodeInserted', function(e){
					var element = e.target;
					if(element.tagName == 'IMG'){	// Identify new images
						if(!$(element).attr('src')){
							$(element).attr('src', src);
							$(element).attr('image-id', imgIndex++);
							src = '';
						}
                    }
				});
			})
		},
		media_poster: false,
        file_browser_callback_types: 'image',
        file_picker_callback: function(callback, value, meta){
            if(meta.filetype == 'image'){
            	if($(this).attr('id') == 'spanish-body-edit')
            		$('#spanishImageField').click();
            	else if($(this).attr('id') == 'english-body-edit')
                    $('#englishImageField').click();
            }
		}
	});
    $('#spanishImageField, #englishImageField').change(function(evt){
        var field = $(this);
        var input = evt.target;
        var id = field.attr('id');
        var closeButton = top.$('.mce-btn.mce-open').parent().find('.mce-textbox').closest('.mce-window').find('.mce-close');

        closeButton.click();
        $('#modal-curtain').removeClass('curtain-hidden').addClass('curtain-visible');
        $.fancybox.showLoading();

        // Read image in base64 and insert it into editor
        var reader = new FileReader();
        reader.onloadend = function(){
            var img = $(new Image());
            src = reader.result;

            if(id == 'spanishImageField')
                tinyMCE.get('spanish-body-edit').execCommand("mceInsertContent", false, img.get(0).outerHTML);
            else if(id == 'englishImageField')
                tinyMCE.get('english-body-edit').execCommand("mceInsertContent", false, img.get(0).outerHTML);

            field.val('');
            $.fancybox.hideLoading();
            $('#modal-curtain').removeClass('curtain-visible').addClass('curtain-hidden');
        };

        reader.readAsDataURL(input.files[0]);
    });

    $(document).ready(function(){
        $('a.modal.picture').fancybox({
            scrolling: false,
            autoSize: false,
            width: 800
        });
    });
    (function($){
		/* Resetea el input de archivos */
        $.fn.resetInput = function(){
            this.wrap('<form>').closest('form').get(0).reset();
            this.unwrap();
        };
    })(jQuery);

	/* Header image */
    $('.selectHeader').click(function(){
        $('#headerField').click();
    });
    $('#changeHeader #changeImage').click(function(){
        $('#headerField').click();
    });
    $('#changeHeader #selectImage').click(function(){
        selectHeader();
    });
    $('#headerField').change(function(){
        if(this.files.length > 0){
            if (!this.files[0].name.match(/\.(jpg|jpeg|png|gif)$/i))
                alert('Debes seleccionar una imagen');
            else{
                $.fancybox.showLoading();
                $('#changeHeader .editor').css('display', 'flex');
                $('#changeHeader .editor').animate({
                    top: '0',
                    opacity: 1
                }, 200);

                readHeaderURL(this);
                $(this).resetInput();
            }
        }
    });

	// Obtiene la url del archivo ingresado por el input
    function readHeaderURL(input) {
        if (input.files && input.files[0]) {
            var reader = new FileReader();

            reader.onload = function (e) {
                $('#changeHeader #imageCropper').attr('src', e.target.result);
                $.fancybox.hideLoading();
                $('a.modal.picture.header').click();
                resetHeaderCrop();
            };

            reader.readAsDataURL(input.files[0]);
        }
    }

	// Activa el editor de imagen
    function enableHeaderCrop(){
        var aspectRatio = 64 / 21;
        cropper = $('#changeHeader #imageCropper').cropper({
            zoomable: false,
            aspectRatio: aspectRatio,
            viewMode: 1,
            background: false
        });
    }

    function resetHeaderCrop(){
        $('#changeHeader #imageCropper').cropper('destroy');
        enableHeaderCrop();
    }

    function selectHeader(){
        $.fancybox.showLoading();
        $('#changeHeader #imageCropper').cropper('disable');

		$('#changeHeader #imageCropper').cropper('getCroppedCanvas', {width: 1600, height: 515}).toBlob(function(blob){
            var form = new FormData();
            form.append('csrfmiddlewaretoken', csrf_token);
            form.append('section_id', $('#changeHeader #selectImage').attr('section-id'));
			form.append('header', blob);

            $.ajax({
                url: upload_header_url,
                method: "POST",
                data: form,
                processData: false,
                contentType: false
            }).done(function(response){
            	if(response.redirect)
                    window.location.href = response.redirect;
                else if(!response['error']){
                	var url = response['url'];

					$('.selectHeader.erasable').remove();
					$('.selectHeader img').attr('src', url + '?' + Date.now()).parent('a').css('display', 'block');

					$('#changeHeader #imageCropper').cropper('enable');
					$.fancybox.hideLoading();
					$.fancybox.close();
                }
            });
		});
    }

	/* Category Thumbnail Image */
    $('.selectThumbnail').click(function(){
        $('#changeThumbnail #selectImage').attr('category-id', $(this).attr('category-id'));
        $('#thumbnailField').click();
    });
    $('#changeThumbnail #changeImage').click(function(){
        $('#thumbnailField').click();
    });
    $('#changeThumbnail #selectImage').click(function(){
        selectThumbnail();
    });
    $('#thumbnailField').change(function(){
        if(this.files.length > 0){
            if (!this.files[0].name.match(/\.(jpg|jpeg|png|gif)$/i))
                alert('Debes seleccionar una imagen');
            else{
                $.fancybox.showLoading();
                $('#changeThumbnail .editor').css('display', 'flex');
                $('#changeThumbnail .editor').animate({
                    top: '0',
                    opacity: 1
                }, 200);

                readThumbnailURL(this);
                $(this).resetInput();
            }
        }
    });

    // Obtiene la url del archivo ingresado por el input
    function readThumbnailURL(input) {
        if (input.files && input.files[0]) {
            var reader = new FileReader();

            reader.onload = function (e) {
                $('#changeThumbnail #imageCropper').attr('src', e.target.result);
                $.fancybox.hideLoading();
                $('a.modal.picture.thumbnail').click();
                resetThumbnailCrop();
            };

            reader.readAsDataURL(input.files[0]);
        }
    }

    // Activa el editor de imagen
    function enableThumbnailCrop(){
        var aspectRatio = 1 / 1;
        cropper = $('#changeThumbnail #imageCropper').cropper({
            zoomable: false,
            aspectRatio: aspectRatio,
            viewMode: 1,
            background: false
        });
    }

    function resetThumbnailCrop(){
        $('#changeThumbnail #imageCropper').cropper('destroy');
        enableThumbnailCrop();
    }

    function selectThumbnail(){
        $.fancybox.showLoading();
        $('#changeThumbnail #imageCropper').cropper('disable');

        $('#changeThumbnail #imageCropper').cropper('getCroppedCanvas', {width: 450, height: 450}).toBlob(function(blob){
        	var category_id = $('#changeThumbnail #selectImage').attr('category-id');

            var form = new FormData();
            form.append('csrfmiddlewaretoken', csrf_token);
            form.append('category_id', category_id);
            form.append('thumbnail', blob);

            $.ajax({
                url: upload_thumbnail_url,
                method: "POST",
                data: form,
                processData: false,
                contentType: false
            }).done(function(response){
                if(response.redirect)
                    window.location.href = response.redirect;
                else if(!response['error']){
                    var url = response['url'];

                    $('.selectThumbnail[category-id=' + category_id + '].erasable').remove();
                    $('.selectThumbnail[category-id =' + category_id + '] img').attr('src', url + '?' + Date.now()).parent('div').css('display', 'block');

                    $('#changeThumbnail #imageCropper').cropper('enable');
                    $.fancybox.hideLoading();
                    $.fancybox.close();
                }
            });
        });
    }
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
	$(document).ready(function(){	// Restore selector on back button
		var select = $('#section-select');
        select.val(select.find('option[selected]').val());
	});
	$('#section-select').change(function(){
		reload_webpage_setup(this.value);
	});
}

function webpage_subsection_init(){
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

    $('#subsection-select').change(function(){
        if(this.value == '-1')
            reload_webpage_setup($('#section-select').val());
        else
            reload_webpage_subsection_setup(this.value);
    });
}

function submitSectionImages(images, submitContent, section_id, title_edit, body_edit){
    // Save images before save content
    if(images.length > 0){
        var form = new FormData();
        form.append('csrfmiddlewaretoken', csrf_token);
        form.append('section_id', section_id);

        var submitAJAX = function(){
            $.ajax({
                url: save_images_url,
                method: "POST",
                data: form,
                processData: false,
                contentType: false
            }).done(function(response){
                if(response.redirect)
                    window.location.href = response.redirect;
                else if(!response['error'])
                    submitContent(response['urls']);
                else{
                    $.fancybox.hideLoading();
                    $('#modal-curtain').removeClass('curtain-visible').addClass('curtain-hidden');
                    title_edit.setMode('design');
                    body_edit.setMode('design');
                }
            })
        };

        // Save images binary in form
        var counter = 0;
        images.each(function(i, image){
            getBlobFromURL(image.src, function(blob){	// Get blob object from url created by the editor
                form.append($(image).attr('image-id'), blob);
                counter++;

                if(counter == images.length)	// Submit only when all images are in form
                    submitAJAX();
            });
        });
    }
    else
        submitContent(null);
}

// Utilities
function getBlobFromURL(url, callback){
    var blob = null;
    var xhr = new XMLHttpRequest();
    xhr.open("GET", url);
    xhr.responseType = "blob";	// force the HTTP response, response-type header to be blob
    xhr.onload = function(){
        blob = xhr.response;
        callback(blob);
    };

    xhr.send();
}

// Gallery View
function reload_gallery_setup(){
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
            $('#gallery-setup').children().remove();
            $('#gallery-setup').append(html);
            $.fancybox.hideLoading();
            $.fancybox.close();
        }

    });
}

function gallery(){
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

    $(document).ready(function(){
        $('a.modal.picture').fancybox({
            scrolling: false,
            autoSize: false
        });
    });
    (function($){
		/* Resetea el input de archivos */
        $.fn.resetInput = function(){
            this.wrap('<form>').closest('form').get(0).reset();
            this.unwrap();
        };
    })(jQuery);

    $('.gallery-photo.photo').parent().click(function(){
    	$('#showPicture #imageCropper').attr('src', $(this).find('.gallery-photo').attr('url'));
        $('#showPicture #deleteImage').attr('photo-id', $(this).attr('photo-id'));
        $('a.modal.show.picture').click();
        $('#showPicture .editor').css('display', 'flex');
        $('#showPicture .editor').animate({
            top: '0',
            opacity: 1
        }, 200);
	});
    $('.addPhoto').click(function(){
        $('#pictureField').click();
    });
    $('#showPicture #deleteImage').click(function(){
    	var id = $(this).attr('photo-id');
    	$.fancybox.showLoading();

        $.ajax({
            url: delete_image_url.replace('999', id),
            method: "POST",
            beforeSend: function(xhr){
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            }
        }).done(function(response){
            if(response.redirect)
                window.location.href = response.redirect;
            else if(!response['error'])
                reload_gallery_setup();
            else
                $.fancybox.hideLoading();
        });
    });
    $('#changePicture #changeImage').click(function(){
        $('#pictureField').click();
    });
    $('#changePicture #selectImage').click(function(){
        selectPicture();
    });
    $('#pictureField').change(function(){
        if(this.files.length > 0){
            if (!this.files[0].name.match(/\.(jpg|jpeg|png|gif)$/i))
                alert('Debes seleccionar una imagen');
            else{
                $.fancybox.showLoading();
                $('#changePicture .editor').css('display', 'flex');
                $('#changePicture .editor').animate({
                    top: '0',
                    opacity: 1
                }, 200);

                readURL(this);
                $(this).resetInput();
            }
        }
    });

    // Obtiene la url del archivo ingresado por el input
    function readURL(input) {
        if (input.files && input.files[0]) {
            var reader = new FileReader();

            reader.onload = function (e) {
                $('#changePicture #imageCropper').attr('src', e.target.result);
                $.fancybox.hideLoading();
                $('a.modal.change.picture').click();
            };

            reader.readAsDataURL(input.files[0]);
        }
    }

    function convertDataURIToBinary(dataURI) {
        // convert base64 to raw binary data held in a string
        // doesn't handle URLEncoded DataURIs - see SO answer #6850276 for code that does this
        var byteString = atob(dataURI.split(',')[1]);
        // separate out the mime component
        var mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];
        // write the bytes of the string to an ArrayBuffer
        var ab = new ArrayBuffer(byteString.length);
        var dw = new DataView(ab);
        for(var i = 0; i < byteString.length; i++) {
            dw.setUint8(i, byteString.charCodeAt(i));
        }
        // write the ArrayBuffer to a blob, and you're done
        return new Blob([ab], {type: mimeString});
    }

    function selectPicture(){
        $.fancybox.showLoading();

		var form = new FormData();
		form.append('csrfmiddlewaretoken', csrf_token);
		form.append('image', convertDataURIToBinary($('#changePicture #imageCropper').attr('src')));

		$.ajax({
			url: upload_image_url,
			method: "POST",
			data: form,
			processData: false,
			contentType: false
		}).done(function(response){
			if(response.redirect)
				window.location.href = response.redirect;
			else if(!response['error'])
				reload_gallery_setup();
			else
				$.fancybox.hideLoading();
		});
    }
}

// News View
function reload_news_setup(){
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
            $('#news-setup').children().remove();
            $('#news-setup').append(html);
        }

    });
}

function news(){
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
    $('.setup-publish-news-box').click(function(){
        $.ajax({
            url: publish.replace('999', $(this).attr('news-id')),
            type: 'GET'
        }).done(function(){
            reload_news_setup();
        });
    });
    $('.setup-unpublish-news-box').click(function(){
        $.ajax({
            url: unpublish.replace('999', $(this).attr('news-id')),
            type: 'GET'
        }).done(function(){
            reload_news_setup();
        });
    });
    $('.setup-pin-news-box').click(function(){
    	if($(this).hasClass('no-hover'))
    		return;

    	var header_url = '';
    	var $this = $(this);
        $this.addClass('no-hover');	// No hover color

    	if($(this).hasClass('selected'))
    		header_url = hide_header;
    	else
            header_url = show_header;

        $.ajax({
            url: header_url.replace('999', $(this).attr('news-id')),
            type: 'GET'
        }).done(function(){
            $this.removeClass('bounce-animation-target');
            void $this.get(0).offsetWidth;	// Let restart css animation
            if($this.hasClass('selected'))
                $this.removeClass('selected');
            else
                $this.addClass('selected');

            $this.addClass('bounce-animation-target');	// Start bouncing animation
            $(document).mousemove(function(){	// On mousemove, enable hover
            	$(this).unbind('mousemove');
            	$this.removeClass('no-hover');
			});
        });
    });
    $('a.delete.modal').fancybox({
        autoSize: true,
        beforeShow: function(links, index){
            var self = $(this.element);
            $('.confirm[type="title"]').attr('data', self.attr('data-title')).html(self.attr('data-title'));
            $('.confirm[type="date"]').attr('data', self.attr('data-date')).html(self.attr('data-date'));
            $('.confirm[type="send"]').click(function(){
                $.ajax({
                    url: remove.replace('999', self.attr('data-id')),
                    type: 'GET'
                }).done(function(){
                    $.fancybox.close();
                    reload_news_setup();
                });
			});
        }
    });
}

// Events View
function reload_events_setup(){
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
            $('#events-setup').children().remove();
            $('#events-setup').append(html);
        }

    });
}

function events(){
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

    $('.setup-publish-news-box').click(function(){
        $.ajax({
            url: publish.replace('999', $(this).attr('news-id')),
            type: 'GET'
        }).done(function(){
            reload_news_setup();
        });
    });
    $('.setup-unpublish-news-box').click(function(){
        $.ajax({
            url: unpublish.replace('999', $(this).attr('news-id')),
            type: 'GET'
        }).done(function(){
            reload_news_setup();
        });
    });
    $('a.delete.modal').fancybox({
        autoSize: true,
        beforeShow: function(links, index){
            var self = $(this.element);
            $('.confirm[type="title"]').attr('data', self.attr('data-title')).html(self.attr('data-title'));
            $('.confirm[type="date"]').attr('data', self.attr('data-date')).html(self.attr('data-date'));
            $('.confirm[type="send"]').click(function(){
                $.ajax({
                    url: remove.replace('999', self.attr('data-id')),
                    type: 'GET'
                }).done(function(){
                    $.fancybox.close();
                    reload_events_setup();
                });
            });
        }
    });
}

function events_create(){
	function init_pickers(){
        $('#create-event-form .date input').datepicker({
			firstDay: 1,
			dateFormat: 'dd-mm-yy'
		});

        $('#create-event-form .time').clockpicker({
            placement: 'top', // clock popover placement
            align: 'right',       // popover arrow align
            autoclose: true,
            default: '00:00'
        });
	}

	function areInputsFilled(){
		var areFilled = true;
		$('#create-event-form .text').each(function(){
			if(!$(this).val().trim()){
                areFilled = false;
				return false;
			}
		});

		return areFilled;
	}

	function checkInputs(){
        if(areInputsFilled()) {
            $('#submitEvent').attr('disabled', false);
        }
        else
            $('#submitEvent').attr('disabled', true);
	}

    function showError(){
        $.fancybox($('#errorModal').parent('div').html(), {
            closebtn: false,
            autoSize: false,
            width: 400,
            height: 100,
            scrolling: false,
            closeBtn: false
        });
    }

    function removeDay(){
        var row = $(this).parent().parent();
        var rowsCount = $('#create-event-form .table table > tbody tr').length;
        --rowsCount;

        if(rowsCount > 0){
            var count = row.find('.num').text();
            row.nextAll().each(function(){
                $(this).find('.num').text(count++);
            });

            row.remove();
        }

        checkInputs();

        if(rowsCount > 1)
            $('.remove-day').css('display', 'inline-block');
        else
            $('.remove-day').css('display', 'none');
    }

	$(document).ready(function(){
        if(current_lang == 'es'){
            $.datepicker.regional['es'] = {
                closeText: 'Cerrar',
                prevText: '<Ant',
                nextText: 'Sig>',
                currentText: 'Hoy',
                monthNames: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
                monthNamesShort: ['Ene','Feb','Mar','Abr', 'May','Jun','Jul','Ago','Sep', 'Oct','Nov','Dic'],
                dayNames: ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
                dayNamesShort: ['Dom','Lun','Mar','Mié','Juv','Vie','Sáb'],
                dayNamesMin: ['Do','Lu','Ma','Mi','Ju','Vi','Sá'],
                weekHeader: 'Sm',
                dateFormat: 'dd/mm/yy',
                firstDay: 1,
                isRTL: false,
                showMonthAfterYear: false,
                yearSuffix: ''
            };
            $.datepicker.setDefaults($.datepicker.regional['es']);
        }

		init_pickers();
        $('#create-event-form .text').val('');
        $('#create-event-form input[type="file"]').val('');

        $('#create-event-form .text').on('input', checkInputs);
        $('#create-event-form .date, #create-event-form .time').change(checkInputs);

        var rowsCount = $('#create-event-form .table table > tbody tr').length;
        if(rowsCount > 1)
            $('.remove-day').css('display', 'inline-block');
        else
            $('.remove-day').css('display', 'none');
    });

    $('.add-day').click(function(){
        var tbody = $('#create-event-form .table table > tbody');
        var row = $('#create-event-form .table table > tbody > tr').first().clone();
        var rowsCount = $('#create-event-form .table table > tbody tr').length;
        row.find('input').val('');
        row.find('.num').text(++rowsCount);
        row.find('.date').find('input').removeAttr('id').removeClass('hasDatepicker');
        row.find('.remove').find('.remove-day').click(removeDay);

        tbody.append(row);
        row.find('.date, .time').change(checkInputs);
        row.find('.location').on('input', checkInputs);
        init_pickers();
        checkInputs();

        if(rowsCount > 1)
        	$('.remove-day').css('display', 'inline-block');
        else
            $('.remove-day').css('display', 'none');
    });

    $('.remove-day').click(removeDay);

    $('#create-event-form').submit(function(e){
        e.preventDefault();

        var days = [];
        $('#create-event-form .table table > tbody tr').each(function(){
        	var day = {};
        	day['day'] = $(this).find('.date input').val();
            day['begin_hour'] = $(this).find('.time.begin-hour input').val();
            day['end_hour'] = $(this).find('.time.end-hour input').val();
            day['location'] = $(this).find('.location input').val();

        	days.push(day);
		});

        var form = new FormData(this);
        form.append('days', JSON.stringify(days));

        $.ajax({
            url: create_event_url,
            method: "POST",
            data: form,
            contentType: false,
            processData: false,
            beforeSend: function(xhr){
                if(!areInputsFilled())	// Abort if required inputs are not filled
                    xhr.abort();
            }
        }).done(function(response){
            if(response.redirect)
                window.location.href = response.redirect;
            else if(response['error'])
                showError();
        });
	});
}

function events_edit(){
	var rowsCount = 0;
	var removeDays = [];

    function init_pickers(){
        $('#edit-event-form .date input').datepicker({
            firstDay: 1,
            dateFormat: 'dd-mm-yy'
        });

        $('#edit-event-form .time').clockpicker({
            placement: 'top', // clock popover placement
            align: 'right',       // popover arrow align
            autoclose: true,
            default: '00:00'
        });
    }

    function areInputsFilled(){
        var areFilled = true;
        $('#edit-event-form .text').each(function(){
            if(!$(this).val().trim()){
                areFilled = false;
                return false;
            }
        });

        return areFilled;
    }

    function isNewData(){
        var isNew = false;
        $('#edit-event-form .text').each(function(){
            if($(this).val() != $(this).attr('original')){
                isNew = true;
                return false;
            }
        });

        if(isNew)
            return true;

        $('#edit-event-form input[type="file"]').each(function(){
        	if($(this).val()){
        		isNew = true;
        		return false;
			}
		});

        return isNew;
    }

    function checkInputs(){
    	var actualRowsCount = $('#edit-event-form .table table > tbody tr').length;
        if(areInputsFilled() && (actualRowsCount != rowsCount || isNewData() || removeDays.length > 0)) {
            $('#submitEvent').attr('disabled', false);
        }
        else
            $('#submitEvent').attr('disabled', true);
    }

    function showError(){
        $.fancybox($('#errorModal').parent('div').html(), {
            closebtn: false,
            autoSize: false,
            width: 400,
            height: 100,
            scrolling: false,
            closeBtn: false
        });
    }

    function removeDay(){
        var row = $(this).parent().parent();
        var rowsCount = $('#edit-event-form .table table > tbody tr').length;
        --rowsCount;

        if(rowsCount > 0){
            if(row.attr('day-id'))
                removeDays.push(row.attr('day-id'));

            var count = row.find('.num').text();
            row.nextAll().each(function(){
            	$(this).find('.num').text(count++);
			});

            row.remove();
        }

        checkInputs();

        if(rowsCount > 1)
            $('.remove-day').css('display', 'inline-block');
        else
            $('.remove-day').css('display', 'none');
	}

    $(document).ready(function(){
        if(current_lang == 'es'){
            $.datepicker.regional['es'] = {
                closeText: 'Cerrar',
                prevText: '<Ant',
                nextText: 'Sig>',
                currentText: 'Hoy',
                monthNames: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
                monthNamesShort: ['Ene','Feb','Mar','Abr', 'May','Jun','Jul','Ago','Sep', 'Oct','Nov','Dic'],
                dayNames: ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
                dayNamesShort: ['Dom','Lun','Mar','Mié','Juv','Vie','Sáb'],
                dayNamesMin: ['Do','Lu','Ma','Mi','Ju','Vi','Sá'],
                weekHeader: 'Sm',
                dateFormat: 'dd/mm/yy',
                firstDay: 1,
                isRTL: false,
                showMonthAfterYear: false,
                yearSuffix: ''
            };
            $.datepicker.setDefaults($.datepicker.regional['es']);
        }

        init_pickers();
        rowsCount = $('#edit-event-form .table table > tbody tr').length;
        $('#edit-event-form .text').each(function(){
            $(this).attr('original', $(this).val());
        });

        $('#edit-event-form .text').on('input', checkInputs);
        $('#edit-event-form .date, #edit-event-form .time, #edit-event-form input[type="file"]').change(checkInputs);

        if(rowsCount > 1)
            $('.remove-day').css('display', 'inline-block');
        else
            $('.remove-day').css('display', 'none');
    });

    $('.add-day').click(function(){
        var tbody = $('#edit-event-form .table table > tbody');
        var row = $('#edit-event-form .table table > tbody > tr').first().clone();
        var rowsCount = $('#edit-event-form .table table > tbody tr').length;
        row.find('input').val('');
        row.find('.num').text(++rowsCount);
        row.find('.date').find('input').removeAttr('id').removeClass('hasDatepicker');
        row.find('.remove').find('.remove-day').click(removeDay);
        row.removeAttr('day-id');

        tbody.append(row);
        row.find('.date, .time').change(checkInputs);
        row.find('.location').on('input', checkInputs);
        init_pickers();
        checkInputs();

        if(rowsCount > 1)
            $('.remove-day').css('display', 'inline-block');
        else
            $('.remove-day').css('display', 'none');
    });

    $('.remove-day').click(removeDay);

    $('#edit-event-form').submit(function(e){
        e.preventDefault();
        var actualRowsCount = $('#edit-event-form .table table > tbody tr').length;

        var days = [];
        $('#edit-event-form .table table > tbody tr').each(function(){
            var day = {};
            var id = $(this).attr('day-id');
            if(id)
            	day['id'] = id;

            day['day'] = $(this).find('.date input').val();
            day['begin_hour'] = $(this).find('.time.begin-hour input').val();
            day['end_hour'] = $(this).find('.time.end-hour input').val();
            day['location'] = $(this).find('.location input').val();

            days.push(day);
        });

        var form = new FormData(this);
        form.append('days', JSON.stringify(days));
        form.append('remove_days', JSON.stringify(removeDays));

        $.ajax({
            url: edit_event_url.replace('999', id),
            method: "POST",
            data: form,
            contentType: false,
            processData: false,
            beforeSend: function(xhr){
                if(!(areInputsFilled() && (actualRowsCount != rowsCount || isNewData())))
                    xhr.abort();
            }
        }).done(function(response){
            if(response.redirect)
                window.location.href = response.redirect;
            else if(response['error'])
                showError();
        });
    });
}