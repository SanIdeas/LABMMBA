var cropper;


// Members View
function reload_member_setup(msg){
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
			$('#members-setup').children().remove();
			$('#members-setup').append(html);

			if(msg != null)
				$('#add-member-error').text(msg);
		}

	});
};

function create() {
		if(!$('#add-member-name').val().trim())	// Abort if name is empty
			console.log("no nombre");
		else {
			$.fancybox({
     			'href' : '#data',
     			'hideOnContentClick': true,
				'autoSize' : false,
		    	'width'    : "80%",
		    	'height'   : "auto"
  			}); 
			$('#modal-member-img').css('background-image', 'url("/static/intranet/images/default.png")');
			$('#create-title').css('display', '');
			$('#edit-title').css('display', 'none'); 
		    $('#modal-member-name').text($('#add-member-name').val().trim()); 
		    $('#modal-member-description').val(''); 
		    $('#modal-confirm-edit').attr('member-id', ''); 
		}
};

function members(){
    // Animation for iOS

    $('.setup-user-list > li').click(function(e){
        e.preventDefault()
        var row = $(this).find('.setup-user-row');
        var handler = function(){
            row.removeClass('expand-row-target');
        };

        $('*').not($(this)).unbind('click', handler);
        $('*').not($(this)).click(handler);

        row.removeClass('expand-row-target');
        void row.get(0).offsetWidth;
        row.addClass('expand-row-target');
    });


	$('.setup-block-box').click(function(){
		$.ajax({
			url: unwork.replace('999', $(this).attr('member-id')),
			type: 'GET'
		}).done(function(){
			reload_member_setup();
		});
	});
	$('.setup-unblock-box').click(function(){
		$.ajax({
			url: work.replace('999', $(this).attr('member-id')),
			type: 'GET'
		}).done(function(){
			reload_member_setup();
		});
	});
	$('.member').click(function(){
		$('#modal-member-img').css('background-image', 'url(' + $(this).attr('member-img') + ')'); 
	    $('#modal-member-name').text($(this).attr('name')); 
	    $('#modal-member-description').val($(this).attr('description')); 
	    $('#modal-confirm-edit').attr('member-id', $(this).attr('member-id')); 
	    $('#edit-title').css('display', '');
		$('#create-title').css('display', 'none'); 
	});

	$('.delete').click(function(){
		$('#modal-user-img').css('background-image', 'url(' + $(this).attr('member-img') + ')'); 
		$('#modal-user-name').text($(this).attr('user-full-name'));
		$('#modal-confirm').attr('member-id', $(this).attr('member-id'));
	});

	$('#modal-cancel').click(function(){
		$.fancybox.close();
	});
	$('#modal-cancel-edit').click(function(){
		$.fancybox.close();
	});
	$('#modal-confirm').click(function(){
		$.ajax({
			url: remove.replace('999', $(this).attr('member-id')),
			type: 'GET'
		}).done(function(){
			$.fancybox.close();
			reload_member_setup();
		});
	});

	$('#modal-confirm-edit').click(function(e){
		if(!$('#modal-confirm-edit').val().trim())	// if id is empty
			$.ajax({
			url: reload,
			type: 'POST',
			data: {
				member_name: $('#add-member-name').val(),
				member_description: $('#modal-member-description').val()
				},
			beforeSend: function(xhr){
				xhr.setRequestHeader("X-CSRFToken", csrf_token);
				e.preventDefault();

				if(!$('#add-member-name').val().trim())	// Abort if name is empty
					xhr.abort();
				else {
					$('#add-member-submit').val("Agregando...").attr("disabled", true);
					$('#add-member-error').text("");
				}
			}
		}).done(function(data){
			$.fancybox.close();
			reload_member_setup();
		});

		else {
			$.ajax({
			url: edit.replace('999', $(this).attr('member-id')),
			type: 'POST',
			data: {
				member_name: $('#modal-member-name').val(),
				member_description: $('#modal-member-description').val()
				},
			beforeSend: function(xhr){
				xhr.setRequestHeader("X-CSRFToken", csrf_token);
				e.preventDefault();
				}
		}).done(function(){
			$.fancybox.close();
			reload_member_setup();
		});
		

		}
});
}

