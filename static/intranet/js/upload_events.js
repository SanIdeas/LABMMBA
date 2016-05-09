//PopupCenter('http://127.0.0.1:8000{% url 'get_credentials' %}', 'Iniciar sesion en Google Drive', 650, 700)
var files = [];
var state = '' //Define el estado. Si es 'single' significa que se esta mostrando un solo archivo gdrive. Si es 'multi' significa que se estan mostrando multiples archivos gdrive.
$('.upload-selector').click(function(){
	if($(this).hasClass('unselect')){
		$(this).removeClass('unselect');
		methodSwitcher($(this).attr('upload-method'));
	}
	else if($(this).attr('frst')){
		$('.upload-selector').removeAttr('frst');
		methodSwitcher($(this).attr('upload-method'));
	}

	if ($(this).attr('upload-method') == 'local')
		$('.upload-selector[upload-method="drive"]').addClass('unselect');
	else
		$('.upload-selector[upload-method="local"]').addClass('unselect');
});

$('#add-btn').click(function(){
	$('#mult-files').click();
});

$('#mult-files').change(function(){
	filesHandler();
	$(this).resetInput();
});

//Envia la solicitud con en enlace a Google Drive
$('#drive-link').change(function(){
	initial_drive_request(link_analizer_link.replace('999', encodeURIComponent($(this).val())));
	//window.open("{% url 'link_analizer' '999' %}".replace('999', encodeURIComponent($(this).val())), '_blank');
});

$('#submit-btn').click(function(){
	download_drive_request();
});


/*$('.type-select').change(function(){
	if($(this).val() == "0")
		$('.frame-header[doc-index="' + $(this).attr('doc-index') + '"]').addClass('public-type').removeClass('private-type');
	else
		$('.frame-header[doc-index="' + $(this).attr('doc-index') + '"]').addClass('private-type').removeClass('public-type');
});*/