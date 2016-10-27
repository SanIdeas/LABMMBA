var files = {}; /* Objeto que almacena los archivos que el usuario ha subido */
var key_count = 0; /* Contador que define la posicion de cada archivo que es insertado en el objeto 'files' */
var crossref_timeout, crossref_busy = false;
var last_cr_query = "";
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
	/* Plantilla para el idioma Espanol */
	if (current_lang == 'es'){
		var code = ['<div class="s1 c10 intranet box upload file wrapper animation enter down" doc-index="$index">',
					'<div class="c12 upload file head">',
						'<button class="upload delete" doc-index="$index"><i class="fa fa-times" aria-hidden="true"></i></button>',
					'</div>',
					'<div class="c12 upload file filename">',
						'<h3>$filename</h3>',
					'</div>',
					'<div class="c12 upload file field">',
						'<div class="c3">',
							'<strong>Titulo:</strong>' ,
						'</div>',
						'<div class="c9">',
							'<div class="upload crossrefWrapper">',
								'<input type="text" class="field text" value="$title" field-name="title" doc-index="$index" name="title$index" placeholder="Ej: Tesis de microbiologia" autocomplete="off" required>',
								//crossref
								'<div class="upload crossref hidden" doc-index="$index">',
									'<div class="upload records">',
										'<div class="upload records topbar">',
											// Cabecera del cuadro
											'<i class="upload fa fa-check" doc-index="$index" aria-hidden="true"></i>',
											'<i class="upload loader fa fa-circle-o-notch fa-spin fa-3x fa-fw" doc-index="$index"></i>',
											'<button doc-index="$index"><i class="fa fa-times" aria-hidden="true"></i></button>',
										'</div>',
										'<div class="upload records list">',
											'<ul class="upload records root" doc-index="$index">',
											//Lista de sugerencias
											'</ul>',
										'</div>',
									'</div>',
								'</div>',
							'</div>',

						'</div>',
					'</div>',
					'<div class="c12 upload file field">',
						'<div class="c3">',
							'<strong>Autor:</strong>' ,
						'</div>',
						'<div class="c9">',
							'<input type="text" class="field text" value="$author" name="author$index" placeholder="Ej: Juan Perez" required>',
						'</div>',
					'</div>',
					'<div class="c12 upload file field">',
						'<div class="c3">',
							'<strong>Fecha de creacion:</strong>',
						'</div>',
						'<div class="c9">',
							'<input type="date" class="field text" value="$date" name="date$index" required>',
						'</div>',
					'</div>',
					'<div class="c12 upload file field">',
						'<div class="c3">',
							'<strong>DOI:</strong>', 
						'</div>',
						'<div class="c9">',
							'<input type="text" class="field text" name="doi$index" placeholder="Ej: 10.1109/ms.2006.34">',
						'</div>',
					'</div>',
					'<div class="c12 upload file field">',
						'<div class="c3">',
							'<strong>ISSN:</strong> ',
						'</div>',
						'<div class="c9">',
							'<input type="text" class="field text" name="issn$index" placeholder="No requerido">',
						'</div>',
					'</div>',
					'<div class="c12 upload file field">',
						'<div class="c3">',
							'<strong>Páginas:</strong> ',
						'</div>',
						'<div class="c9">',
							'<input type="text" class="field text" name="pages$index" placeholder="No requerido">',
						'</div>',
					'</div>',
					'<div class="c12 upload file field">',
						'<div class="c3">',
							'<strong>Area:</strong> ',
						'</div>',
						'<div class="c9">',
							'<select name="category$index" class="field" required>',
								'<option value="" disabled selected>Selecciona una categoria</option>',
								'<option value="1">Microbiología Molecular</option>',
								'<option value="2">Biotecnología Ambiental</option>',
								'<option value="3">Bionanotecnología</option>',
								'<option value="4">Genómica Funcional y Proteómica</option>',
								'<option value="5">Síntesis de compuestos bioactivos y de interés biotecnológico</option>',
								'<option value="6">Biorremediación de Ambientes Contaminados</option>',
							'</select>',
						'</div>',
					'</div>',
					'<div class="c12 upload file field">',
						'<div class="c3">',
							'<strong>Privacidad:</strong> ',
						'</div>',
						'<div class="c9">',
							'<select class="type-select field" name="type$index" required>',
									'<option value="" disabled selected>Selecciona privacidad</option>',
									'<option value="0">Público</option>',
									'<option value="1">Privado</option>',
								'</select>',
						'</div>',
					'</div>',
				'</div>']
	}

	/* Plantilla para el idioma Ingles */ 
	else if (current_lang == 'en'){
		var code = ['<div class="document-frame animation-down" doc-index="$index">',
					'<div class="frame-header">',
						'<h5 class="frame-title">$filename</h5>',
						'<select class="type-select field" name="type$index" required>',
							'<option value="" disabled selected>' + gettext('Selecciona privacidad') + '</option>',
							'<option value="0">' + gettext('Público') + '</option>',
							'<option value="1">' + gettext('Privado') + '</option>',
						'</select>',
						'<button class="close-btn"  doc-index="$index"><i class="fa fa-times" aria-hidden="true"></i></button>',
						'<div class="clear"></div>',
					'</div>',
					'<ul class="frame-data">',
						'<li><strong>' + gettext('Titulo') + ':</strong> <input type="text" class="field" value="$title" field-name="title" name="title$index" doc-index="$index" placeholder="' + gettext('Ej: Tesis de microbiologia') + '" autocomplete="off" required><div class="crossref-wrapper hidden" doc-index="$index"><div class="loader hidden" doc-index="$index><img src="' + spinner_link + '"></div><div class="crossref-list-wrapper"><ul class="crossref-list" doc-index="$index"></ul></div></div></li>',
						'<li><strong>' + gettext('Autor') + ':</strong> <input type="text" class="field" value="$author" name="author$index" placeholder="' + gettext('Ej: Juan Perez') + '" required></li>',
						'<li><strong>' + gettext('Fecha de creación') + ':</strong> <input type="text" class="field" value="$date" name="date$index" placeholder="' + gettext('Ej: 2016-12-30') + '" required></li>',
						'<li><strong>ISSN:</strong><input type="text" class="field" name="issn$index" placeholder="No requerido"></li>',
						'<li><strong>DOI:</strong><input type="text" class="field" name="doi$index" placeholder="No requerido"></li>',
						'<li><strong>URL:</strong><input type="text" class="field" name="url$index" placeholder="ej: http://dx.doi.org/10.1109/ms.2006.34"></li>',
						'<li><strong>Paginas:</strong><input type="text" class="field" name="pages$index" placeholder="No requerido"></li>',
						'<li><strong>' + gettext('Area') + ':</strong>',
							'<select name="category$index" class="field form-select" required>',
								'<option value="" disabled selected>' + gettext('Selecciona una categoria') + '</option>',
								'<option value="1">' + gettext('Microbiología Molecular') + '</option>',
								'<option value="2">' + gettext('Biotecnología Ambiental') + '</option>',
								'<option value="3">' + gettext('Bionanotecnología') + '</option>',
								'<option value="4">' + gettext('Genómica Funcional y Proteómica') + '</option>',
								'<option value="5">' + gettext('Síntesis de compuestos bioactivos y de interés biotecnológico') + '</option>',
								'<option value="6">' + gettext('Biorremediación de Ambientes Contaminados') + '</option>',
							'</select>',
						'</li>',
					'</ul>',
				'</div>']
	}
	/* Se reemplazan las etiquetas por los Metadatos extraidos */
	code = code.join('')
		.replace(/\$index/g, key_count)
		.replace(/\$filename/g, filename)
		.replace(/\$title/g, object['Title'] ? object['Title']:'')
		.replace(/\$author/g, object['Author'] ? object['Author']:'')
		.replace(/\$date/g, object['CreationDate'] ? (object['CreationDate'].substr(2, 4) + '-' + object['CreationDate'].substr(6, 2) + '-' + object['CreationDate'].substr(8, 2) ):'');
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
		if(Object.size(files) == 0)
			$('#local-submit').prop('disabled', true).addClass('disabled');
	});

	// Se activa crossref
	enableCrossref("class");

}

