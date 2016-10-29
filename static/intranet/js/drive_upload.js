var monthNames = ["Ene.", "Feb.", "Mar.", "Abr.", "May", "Jun.", "Jul.", "Ago.", "Sep.", "Oct.", "No.v", "Dec."];
var bCrumbsCount = 0;
var doc_selected = {};
var crossref_timeout, crossref_busy = false;
var last_cr_query = {};
var real_ids;
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

//Para formatear Bytes a diferentes unidades.
//http://stackoverflow.com/questions/15900485/correct-way-to-convert-size-in-bytes-to-kb-mb-gb-in-javascript
function formatSizeUnits(bytes){
        if      (bytes>=1000000000) {bytes=(bytes/1000000000).toFixed(0)+' GB';}
        else if (bytes>=1000000)    {bytes=(bytes/1000000).toFixed(1)+' MB';}
        else if (bytes>=1000)       {bytes=(bytes/1000).toFixed(0)+' KB';}
        else if (bytes>1)           {bytes=bytes+' bytes';}
        else if (bytes==1)          {bytes=bytes+' byte';}
        else                        {bytes='0 byte';}
        return bytes;
}

//Le da formato a la fecha proporcionada por Google Drive.
function format_date(date){
	var date = new Date(date);
	var day = date.getDate();
	var month = monthNames[date.getMonth()];
	var year = date.getFullYear();
	return formated_date = day + ' ' + month + ' ' + year;
}

$(document).ready(function(){
	// Se define una altura inicial del cuadro con el boton 'mas' para que la animacion se vea
	$('.drive.plus').height($('.drive.plus').height());
})

// Previene que el formulario se envie.
$('.drive.form').submit(function(){
	return false;
});

//Envia la solicitud con en enlace a Google Drive
$('.link').change(function(){
	if($(this).val() != ""){
		sendLink(link_analizer_link.replace('999', encodeURIComponent($(this).val())));
	}
	//window.open("{% url 'link_analizer' '999' %}".replace('999', encodeURIComponent($(this).val())), '_blank');
});

// Cuando el boton 'mas' es presionado, se ocultan y eliminan algunos elementos con una animacion
$('.drive.btn').click(function(){
	$('.erasable').animate({
		top: '-10px',
		height: '0px',
		margin: '0px',
		padding: '0px',
		opacity: '0'
	}, 200, function(){
		$(this).remove();
	});
	getFiles();
});

//Cuando el boton 'enviar' es presionado, se envian las id de los archivos que se subiran al sistema
$('.upload.button.send.first').click(function(){
	sendIds();
});

//Cuando el boton 'enviar' es presionado, se envia la informacion actualizada de los documentos
$('.upload.button.send.second').click(function(){
	sendCompleteInfo();
});


// Envia el link de Google Drive al servidor
function sendLink(url){
	doc_selected = {}
	checkFilesSize();
	showLoadingBar();
	$.ajax({
		url: url,
		method: 'GET'
	}).done(function(response){
		$('.loading').addClass("hidden");
		$('.drive.link').prop("disabled", false);
		console.log(response);
		if(!response['error']){
			$('.message').html("");

			// Si es una carpeta:
			if(response['is_folder']){
				filesHandler(response, -1);
				// Se oculta la interfaz del documento individual
				if(!$('.singlefile').hasClass('hidden'))
					hideElement('.singlefile', false);
				// Se muetra (si es que estaba oculto) la interfaz de carpetas
				$('.drive.plus').css('display', 'block').animate({
					height: ($('.drive.user').height()).toString() + 'px',
				}, 200, function(){
				});
			}
			// Si es un solo documento:
			else{
				// Se trabajan los datos
				$('.singlefile').children('.content').children('.size').html(formatSizeUnits(response['size']));
				$('.singlefile').children('.content').children('.name').html(response['name']);
				$('.singlefile').children('.content').children('.date').html(format_date(response['date']));
				$('.singlefile').children('.thumbnail').children('img').attr('src', response['thumbnail']);
				doc_selected[response['id']] = response['name'];
				checkFilesSize();

				// Se oculta la interfaz de carpetas 
				$('.drive.plus').animate({
					height: '0px',
				}, 200, function(){
					$(this).css('display', 'block');
					// Se muestra el documento individual
					addElement('.singlefile');
				});
			}
			// Se eliminan los elementos innecesarios, los que no seran ocupados cuando se utilizan enlaces
			$('.erasable2').animate({
					top: '-10px',
					height: '0px',
					margin: '0px',
					padding: '0px',
					opacity: '0'
				}, 200, function(){
					$(this).remove();
				});
		}
		else{
			hideLoadingBar();
			$('.message').html(response['message']);
		}
	});
}

