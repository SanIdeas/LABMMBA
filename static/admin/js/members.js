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
}

function members(){

	$('#add-member-form').submit(function(e){
		$.ajax({
			url: reload,
			type: 'POST',
			data: $(this).serialize(),
			beforeSend: function(xhr){
				xhr.setRequestHeader("X-CSRFToken", csrf_token);
				e.preventDefault();

				if($('#add-member-name').val().length <= 0)	// Abort if name is empty
					xhr.abort();
				else {
					$('#add-member-submit').val("Agregando...").attr("disabled", true);
					$('#add-member-error').text("");
				}
			}
		}).done(function(data){
			reload_member_setup(data['message']);
		});
	});
	$('.setup-block-box').click(function(){
		$.ajax({
			url: unwork.replace('999', $(this).attr('member-id')),
			type: 'GET',
		}).done(function(){
			reload_member_setup();
		});
	});
	$('.setup-unblock-box').click(function(){
		$.ajax({
			url: work.replace('999', $(this).attr('member-id')),
			type: 'GET',
		}).done(function(){
			reload_member_setup();
		});
	});
	$('.setup-delete-box').click(function(){
		$('#modal-user-img').css('background-image', 'url(' + $(this).attr('member-img') + ')');
		$('#modal-user-name').text($(this).attr('user-full-name'));
		$('#modal-confirm').attr('member-id', $(this).attr('member-id'));
		$('#modal-delete-confirm').removeClass('modal-hidden').addClass('modal-visible');
		$('#modal-delete').removeClass('curtain-hidden').addClass('curtain-visible');
	});
	$('#modal-cancel').click(function(){
		$('#modal-delete-confirm').addClass('modal-hidden').removeClass('modal-visible');
		$('#modal-delete').addClass('curtain-hidden').removeClass('curtain-visible');
	});
	$('#modal-confirm').click(function(){
		$.ajax({
			url: remove.replace('999', $(this).attr('member-id')),
			type: 'GET',
		}).done(function(){
			reload_member_setup();
		});
	});
	$('.setup-view-box').click(function(){
		$('#modal-member-img').css('background-image', 'url(' + $(this).attr('member-img') + ')');
		$('#modal-member-name').text($(this).attr('user-full-name'));
		$('#modal-member-description').val($(this).attr('user-description'));
		$('#modal-confirm-edit').attr('member-id', $(this).attr('member-id'));
		$('#modal-edit-confirm').removeClass('modal-hidden').addClass('modal-visible');
		$('#modal-edit').removeClass('curtain-hidden').addClass('curtain-visible');
	});
	$('#modal-cancel-edit').click(function(){
		$('#modal-edit-confirm').addClass('modal-hidden').removeClass('modal-visible');
		$('#modal-edit').addClass('curtain-hidden').removeClass('curtain-visible');
	});
	$('#modal-confirm-edit').click(function(e){
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
			reload_member_setup();
		});
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