var files = {}; /* Objeto que almacena los archivos que el usuario ha subido */
var key_count = 0; /* Contador que define la posicion de cada archivo que es insertado en el objeto 'files' */
(function($){
	/* Resetea el input de archivos */
	$.fn.resetInput = function(){
		this.wrap('<form>').closest('form').get(0).reset();
		this.unwrap();
	};
})(jQuery);

/* Escucha a los botones 'Agregar Documentos' y 'Enviar Documentos' */
$('.upload.button').click(function(){
	if($(this).hasClass("add"))
		$('#input-files').click();
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
			if(Object.size(files) > 0)
				$('#local-submit').prop('disabled', false).removeClass('disabled');
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

function addDocument(key_count, filename, object){
	/* Plantilla para el idioma Espanol */
	if (current_lang == 'es'){
		var code = ['<div class="document-frame animation-down" doc-index="$index">',
					'<div class="frame-header">',
						'<h5 class="frame-title">$filename</h5>',
						'<select class="type-select field" name="type$index" required>',
							'<option value="" disabled selected>Selecciona privacidad</option>',
							'<option value="0">Público</option>',
							'<option value="1">Privado</option>',
						'</select>',
						'<button class="close-btn"  doc-index="$index"><i class="fa fa-times" aria-hidden="true"></i></button>',
						'<div class="clear"></div>',
					'</div>',
					'<ul class="frame-data">',
						'<li><strong>Titulo:</strong> <input type="text" class="field" value="$title" field-name="title" doc-id="$index" name="title$index" placeholder="Ej: Tesis de microbiologia" autocomplete="off" required><div class="crossref-wrapper hidden" doc-id="$index"><div class="loader hidden" doc-id="$index><img src="' + spinner_link + '"></div><div class="crossref-list-wrapper"><ul class="crossref-list" doc-id="$index"></ul></div></div></li>',
						'<li><strong>Autor:</strong> <input type="text" class="field" value="$author" name="author$index" placeholder="Ej: Juan Perez" required></li>',
						'<li><strong>Fecha de creación:</strong> <input type="text" class="field" value="$date" name="date$index" placeholder="Ej: 2016" required></li>',
						'<li><strong>ISSN:</strong><input type="text" class="field" name="issn$index" placeholder="No requerido"></li>',
						'<li><strong>DOI:</strong><input type="text" class="field" name="doi$index" placeholder="No requerido"></li>',
						'<li><strong>URL:</strong><input type="text" class="field" name="url$index" placeholder="ej: http://dx.doi.org/10.1109/ms.2006.34"></li>',
						'<li><strong>Paginas:</strong><input type="text" class="field" name="pages$index" placeholder="No requerido"></li>',
						'<li><strong>Area:</strong>',
							'<select name="category$index" class="field form-select" required>',
								'<option value="" disabled selected>Selecciona una categoria</option>',
								'<option value="1">Microbiología Molecular</option>',
								'<option value="2">Biotecnología Ambiental</option>',
								'<option value="3">Bionanotecnología</option>',
								'<option value="4">Genómica Funcional y Proteómica</option>',
								'<option value="5">Síntesis de compuestos bioactivos y de interés biotecnológico</option>',
								'<option value="6">Biorremediación de Ambientes Contaminados</option>',
							'</select>',
						'</li>',
					'</ul>',
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
						'<li><strong>' + gettext('Titulo') + ':</strong> <input type="text" class="field" value="$title" field-name="title" name="title$index" doc-id="$index" placeholder="' + gettext('Ej: Tesis de microbiologia') + '" autocomplete="off" required><div class="crossref-wrapper hidden" doc-id="$index"><div class="loader hidden" doc-id="$index><img src="' + spinner_link + '"></div><div class="crossref-list-wrapper"><ul class="crossref-list" doc-id="$index"></ul></div></div></li>',
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
	code = code.join('').replace(/\$index/g, key_count).replace(/\$filename/g, filename).replace(/\$title/g, object['Title'] ? object['Title']:'').replace(/\$author/g, object['Author'] ? object['Author']:'').replace(/\$date/g, object['CreationDate'] ? (object['CreationDate'].substr(2, 4) + '-' + object['CreationDate'].substr(6, 2) + '-' + object['CreationDate'].substr(8, 2) ):'');
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
	$('.close-btn').off();
	$('.close-btn').click(function(){
		$('.document-frame[doc-index="' + $(this).attr('doc-index') + '"]').remove();
		delete files[$(this).attr('doc-index')];
		if(Object.size(files) == 0)
			$('#local-submit').prop('disabled', true).addClass('disabled');
	});
	$('.type-select').off();
	$('.type-select').change(function(){
				if($(this).val() == "0")
					$(this).closest('.frame-header').addClass('public-type').removeClass('private-type');
				else
					$(this).closest('.frame-header').addClass('private-type').removeClass('public-type');
	});
	$('.field[field-name="title"]').off();
	$('.field[field-name="title"]').on('input', function(){
		if(!crossref_busy){
			crossref_busy = true;
			$('.loader[doc-id="' + $(this).attr('doc-id') +'"]').removeClass('hidden');
			$('.crossref-wrapper[doc-id="' + $(this).attr('doc-id') +'"]').removeClass('hidden');
			var $this = $(this)
			crossref_timeout = setTimeout(function(){
				if($this.val() == ''){
					crossref_busy = false;
					$('.crossref-wrapper[doc-id="' + $this.attr('doc-id') +'"]').removeClass('hidden');
					$('.loader[doc-id="' + $this.attr('doc-id') +'"]').addClass('hidden');
				}
				else{
					console.log($this.attr('doc-id'));
					crossref_query($this.val(), $this.attr('doc-id'), false);
				}
			}, 2000);
		}
	});
	$('.field[field-name="title"]').focus(function(e){
		$('.crossref-wrapper[doc-id="' + $(this).attr('doc-id') +'"]').removeClass('hidden');
	});
	$('.field[field-name="title"]').keyup(function(e){
		if(e.which == 27 || e.which == 13){
			$('.crossref-wrapper[doc-id="' + $(this).attr('doc-id') +'"]').addClass('hidden');
			$('.loader[doc-id="' + $(this).attr('doc-id') +'"]').addClass('hidden');
		}
	});
	$('.field[field-name="title"]').focusout(function(e){
		var $this = $(this)
		setTimeout(function(){
			$('.crossref-wrapper[doc-id="' + $this.attr('doc-id') +'"]').addClass('hidden');
			$('.loader[doc-id="' + $this.attr('doc-id') +'"]').addClass('hidden');			
		}, 100);
	});

}

function crossref_query(query, doc_id, is_drive){
	$.ajax({
		url: crossref_link.replace('999', query),
		method: 'GET'
		/*beforeSend: function(xhr){
			xhr.setRequestHeader("X-CSRFToken", csrf_token);
		}*/
	}).done(function(response){
		if(!response['error']) {
			$('.crossref-list[doc-id="' + doc_id +'"]').children().remove();
			$('.crossref-list[doc-id="' + doc_id +'"]').append(response);
			$('.loader').addClass('hidden');
			crossref_busy = false;
			$('.crossref-row').off();
			$('.crossref-row').click(function(e){
				if(is_drive)
					var doc = $(this).closest('ul').attr('doc-id').replace('drive', '');
				else
					var doc = $(this).closest('ul').attr('doc-id');
				console.log('.' + cls + '[name="title' + doc + '"]');
				$('.' + cls + '[name="title' + doc + '"]').val($(this).attr('title'));
				$('.' + cls + '[name="author' + doc + '"]').val($(this).attr('author'));
				$('.' + cls + '[name="date' + doc + '"]').val($(this).attr('date'));
				$('.' + cls + '[name="issn' + doc + '"]').val($(this).attr('issn'));
				$('.' + cls + '[name="doi' + doc + '"]').val($(this).attr('doi'));
				$('.' + cls + '[name="url' + doc + '"]').val($(this).attr('url'));
				$('.' + cls + '[name="pages' + doc + '"]').val($(this).attr('pages'));
			});
		}
	});		
	var xhr = new XMLHttpRequest();
	xhr.open('GET', crossref_link.replace('999', query) , true);
	xhr.onload = function(){
		if (xhr.readyState == 4 && xhr.status == 200 && !response['error']) {
				$('.crossref-list[doc-id="' + doc_id +'"]').children().remove();
				$('.crossref-list[doc-id="' + doc_id +'"]').append(response);
				$('.loader').addClass('hidden');
				crossref_busy = false;
				$('.crossref-row').off();
				$('.crossref-row').click(function(e){
					if(is_drive)
						var doc = $(this).closest('ul').attr('doc-id').replace('drive', '');
					else
						var doc = $(this).closest('ul').attr('doc-id');
					console.log('.' + cls + '[name="title' + doc + '"]');
					$('.' + cls + '[name="title' + doc + '"]').val($(this).attr('title'));
					$('.' + cls + '[name="author' + doc + '"]').val($(this).attr('author'));
					$('.' + cls + '[name="date' + doc + '"]').val($(this).attr('date'));
					$('.' + cls + '[name="issn' + doc + '"]').val($(this).attr('issn'));
					$('.' + cls + '[name="doi' + doc + '"]').val($(this).attr('doi'));
					$('.' + cls + '[name="url' + doc + '"]').val($(this).attr('url'));
					$('.' + cls + '[name="pages' + doc + '"]').val($(this).attr('pages'));
				});
			}
	}
	xhr.send(null);
}