// Obtiene los archivos de Google Drive
// Si no se envia una id de carpeta, el servidor responde con la carpeta raiz del usuario
// Si se requieren la carpeta raiz del usuario, llamar a la funcion sin parametros: getFiles()
function getFiles(folderId = "", bcId = (bCrumbsCount+1)){
	showLoadingBar();
	$.ajax({
		url: folder_files_link.replace('999', folderId),
		method: 'GET'
	}).done(function(response){
		console.log(response);
		if(!response['error']){
			// Se llama a la funcion filesHandler para mostrar la lista al usuario
			filesHandler(response, bcId);
		}
		else
			$('.message').html(response['message']);
	});
}

// Se encarga de recibir la lista de archivos de Google drive y las muestra en pantalla, configurando todo lo necesario
// Si no recibe un nombre, no se crea la miga de pan
// bcId representa la id de la nueva miga de pan (o la seleccionada)
function filesHandler(object, bcId){
	var files = object['list'];
	var folderId = object['id'];
	var name = object['title'];
	$('.drive.list.nav').children().remove();
	template = [
			'<tr class="document nav" type="$type" title="$title" id="$id" $style size="$rawsize">',
				'<td class="check"> $checkbox </td>',
				'<td> <i class="fa fa-$icon" aria-hidden="true"></i> $name </td>',
				'<td>$date</td>',
				'<td class="size">$size</td>',
			'</tr>'];
	for(var i = 0; i < files.length; i++){
		code = template.join('');
		if(files[i]['isFolder']){
			code = code.replace(/\$icon/g, 'folder')
						.replace(/\$type/g, 'folder')
						.replace(/\$rawsize/g, '')
						.replace(/\$size/g, '-');
		}
		else{
			code = code.replace(/\$icon/g, 'file-pdf-o')
						.replace(/\$size/g, formatSizeUnits(parseInt(files[i]['fileSize'])))
						.replace(/\$rawsize/g, files[i]['fileSize'])
						.replace(/\$type/g, 'file');
		}

		// Si el archivo esta seleccionado, se pinta de verde
		if(files[i]['id'] in doc_selected){
			code = code.replace('$style', 'style="background-color: rgb(207, 234, 226);"')
						.replace('$checkbox', '<i class="fa fa-check" aria-hidden="true"></i>');
		}
		else
			code = code.replace("$style", "").replace('$checkbox', '');

		code = code.replace(/\$name/g, files[i]['title'])
				.replace(/\$date/g, format_date(files[i]['modifiedDate']))
				.replace(/\$id/g, files[i]['id'])
				.replace(/\$title/g, files[i]['title']);

		$('.drive.list.nav').append(code);
	}

	// Se configuran los escucha
	$('.document.nav').off(); // Se desactivan los anteriores
	$('.document.nav').click(function(){
		// Si es una carpeta, se solicitan sus hijos
		if($(this).attr('type') == 'folder'){
			getFiles($(this).attr('id'))
		}
		else if($(this).attr('type') == 'file'){
			if($(this).attr('id') in doc_selected){
				// Si la id ya existe, se elimina
				removeFromSelected($(this).attr('id'));
			}
			else{
				// Si el tamaño es mayor a 2 megabytes, no se permite la seleccion
				if(parseInt($(this).attr('size')) > 2097152){
					$(this).children('.size').css('background-color', '#f7cacd');
					var $this = $(this);
					setTimeout(function(){
						$this.children('.size').css('background-color', 'transparent');
					},500);
				}
				// Si la id no existe y es menor a 2 mb, se crea
				else{
					addToSelected($(this).attr('id'));
				}
			}
		}
	});
	// Una vez rellenada la pagina con los datos, se realizan unos arreglos a la interfaz
	hideLoadingBar();
	// Mientras el boton + siga vivo:
	if($('.drive.btn').length > 0){
		console.log(" .drive.btn > 0");
		// Se hace desaparecer el boton con una animacion
		$('.drive.btn').animate({
			opacity: '0'
		}, 200, function(){
			// Una vez terminada la animacion se elimina el boton y se expande el cuadro
			console.log("remove plus");
			$(this).remove();
			console.log("remove hidden");
			$('.drive.user').removeClass('hidden');
			adjustBoxHeight();
		});
	}
	else{
		// Si el boton + no existe
		// Se expande el cuadro
		console.log("remove hidden");
		$('.drive.user').removeClass('hidden');
		adjustBoxHeight();
	}
	// Si la id de la miga de pan nueva o seleccionada es menor a la ultima insertada
	if(0 < bcId && bcId < bCrumbsCount){
		// Se remueven las migas de pan superiores a la id actual (o seleccionada)
		removeBreadCrumbs(bcId);
	}
	else if(bcId > bCrumbsCount){
		// Se agrega la miga de pan
		addBreadCrumb(folderId, name);
	}
	else if (bcId < 0){
		removeBreadCrumbs(bcId);
		addBreadCrumb(folderId, name);
	}
	return true;
}

