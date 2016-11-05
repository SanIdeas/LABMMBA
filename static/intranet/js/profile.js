var cropper;
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

			preview.height(previewHeight).find('img').css({
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

function sendPicture(){
	$('#imageCropper').cropper('getCroppedCanvas',{width: 500, height: 500}).toBlob(function(blob){
		$.fancybox.showLoading();
		$('#imageCropper').cropper('disable');
		$('#sendImage').attr('disabled', true);
		var form = new FormData();
		form.append('csrfmiddlewaretoken', csrf_token);
		form.append('picture', blob);
		$.ajax({
			url: update_picture_link,
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