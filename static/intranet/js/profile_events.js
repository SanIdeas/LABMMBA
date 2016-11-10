var cropper;
$(document).ready(function() {
	$('a.modal.picture').fancybox({
		scrolling: false,
		autoSize: false,
	});
	$('a.modal.google').fancybox({
		scrolling: false,
		autoSize: false,
	});
	$('a.modal.edit').fancybox({
		width: 800,
		height: 'auto',
	});
	$('a.modal.password').fancybox({
		width: 400,
		height: 'auto',
	});
	$(window).resize(function(){
		$.fancybox.update();
	});
});
$('#sendImage').click(function(){
	sendPicture();
});	
$('#selectImage').click(function(){
	$('#pictureField').click();
});	
$('#changeImage').click(function(){
	$('#pictureField').click();
});	
$('#authenticate').click(function(){
	googleAuthentication();
});	
$('#passwordForm').submit(function(e){
	e.preventDefault();
	changePassword();
});
$('#pictureField').change(function(){
	if (!this.files[0].name.match(/\.(jpg|jpeg|png|gif)$/i))
    	alert('Debes seleccionar una imagen');
	else if(this.files.length > 0){
		console.log("asd");
		$.fancybox.showLoading();
		$('#selectImage').animate({
			top: '-20px',
			opacity: 0
		}, 200, function(){
			$(this).remove();
		});
		
		$('.editor').css('display', 'flex');
		$('.editor').animate({
			top: '0',
			opacity: 1
		}, 200);
		
		console.log("asd2");
		readURL(this);
	}
});