function showLoadingBar(){
	// Se activa la barra de carga
	$('.loading').removeClass("hidden");
	// Se desactiva el campo de texto hasta obtener una respuesta
	$('.drive.link').prop("disabled", true);
}

function hideLoadingBar(){
	// Se desactiva la barra de carga
	$('.loading').addClass("hidden");
	// Se activa el campo de texto (si es que existe)
	$('.drive.link').prop("disabled", false);
}

function addBreadCrumb(folderId, name){
	code = [
		'<div class="crumbs step" bc-id="$id">',
			'<button onclick="getFiles($folderId, $id)">$name</button>',
		'</div>',
	];

	code = code.join(' ').replace(/\$id/g, (++bCrumbsCount).toString()).replace('$folderId', "'" + folderId + "'").replace('$name', name);
	$('.drive.breadcrumbs').append(code);

	$('.crumbs.step[bc-id="' + bCrumbsCount + '"]').animate({
		left: '0px',
		opacity: '1'
	},200);
	console.log("add bc");
}

// Remueve todas las migas de pan que posean una id superior al parametro 'id' de la funcion
// Si recibe -1, se reinician las migas de pan
function removeBreadCrumbs(id){
	for(var i = bCrumbsCount; id < i; i--){
		$('.crumbs.step[bc-id="' + i + '"]').animate({
			left: '-7px',
			opacity: '0'
		},200, function(){
			$(this).remove();
		});
	}
	if(id < 0)
		bCrumbsCount = 0;
	else
		bCrumbsCount = id;
}

// Se encarga de agregar el documento al cuadro de seleccionados y al objecto de documentos
function addToSelected(id){
	var object = $('#' + id + '.document.nav');
	doc_selected[id] = object.attr('title');

	// Se crea el documento en el cuadro de seleccionados
	code = object.wrap('<p/>').parent().html();
	object.unwrap();
	code = $('.drive.list.selected').append(code);
	code.children('#' + id).removeClass('nav').addClass('selected');
	code.children('#' + id).children('.check').html('<i class="fa fa-times-circle" aria-hidden="true"></i>');
	
	// Se pinta el documento de verde en de los directorios de Google Drive
	object.css('background-color', '#cfeae2');
	object.children('.check').append('<i class="fa fa-check" aria-hidden="true"></i>');

	checkFilesSize();

	// Se configura el click
	code.children('#' + id).click(function(){
		removeFromSelected(id);
		});

	adjustSelectedBoxHeight();
}

// Se encarga de eliminar el documento del cuadro de seleccionados y del objeto de documentos
function removeFromSelected(id){
	delete doc_selected[id];

	$('#' + id + '.document.nav').css('background-color', 'transparent');
	$('#' + id + '.document.nav').children('.check').children().remove();

	$('#' + id + '.document.selected').remove();

	adjustSelectedBoxHeight();
	checkFilesSize();

}

function adjustBoxHeight(plus=0){
	console.log("ajustar");
	// Se ajusta el alto del cuadro
	$('.drive.plus').animate({
		height: ($('.drive.user').height() + plus).toString() + 'px'
	}, 200);
}

function adjustSelectedBoxHeight(){
	adjustBoxHeight($('.drive.list.selected').height() - $('.drive.selected.wrapper').height());
	// Se ajusta el alto del cuadro
	$('.drive.selected.wrapper').animate({
		height: $('.drive.list.selected').height().toString() + 'px'
	}, 200);
}

// Envia las id de los documentos seleccionados al servidor
function sendIds(){
	// Muestra la barra de carga
	showLoadingBar();
	// Elimina la vista actual
	hideElement('.upload.drive.plus', true);
	hideElement('.singlefile', true);
	var ids = [];
	for (var key in doc_selected) {
	    if (doc_selected.hasOwnProperty(key)) {
	        ids.push(key);
	    }
	}
	ids = ids.join('+');
	url = download_drive_link.replace('999', ids);

	// Solicitud al servidor
	$.ajax({
		url: url,
		method: 'GET'
	}).done(function(response){
		handleDocuments(response['files']);
		hideLoadingBar();
		real_ids = response['real_ids'].join(',');
		extract_content(real_ids);
	});
	console.log("Drive ids: " + ids);
}

