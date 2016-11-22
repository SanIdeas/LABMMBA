//PopupCenter('http://127.0.0.1:8000{% url 'get_credentials' %}', 'Iniciar sesion en Google Drive', 650, 700)
var state = ''; //Define el estado. Si es 'single' significa que se esta mostrando un solo archivo gdrive. Si es 'multi' significa que se estan mostrando multiples archivos gdrive. si es 'confirm' significa que se esta en la ventana de confirmacion.
/* Escucha la los click sobre las opciones iniciales */
$.ajaxPrefilter(function( options, originalOptions, jqXHR ) {
    options.async = true;
});
$('.upload.method').click(function(){
	
	/* Dependiendo del tipo del boton, se llaman funciones diferentes */
	if($(this).attr("upload-type") == "local"){
		loadLocalUploader();
	}
	else{
		if(google_status)
			loadDriveUploader();
		else{
			googleAuthentication();
			return;
		}
	}
	/* Una vez hecho el click, las opciones se desvanecen hacia arriba y son eliminadas a los 200 ms */
	hideElement('.upload.selector', true);
});

/* Funcion encargada de solicitar la seccion de subida local */
function loadLocalUploader(){
	$.ajax({
		url: localSection,
		method: 'GET'
	}).done(function(html){
		$('.upload.section').append(html); 
		/* Una vez cargada la respuesta, se muestra en frontend con una animacion */
		$('.upload.section').addClass('animation enter up');
	});		
}

/* Funcion encargada de solicitar la seccion de subida por Google Drive */
function loadDriveUploader(){
	$.ajax({
		url: driveSection,
		method: 'GET'
	}).done(function(html){
		$('.upload.section').append(html); 
		/* Una vez cargada la respuesta, se muestra en frontend con una animacion */
		$('.upload.section').addClass('animation enter up');
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
		     $.fancybox(
		     	$('#enablePopupModal').html());
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