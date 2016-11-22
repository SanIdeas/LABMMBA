var cropper;
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
// Abre la ventana para iniciar sesion con google, si los popups estan desactivados le dice al usuario que debe activarlos.
//http://stackoverflow.com/questions/4068373/center-a-popup-window-on-screen
function googleAuthentication() {
	var title = "Google Drive";
	var url = authentication_url;
	var w = 650;
	var h = 700;
    // Fixes dual-screen position                         Most browsers      Firefox
    var dualScreenLeft = window.screenLeft != undefined ? window.screenLeft : screen.left;
    var dualScreenTop = window.screenTop != undefined ? window.screenTop : screen.top;
    
    var left = (window.top.outerWidth -  w )/2 +dualScreenLeft;
    var top = window.top.outerHeight / 2 + window.top.screenY - ( h / 2) + dualScreenTop;
    var newWindow = window.open(url, title, 'scrollbars=yes, width=' + w + ', height=' + h + ', top=' + top + ', left=' + left);

    if(!newWindow || newWindow.closed || typeof newWindow.closed=='undefined') 
		{ 
		     // Ventanas emergentes bloqueadas
		     $.fancybox($('#enablePopupModal').html());
		}
		else{
			 // Puts focus on the newWindow
		    if (window.focus) {
		        newWindow.focus();
		    }
		    // Se detecta cuando la ventana se cierra
		    var timer = window.setInterval(function() {
		    	if (newWindow.closed !== false) { // !== es requerido para la compatibilidad con Opera.
		        	window.clearInterval(timer);
		        	location.reload();
			    }
			}, 200);
		}
}

function changePassword(){
	if($('#new').val() == $('#confirm').val()){
		$('.message.password').html('');
		$('#passSubmit').attr('disabled', true);
		var form  = new FormData($('#passwordForm')[0]);
		$('#passwordForm').find('.text').attr('disabled', true);
		$.ajax({
			url:password_url,
			method: 'POST',
			data: form,
			processData: false,
			contentType: false,
		}).done(function(response){
			if(!response['error']){
				// No hay errores
				$.fancybox($('#successModal').parent('div').html(), {
					closebtn: false,
					autoSize: false,
					width: 300,
					height: 100,
					scrolling: false,
					closeBtn: false,
				});
				setTimeout(function(){
					location.reload();
				}, 1000)
			}
			else{
				// Si hay errores
				$('.message.password').html(response['message']);
				$('#passSubmit').attr('disabled', false);
				$('#passwordForm').find('.text').attr('disabled', false);
			}
		}).error(function(){
			$('#passSubmit').attr('disabled', false);
			$('#passwordForm').find('.text').attr('disabled', false);
		});
	}
	else{
		if(current_lang == 'es')
			$('.message.password').html('Las contraseñas no coinciden.');
		else
			$('.message.password').html(gettext('Las contraseñas no coinciden.'));
	}
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