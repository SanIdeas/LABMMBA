var files = {}; /* Objeto que almacena los archivos que el usuario ha subido */
var key_count = 0; /* Contador que define la posicion de cada archivo que es insertado en el objeto 'files' */
var form_template;
// Realiza la primera y unica solicitud con la plantilla de los formularios
$.fancybox.showLoading();
$.ajax({
	url: template_url,
	method: "GET"
}).done(function(response){
	form_template = response;
	$.fancybox.hideLoading();
});

(function($){
	/* Resetea el input de archivos */
	$.fn.resetInput = function(){
		this.wrap('<form>').closest('form').get(0).reset();
		this.unwrap();
	};
})(jQuery);

Object.size = function(obj) {
    var size = 0, key;
    for (key in obj) {
        if (obj.hasOwnProperty(key)) size++;
    }
    return size;
};

/* Escucha a los botones 'Agregar Documentos' y 'Enviar Documentos' */
$('.upload.button').click(function(){
	if($(this).hasClass("add"))
		$('#input-files').click();
	if($(this).hasClass("send"))
		sendDocuments();
});

/* Cuando el estado del input de archivos cambie, es decir, cuando contenga nuevos archivos */
$('#input-files').change(function(){
	filesHandler();
	$(this).resetInput();
});

/* Funcion que se encarga de agregar los nuevos archivos al objeto 'files' */
function filesHandler(){
	/* Se obtienen los archivos del input */
	var new_files = document.getElementById('input-files').files;

	/* Se crea una lista para almacenar los nombres de los archivos ya existentes */
	var files_names = [];
	for(var i = 0; i < files.length; i++){
		files_names.push(files[i].name);
	}

	/* Luego se comparan los nombres existentes con los nuevos. El objetivo es evitar archivos duplicados */
	for (var i = 0; i < new_files.length; i++){
		var exists = false
		for(var key in files){
			if(files.hasOwnProperty(key)){
				/* Si el archivo ya existe se cambia el estado */
				if(files[key].name == new_files[i].name){
					exists = true;
				}
			}
		}

		/* Solo e almacena en la lista 'files' si el archivo no existe (exists == false) */
		if(!exists){
			files[key_count] = new_files[i];
			getMeta(key_count, new_files[i]);
			key_count++;

			 /* Si la cantidad de archivos es mayor a 0, se habilita el boton para enviar */

			checkFilesSize();
		}
	}
}

/* Funcion que se encarga de extraer los Metadatos de los archivos */
function getMeta(key_count, file){
	var reader  = new FileReader();
				
	reader.addEventListener("load", function () {
		PDFJS.getDocument(convertDataURIToBinary(reader.result)).then(function (pdfDoc_) {
		    pdfDoc = pdfDoc_;   
		    pdfDoc.getMetadata().then(function(stuff) {

		        /* Una vez extraidos, se llama a la funcion 'addDocument' para generar el formulario (frontend) */
		        addDocument(key_count, file.name, stuff['info']);

		    }).catch(function(err) {
		       console.log('Error getting meta data');
		       console.log(err);
		    });
		}).catch(function(err) {
		    console.log('Error getting PDF from ' + url);
		    console.log(err);
		});
	}, false);

	reader.readAsDataURL(file);
}

/* Muestra en pantalla el formulario del documento */
function addDocument(key_count, filename, object){
	var code = form_template;
	/* Se reemplazan las etiquetas por los Metadatos extraidos */
	code = code
		.replace(/\$index/g, key_count)
		.replace(/\$filename/g, filename)
		.replace(/\$title/g, object['Title'] ? object['Title']:'')
		.replace(/\$author/g, object['Author'] ? object['Author']:'')
		.replace(/\$date/g, object['CreationDate'] ? (object['CreationDate'].substr(8, 2) + '-' + object['CreationDate'].substr(6, 2) + '-' + object['CreationDate'].substr(2, 4) ):'');
	/* Se agrega al frontend */
	$('#form').append(code);
	/* Se realiza la primera consulta a crossref */
	crossref_query(object['Title'] ? object['Title']:'', key_count, false);

	/* Se evita la accion del boton Enter */
	$('#form').off();
	$('#form').keydown(function(e){
		if(event.keyCode == 13) {
		  event.preventDefault();
		  return false;
		}
	});

	/* Se configura la accion del boton Cruz */
	$('.upload.delete').off();
	$('.upload.delete').click(function(e){
		e.preventDefault();
		hideElement('.file[doc-index="' + $(this).attr('doc-index') + '"]', true);
		console.log('.file[doc-index="' + $(this).attr('doc-index') + '"]');
		delete files[$(this).attr('doc-index')];
		checkFilesSize();
	});

	// Se activa crossref
	enableCrossref("class");

}

// Se encarga de mostrar o eliminar el mensaje "no has agregado documentos"
function checkFilesSize(){
	if(Object.size(files) == 0){
		addElement(".upload.empty");
		$('.upload.button.send').prop('disabled', true);				
	}
	else{
		hideElement(".upload.empty", false);
		$('.upload.button.send').prop('disabled', false);	
	}
}

function sendDocuments(){
	$('.upload.button.send, .upload.button.add').prop('disabled', true);	
	var form = new FormData($('#form')[0]);
	console.log(Object.keys(files));

	// Se almacenan las id
	form.append('user_side_ids', Object.keys(files).join(','));
	for(var id in files){
		if (files.hasOwnProperty(id)){
			form.append('document'+id.toString(), files[id]);
		}
	}
	var form_status = $('#form')[0].checkValidity();

	//Si no esta completo el formulario, se resaltan los campos faltantes
	if(!form_status){
		checkEmptyFields();
		$('.upload.button.send, .upload.button.add').prop('disabled', false);
	}

	//De lo contrario, se envia la solicitud
	else{
		// Mientras se realiza la subida, se oculta el formulario
		hideElement(".upload.section", false);//false: no se elimina el elemento
		//Se muestra la animacion de loading
		addElement(".cssload-loader-wrapper");
		$.ajax({
			url: upload_link,
			type: 'POST',
			data: form,
			processData: false,
			contentType: false
		}).done(function(response){
			console.log(response['error']);
			if(!response['error']) {
				hideElement(".cssload-loader-wrapper", true);
				addElement("#success-icon");
				setTimeout(function(){window.location.href = upload_link;}, 1000);
			}
			else{
				//hubo un error, se muestra el mensaje y el formulario
				$('.upload.message').html("").append(response['message']);
				addElement(".upload.section");
				hideElement(".cssload-loader-wrapper", false);
				$('.upload.button.send, .upload.button.add').prop('disabled', false);
			}		
		}).error(function(xhr, status, error){
				$('.upload.message').html("").append(error);
				addElement(".upload.section");
				hideElement(".cssload-loader-wrapper", false);
				$('.upload.button.send, .upload.button.add').prop('disabled', false);
		});
	}
}

function checkEmptyFields(){
	$(".field").each(function(i, field){
		if (($(field).val() == null || $(field).val() == '') && $(field).prop('required') == true){
			$(field).addClass("required");
			$(field).on('input', function(){
				if($(this).hasClass('required'))
					$(this).removeClass('required');
				$(this).off();
			});	
		}
	});
}