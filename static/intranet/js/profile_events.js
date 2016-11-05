var cropper;
$(document).ready(function() {
	$('a.modal').fancybox({
		scrolling: false,
		autoSize: false,
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
})
$('#pictureField').change(function(){
	if(this.files.length > 0){
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
		
		readURL(this);
	}
});