// Solicita la extraccion del contenido y el resumen del texto explicitamente
function extract_content(ids){
	var form = new FormData();
	form.append('ids', real_ids);
	$	.ajax({
		url: extract_link,
		method: 'POST',
		data: form,  
		beforeSend: function(xhr){
			xhr.setRequestHeader("X-CSRFToken", csrf_token);
		},
		processData: false,
		contentType: false,
	}).done(function(response){
		if(!response['error']){
			abs = response['abstracts'];
			console.log("Resumenes:");
			console.log(abs);
			for (var i=0; i < abs.length; i++){
				var field = $('textarea[name="abstract' + abs[i]['id'] + '"]');
				field.prop('disabled', false).val(abs[i]['abstract']);
				field.siblings('i').remove();
			}
			// Se activa el boton de enviar
			$('.upload.button.send.second').prop('disabled', false).removeClass('disabled');

			// Se actualiza el tamaño de los textarea
			$('textarea').each(function(){
				autosize.update($(this));
			})
		}
	});
}


function sendCompleteInfo(){
	var form = new FormData($('#form')[0]);
	form.append('id', real_ids);
	var form_status = $('#form')[0].checkValidity();
	console.log(form_status);

	//Si no esta completo el formulario, se resaltan los campos faltantes
	if(!form_status)
		checkEmptyFields();
	else{
		$.ajax({
			url: upload_link,
			method: 'POST',
			data: form,
			processData: false,
			contentType: false,
		}).done(function(response){
			console.log(response);
			hideElement('.upload.section', true);
			addElement("#success-icon");
			setTimeout(function(){window.location.href = upload_link;}, 1000);
		});
	}

}


/***********************************************/

function handleDocuments(documents){
	console.log(documents);
	for(var i = 0; i < documents.length; i++){
		addDocument(documents[i]);
	}
	/* Se evita la accion del boton Enter */
	$('#form').keydown(function(e){
		if(event.keyCode == 13) {
		  event.preventDefault();
		  return false;
		}
	});
	// Se activan los textarea auto ajustables
	autosize($('textarea'));

	// Se activa crossref
	enableCrossref();
	addElement('.upload.files');
}


/* Muestra en pantalla el formulario del documento */
function addDocument(document){
	/* Plantilla para el idioma Espanol */
	if (current_lang == 'es'){
		var code = ['<div class="s1 c10 intranet box upload file wrapper animation enter down" doc-index="$index">',
						'<div class="subwrapper">',
							'<div class="c3">',
								'<img src="$thumbnail">',
							'</div>',
							'<div class="c9">',
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
								'<div class="c12 upload file field abstract">',
									'<div class="c3">',
										'<strong>Resumen:</strong> ',
									'</div>',
									'<div class="c9">',
										'<i class="fa fa-circle-o-notch fa-spin fa-3x fa-fw" doc-index="$index"></i>',
										'<textarea  name="abstract$index" disabled required></textarea>',
									'</div>',
								'</div>',
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
				'</div>',
				'</br>']
	}
	/* Se reemplazan las etiquetas por los Metadatos extraidos */
	code = code.join('')
		.replace(/\$index/g, document['id'])
		.replace(/\$title/g, document['title'] ? document['title']:'')
		.replace(/\$author/g, document['author'] ? document['author']:'')
		.replace(/\$thumbnail/g, document['thumbnail'] ? static_link.replace('999', document['thumbnail']):'')
		.replace(/\$date/g, document['date'] ? document['date']:'');
	/* Se agrega al frontend */
	$('#form').append(code);
	/* Se realiza la primera consulta a crossref */
	last_cr_query[document['id']] = document['title'];
	crossref_query(document['title'] ? document['title']:'', document['id']);

	
}

function crossref_query(query, doc_id){
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
			toggleCrossref(doc_id);
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
		console.log(last_cr_query[doc_id]);
		if(last_cr_query[doc_id].localeCompare(query) != 0){
			crossref_query(last_cr_query[doc_id], [doc_id]);
		}
		else
			crossref_busy = false;

	});		
}

// Activa los eventos de Crossref
function enableCrossref(){

	$('.field[field-name="title"]').off();
	$('.field[field-name="title"]').on('input', function(){
		last_cr_query[$(this).attr('doc-index')] = $(this).val();
		if(!crossref_busy){
			crossref_busy = true;

			toggleCrossref($(this).attr('doc-index'));
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

// Se encarga de habilitar o deshabilitar el boton de enviar
function checkFilesSize(){
	if(Object.size(doc_selected) == 0){
		$('.upload.button.send.first').prop('disabled', true).addClass('disabled');				
	}
	else{
		$('.upload.button.send.first').prop('disabled', false).removeClass('disabled');	
	}
}
