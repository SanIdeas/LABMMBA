var cropper;
var busy = false;
var is_thumbnail; // true: si es una miniatura. false: si es una cabecera
$(document).ready(function(){
	$('a.modal.picture').fancybox({
		scrolling: false,
		autoSize: false,
		width: 800,
	});
});
(function($){
	/* Resetea el input de archivos */
	$.fn.resetInput = function(){
		this.wrap('<form>').closest('form').get(0).reset();
		this.unwrap();
	};
})(jQuery);
$('.selectThumbnail').click(function(){
	if(!busy){
		is_thumbnail = true;

		$('#pictureField').click();
	}
});
$('.selectHeader').click(function(){
	if(!busy){
		is_thumbnail = false;

		$('#pictureField').click();
	}
});		
$('#changeImage').click(function(){
	$('#pictureField').click();
});
$('#selectImage').click(function(){
	selectImage();
});	
$('#pictureField').change(function(){
	if(this.files.length > 0){
		if (!this.files[0].name.match(/\.(jpg|jpeg|png|gif)$/i))
	    	alert('Debes seleccionar una imagen');
		else{
			$.fancybox.showLoading();		
			$('.editor').css('display', 'flex');
			$('.editor').animate({
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
            $('#imageCropper').attr('src', e.target.result);
			$.fancybox.hideLoading();
			$('a.modal.picture').click();
			resetCrop();
        }

        reader.readAsDataURL(input.files[0]);
    }
}

// Activa el editor de imagen
function enableCrop(){
	if(is_thumbnail)
		var aspectRatio = 100 / 77;
	else
		var aspectRatio = 64 / 21
	cropper = $('#imageCropper').cropper({
		zoomable: false,
		aspectRatio: aspectRatio,
		viewMode: 1,
		background: false,
	});
}

function resetCrop(){
	$('#imageCropper').cropper('destroy');
	enableCrop();
}

function selectImage(){
	$.fancybox.showLoading();
	$('#imageCropper').cropper('disable');
	$('#sendImage').attr('disabled', true);
	if(is_thumbnail){
		var url = $('#imageCropper').cropper('getCroppedCanvas',{width: 500, height: 385}).toDataURL();
		$('.selectThumbnail.erasable').remove();
		$('.selectThumbnail img').attr('src', url).attr('new', true).parent('a').css('display', 'block');
	}
	else{
		var url = $('#imageCropper').cropper('getCroppedCanvas',{width: 1600, height: 515}).toDataURL();
		$('.selectHeader.erasable').remove();
		$('.selectHeader img').attr('src', url).attr('new', true).parent('a').css('display', 'block');
		// Se habilita la descripcion corta
		$('textarea[name="mini-description"]').attr('disabled', false);
	}
	$('#imageCropper').cropper('enable');
	$('#sendImage').attr('disabled', false);
	$.fancybox.hideLoading();
	$.fancybox.close();
}