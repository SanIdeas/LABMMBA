//PopupCenter('http://127.0.0.1:8000{% url 'get_credentials' %}', 'Iniciar sesion en Google Drive', 650, 700)
var state = ''; //Define el estado. Si es 'single' significa que se esta mostrando un solo archivo gdrive. Si es 'multi' significa que se estan mostrando multiples archivos gdrive. si es 'confirm' significa que se esta en la ventana de confirmacion.
/* Escucha la los click sobre las opciones iniciales */
$('.upload.option').click(function(){
	/* Una vez hecho el click, las opciones se desvanecen hacia arriba y son eliminadas a los 200 ms */
	hideElement('.upload.selector', true);
	
	/* Dependiendo del tipo del boton, se llaman funciones diferentes */
	if($(this).attr("upload-type") == "local")
		loadLocalUploader();
	else
		loadDriveUploader();
	
});

/* Funcion encargada de solicitar la seccion de subida local */
function loadLocalUploader(){
	$.ajax({
		url: localSection,
		method: 'GET'
		/*beforeSend: function(xhr){
			xhr.setRequestHeader("X-CSRFToken", csrf_token);
		}*/
	}).done(function(html){
		$('.upload.section').append(html); 
		/* Una vez cargada la respuesta, se muestra en frontend con una animacion */
		$('.upload.section').addClass('animation enter up');
	});		
}

/* Funcion encargada de solicitar la seccion de subida por Google Drive */
function loadDriveUploader(){}




//Envia la solicitud con en enlace a Google Drive
$('#drive-link').change(function(){
	initial_drive_request(link_analizer_link.replace('999', encodeURIComponent($(this).val())));
	//window.open("{% url 'link_analizer' '999' %}".replace('999', encodeURIComponent($(this).val())), '_blank');
});

/*$('.type-select').change(function(){
	if($(this).val() == "0")
		$('.frame-header[doc-index="' + $(this).attr('doc-index') + '"]').addClass('public-type').removeClass('private-type');
	else
		$('.frame-header[doc-index="' + $(this).attr('doc-index') + '"]').addClass('private-type').removeClass('public-type');
});*/