$.extend(jQuery.easing,{outcubic:function(x,t,b,c,d){
	var ts = Number=(t/=d)*t;
	var tc = Number=ts*t;
	return b+c*(tc + -3*ts + 3*t);
}})
// Obtiene la url del archivo ingresado por el input
function readURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function (e) {
            $('#imageCropper').attr('src', e.target.result);
			resetCrop();
        }

        reader.readAsDataURL(input.files[0]);
    }
}

// Activa el editor de imagen
function enableCrop(){
	var preview = $('.profile.image').children('div');
	cropper = $('#imageCropper').cropper({
		zoomable: false,
		aspectRatio: 1 / 1,
		viewMode: 1,
		background: false,
		build: function(e){
			var $clone = $(this).clone();
			$clone.attr('id', '');
			preview.html($clone);
			$.fancybox.hideLoading();

		},
		crop: function(e) {
			var imageData = $(this).cropper('getImageData');
            var previewAspectRatio = e.width / e.height;

			var previewWidth = preview.width();
			var previewHeight = previewWidth / previewAspectRatio;
			var imageScaledRatio = e.width / previewWidth;

			preview.find('img').height(previewHeight).css({
				width: imageData.naturalWidth / imageScaledRatio,
				height: imageData.naturalHeight / imageScaledRatio,
				marginLeft: -e.x / imageScaledRatio,
				marginTop: -e.y / imageScaledRatio
			});	
		}
	});
}

function resetCrop(){
	$('#imageCropper').cropper('destroy');
	enableCrop();
}

// Envia la nueva foto de perfil
// Desactiva botones y el editor. Los vuelve a activar si falla
function sendPicture(){
	$('#imageCropper').cropper('getCroppedCanvas',{width: 500, height: 500}).toBlob(function(blob){
		$.fancybox.showLoading();
		$('#imageCropper').cropper('disable');
		$('#sendImage').attr('disabled', true);
		var form = new FormData();
		form.append('csrfmiddlewaretoken', csrf_token);
		form.append('picture', blob);
		form.append('member', $('#modal-confirm-edit').attr('member-id'));
		$.ajax({
			url: update_picture_url,
			method: "POST",
			data: form,
			processData: false,
			contentType: false,
		}).done(function(response){
			if(!response['error'])
				location.reload();
		}).error(function(){
			$.fancybox.hideLoading();
			$('#imageCropper').cropper('enable');
			$('#sendImage').attr('disabled', false);
		});
	});
}
function openOptions(id){
	var opt = $('.options[data-id="' + id + '"]');
	if(opt.width() == 0){
		opt.animate({
			width: 160
		}, {
			duration: 200,
			easing: 'outcubic'
		});
	}
	else{
		opt.animate({
			width: 0
		}, {
			duration: 200,
			easing: 'outcubic'
		});	
	}
}
function closeOptions(id){
	var opt = $('.options[data-id="' + id + '"]');
	if(opt.width() > 0){
		opt.animate({
			width: 0
		}, {
			duration: 200,
			easing: 'outcubic'
		});	
	}
}

$(document).ready(function() {
	/* This is basic - uses default settings */
	$('a.modal.picture').fancybox({
		scrolling: false,
		autoSize: false,
	});
	/* Using custom settings */


	$("a.member").fancybox({
		'hideOnContentClick': true,
		'autoSize' : false,
    	'width'    : "80%",
    	'height'   : "auto"
	});

	$("a.delete").fancybox({
		'hideOnContentClick': true,
		'autoSize' : false,
    	'width'    : "80%",
    	'height'   : "auto"
	});

	/* Apply fancybox to multiple items */
	
	$("member.group").fancybox({
		'transitionIn'	:	'elastic',
		'transitionOut'	:	'elastic',
		'speedIn'		:	600, 
		'speedOut'		:	200, 
		'overlayShow'	:	false
	});



	$(window).resize(function(){
		$.fancybox.update();
	});
});