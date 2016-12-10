var cropper;
$(document).ready(function() {
	$('a.modal.picture').fancybox({
		scrolling: false,
		autoSize: false,
	});
	$(window).resize(function(){
		$.fancybox.update();
	});
});
$(window).click(function(e){
	$('.options').each(function(){
		if($(this).attr('data-id') != $(e.target).parent('.options').attr('data-id')){
			closeOptions($(this).attr('data-id'));
		}
	});
})
$('#sendImage').click(function(){
	sendPicture();
});	

$('#selectImage').click(function(){
	$('#pictureField').click();
});	
$('#changeImage').click(function(){
	$('#pictureField').click();
});	
$('.btn').children('button').click(function(){
	openOptions($(this).attr('data-id'));
});
$('.delete').click(function(){
	$('.confirm[type="title"]').attr('data', $(this).attr('data-title')).html($(this).attr('data-title'));
	$('.confirm[type="author"]').attr('data', $(this).attr('data-author')).html($(this).attr('data-author'));
	$('.confirm[type="send"]').attr('data', $(this).attr('data-id'));
	$.fancybox($('#deleteModal').parent('div').html());

	// Se activa la escucha al boton confirmar
	$('.confirm[type="send"]').off();
	$('.confirm[type="send"]').click(function(){
		if($.fancybox.isOpen){
			$.ajax({
				url: encodeURI(edit_document_url.replace('888', $('.confirm[type="send"]').attr('data'))),
				type: "DELETE",
				beforeSend: function(xhr){
					xhr.setRequestHeader("X-CSRFToken", csrf_token);
				}
			}).done(function(response){
				if(!response['error']){
					location.reload();
				}
			});
		};
	});
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
