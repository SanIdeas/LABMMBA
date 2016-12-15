$(document).ready(function() {
	$('input.text, input.date').on('input', function(){
		 checkFields();
	});
	$('.image.required').on('load', function(){
		 checkFields();
	});
	$('input[type="submit"].editor-link').click(function(e){
		e.preventDefault();
		// Si el formulario no tiene cambios
		if($('input[type="submit"].news').attr('disabled')){
			window.location.href = live_editor_url.replace('888', id);
		}
		else{
			$('.news form').attr('redirect-to', 'live-editor')
			$('input[type="submit"].news').click();
		}
	});
});

function checkFields() {
	var changed = true;
	var formElement = $('.news form')[0];
	var formStatus = formElement.checkValidity();
	console.log('formStatus', formStatus);
	if(!formStatus){
		changed = false;
	}
	$('.image.required').each(function(){
		if(!$(this).attr('new')){
			changed = false;
		}
		else{
			changed = changed && true;
		}
	});

	if(changed)
		$('input[type="submit"].news').attr('disabled', false);
	else
		$('input[type="submit"].news').attr('disabled', true);
}