function crossref_query(query, doc_id, open = true){
	// Se muestra el icono que gira y se remueve el check
	$('.upload.fa-check[doc-index="' + doc_id +'"]').addClass('hidden');
	$('.upload.loader[doc-index="' + doc_id +'"]').removeClass('hidden');

	$.ajax({
		url: crossref_link.replace('999', query),
		method: 'GET'
		/*beforeSend: function(xhr){
			xhr.setRequestHeader("X-CSRFToken", csrf_token);
		}*/
	}).done(function(response){
		if(!response['error']) {
			toggleCrossref(doc_id, open);
			$('.upload.records.root[doc-index="' + doc_id +'"]').children().remove();
			$('.upload.records.root[doc-index="' + doc_id +'"]').append(response);

			$('.crossref-row').off();
			$('.crossref-row').click(function(e){
				//Cuando se hace click sobre una sugerencia, se rellenan los datos
				var index = $(this).closest('ul').attr('doc-index');
				console.log('.field[name="title' + index + '"]');
				$('.field[name="title' + index + '"]').val($(this).attr('title'));
				$('.field[name="author' + index + '"]').val($(this).attr('author'));
				$('.field[name="date' + index + '"]').val($(this).attr('date'));
				$('.field[name="issn' + index + '"]').val($(this).attr('issn'));
				$('.field[name="doi' + index + '"]').val($(this).attr('doi'));
				$('.field[name="url' + index + '"]').val($(this).attr('url'));
				$('.field[name="pages' + index + '"]').val($(this).attr('pages'));
			});
			// Se meuestra el icono check
			$('.upload.fa-check[doc-index="' + doc_id +'"]').removeClass('hidden');
		}
		$('.upload.loader[doc-index="' + doc_id +'"]').addClass('hidden');
		//Comprueba si hubo un cambio en el campo de texto desde que mando la solicitud
		if(last_cr_query.localeCompare(query) != 0){
			console.log("entra");
			crossref_query(last_cr_query, doc_id);
		}
		else
			crossref_busy = false;

	});		
}

function enableCrossref(){

	$('.field[field-name="title"]').off();
	$('.field[field-name="title"]').on('input', function(){
		last_cr_query = $(this).val();
		if(!crossref_busy){
			crossref_busy = true;

			toggleCrossref($(this).attr('doc-index'), true);
			var $this = $(this)
			crossref_timeout = setTimeout(function(){
				if($this.val() == ''){
					crossref_busy = false;
				}
				else{
					console.log($this.val());
					crossref_query($this.val(), $this.attr('doc-index'));
				}
			}, 500);
		}
	});

	//Al hacer click sobre el campo de texto, si hay textos de sugerencia, se muestran.
	$('.field[field-name="title"]').focus(function(e){
		var cr = $('.crossref[doc-index="' + $(this).attr('doc-index') +'"]');
		console.log(cr.find('.upload.records.list').find('li').length);
		if(cr.find('.upload.records.list').find('li').length > 0)
			toggleCrossref($(this).attr('doc-index'), true, false);
	});
	
	// Cuando se presiona esc o enter, se esconde el cuadro.
	$('.field[field-name="title"]').keyup(function(e){
		if(e.which == 27 || e.which == 13){
			toggleCrossref($(this).attr('doc-index'));
		}
	});


	//Cuando se sale el cursor del campo de texto, se esconde el cuadro
	$('.field[field-name="title"]').focusout(function(e){
		var $this = $(this)
		setTimeout(function(){
			toggleCrossref($this.attr('doc-index'));			
		}, 100);
	});
}

// Se encarga de mostrar o eliminar el mensaje "no has agregado documentos"
function checkFilesSize(){
	if(Object.size(files) == 0){
		addElement(".upload.empty");
		$('.upload.button.send').prop('disabled', true).addClass('disabled');				
	}
	else{
		hideElement(".upload.empty", false);
		$('.upload.button.send').prop('disabled', false).removeClass('disabled');	
	}
}

function sendDocuments(){
	var form = new FormData($('#form')[0]);
	console.log(Object.keys(files));
	form.append('local_ids', Object.keys(files).join(','));
	for(var id in files){
		if (files.hasOwnProperty(id)){
			form.append('document'+id.toString(), files[id]);
		}
	}
	var form_status = $('#form')[0].checkValidity();
	console.log(form_status);

	//Si no esta completo el formulario, se resaltan los campos faltantes
	if(!form_status)
		checkEmptyFields();

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
			console.log(response);
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
			}		
		}).error(function(xhr, status, error){
				$('.upload.message').html("").append(error);
				addElement(".upload.section");
				hideElement(".cssload-loader-wrapper", false);
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