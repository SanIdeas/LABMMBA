var monthNames = ["Ene.", "Feb.", "Mar.", "Abr.", "May.", "Jun.", "Jul.", "Ago.", "Sep.", "Oct.", "Nov.", "Dec."];





NodeList.prototype.remove = HTMLCollection.prototype.remove = function() {
    for(var i = this.length - 1; i >= 0; i--) {
        if(this[i] && this[i].parentElement) {
            this[i].parentElement.removeChild(this[i]);
        }
    }
}



function convertDataURIToBinary(dataURI) {
	var BASE64_MARKER = ';base64,';
	var base64Index = dataURI.indexOf(BASE64_MARKER) + BASE64_MARKER.length;
	var base64 = dataURI.substring(base64Index);
	var raw = window.atob(base64);
	var rawLength = raw.length;
	var array = new Uint8Array(new ArrayBuffer(rawLength));

	for(var i = 0; i < rawLength; i++) {
	array[i] = raw.charCodeAt(i);
	}
	return array;
}

function replaceValues(object){

	if(object['Author'].length > 0){
		var input = $('#author');

		input.val(object['Author']);
		input.prop('readOnly', true);
		input.addClass('read-only');
	}
	else{
		input.val('');
		input.prop('readOnly', false);
		input.removeClass('read-only');
	}
	if(object['Title'].length > 0){
		var input = $('#title');

		input.val(object['Title']);
		input.prop('readOnly', true);
		input.addClass('read-only');
	}
	else{
		input.val('');
		input.prop('readOnly', false);
		input.removeClass('read-only');
	}
	if(object['CreationDate'].length > 0){
		var input = $('#date');
		var year = object["CreationDate"].substr(2, 4);
		var month = object["CreationDate"].substr(6, 2);
		var day = object["CreationDate"].substr(8, 2);
		var date = year + '-' + month + '-' + day;

		input.val(date);
		input.prop('readOnly', true);
		input.addClass('read-only');
	}
	else{
		input.val('');
		input.prop('readOnly', false);
		input.removeClass('read-only');
	}
}



function methodSwitcher(method){
	upload_method  = method;
	if(method == 'local'){
		state="confirm";
		if($('.upload-body[upload-method="local"]').hasClass('hidden'))$('.upload-body[upload-method="local"]').removeClass('hidden');
		if(!$('.upload-body[upload-method="drive"]').hasClass('hidden'))$('.upload-body[upload-method="drive"]').addClass('hidden');
	}
	else{
		if($('.upload-body[upload-method="drive"]').hasClass('hidden'))$('.upload-body[upload-method="drive"]').removeClass('hidden');
		if(!$('.upload-body[upload-method="local"]').hasClass('hidden'))$('.upload-body[upload-method="local"]').addClass('hidden');
	}
}




//http://stackoverflow.com/questions/4068373/center-a-popup-window-on-screen
function PopupCenter(url, title, w, h) {
    // Fixes dual-screen position                         Most browsers      Firefox
    var dualScreenLeft = window.screenLeft != undefined ? window.screenLeft : screen.left;
    var dualScreenTop = window.screenTop != undefined ? window.screenTop : screen.top;
    
    var left = (window.top.outerWidth -  w )/2 +dualScreenLeft;
    var top = window.top.outerHeight / 2 + window.top.screenY - ( h / 2) + dualScreenTop;
    var newWindow = window.open(url, title, 'scrollbars=yes, width=' + w + ', height=' + h + ', top=' + top + ', left=' + left);

    // Puts focus on the newWindow
    if (window.focus) {
        newWindow.focus();
    }

    if(!newWindow || newWindow.closed || typeof newWindow.closed=='undefined') 
	{ 
	     // Ventanas emergentes bloqueadas
	     return false;
	}
	else
		return true;


}


function initial_drive_request(link){
	if (link == '/drive/analizer//'){
		alternator('#error-message', gettext('Debes añadir un enlace de Google Drive a la solicitud'));
		/*if(!$('.folder-wrapper').hasClass('hidden'))$('.folder-wrapper').addClass('hidden');
		if($('#error-message').hasClass('hidden'))$('#error-message').removeClass('hidden');
		$('#error-message').text('Debes añadir un enlace de Google Drive a la solicitud');*/
	}
	else{
		$('#spinner-wrapper').removeClass('hidden');
		xhr = new XMLHttpRequest;
		xhr.open('GET', link, true);
		xhr.onload =function(){
			response = JSON.parse(xhr.responseText);

			if (xhr.readyState == 4 && xhr.status == 200 && !response['error']) {
				if (response['type'] == 'Folder')
					create_drive_table(response);
				else if(response['type'] == 'PDF Document')
					create_drive_document(response);
			}
			else if ((response['error'])){
				$('#spinner-wrapper').removeClass('hidden');
				alternator('#error-message', JSON.parse(xhr.responseText)['message']);
				if  (JSON.parse(xhr.responseText)['code'] == 'gglir')
					PopupCenter(get_credentials_link, 'Iniciar sesion en Google Drive', 650, 700, true);
				/*if(!$('.folder-wrapper').hasClass('hidden'))$('.folder-wrapper').addClass('hidden');
				if($('#error-message').hasClass('hidden'))$('#error-message').removeClass('hidden');
				$('#error-message').text(JSON.parse(xhr.responseText)['message']);*/
			}
			$('#spinner-wrapper').addClass('hidden');
		};
		xhr.onprogress = function(e) {
		    if (e.lengthComputable) {


		    }
		};
		xhr.onloadstart = function(e) {

		};
		xhr.onloadend = function(e) {

		};
		xhr.send();
	}
}


function create_drive_table(response){
	$('.folder-row').remove();
	var files = response['files'];
	if (files.length > 0){
		var code = ['<tr class="folder-row animation-down">',
						'<td><input class="checkbox" type="checkbox" name="id" value="$id"></td>',
						'<td>$filename</td>',
						'<td>$owner</td>',
						'<td>$date</td>',
						'<td>$fileSize</td>',
					'</tr>',]
		$('#drive-title').text(response['folder_name']);
		var body = $('#folder-body');

		for(var i = 0; i < files.length; i++){			
			body.append(code.join('').replace(/\$filename/g, files[i]['title']).replace(/\$owner/g, files[i]['ownerNames']).replace(/\$date/g, format_date(files[i]['modifiedDate'])).replace(/\$fileSize/g, formatSizeUnits(parseInt(files[i]['fileSize']))).replace(/\$id/g, files[i]['id']));
		}

		$('.main-checkbox').click(function(){

			if (this.checked){
				$('.checkbox').prop('checked', true);
			}
			else{
				$('.checkbox').prop('checked', false);
			}
		});

		$('.checkbox').click(function(){
			$('.main-checkbox').prop('indeterminate', true);
		});

		alternator('#folder-table', null);
		/*$('.folder-wrapper').removeClass('hidden');
		if(!$('#error-mesage').hasClass('hidden'))$('#error-message').addClass('hidden');*/
	}
	else{
		alternator('#error-message', gettext('No se encontraron archivos compatibles en el enlace'));
		/*if(!$('.folder-wrapper').hasClass('hidden'))$('.folder-wrapper').addClass('hidden');
		if($('#error-message').hasClass('hidden'))$('#error-message').removeClass('hidden');
		$('#error-message').text('No se encontraron archivos compatibles en el enlace');*/
	}
}

function create_drive_document(response){
	var file = response['file'];
	$('#drive-title').text(file['title']);
	$('#document-owner').text(file['ownerNames']);
	$('#document-email').text(file['owners'][0]['emailAddress']);
	$('#document-modifiedDate').text(format_date(file['modifiedDate']));
	$('#document-size').text(formatSizeUnits(parseInt(file['fileSize'])));
	$('#information-section').attr('document-id', file['id']);
	$('#document-thumbnail').attr('src', file['thumbnailLink']);

	alternator('#information-section', null);
}

//Alterna entre los diferentes tipos de respuesta. Estos son: Carpetas, archivos individuales y mensajes de error.
function alternator(id, message){
	var options = ['#information-section', '#error-message', '#folder-table', "#confirmation-section", "#success-icon", '.cssload-loader', 'local-error'];
	if (id == options[1]){
		$('.cssload-loader').addClass('hidden');
		if(!$('.folder-wrapper').hasClass('hidden'))$('.folder-wrapper').addClass('hidden');
		if($('#error-message').hasClass('hidden'))$('#error-message').removeClass('hidden');
		$('#error-message').text(message);
	}
	else if(id == options[5]){
		$('.upl-hud').addClass('hidden');
		$('.cssload-loader').removeClass('hidden');
	}	
	else if(id == options[6]){
		$('.upl-hud').removeClass('hidden');
		$('.cssload-loader').addClass('hidden');
		$('#message').removeClass('hidden');
		$('#message').html(message);
	}
	else if(id == options[4]){
		$('.upl-hud').removeClass('hidden');
		$('.cssload-loader').addClass('hidden');
		if($(id).hasClass('hidden'))$(id).removeClass('hidden');
		$('#upload-selector-container').addClass('hidden');
		$('.upload-body').addClass('hidden');
		$('.documents-message').addClass('hidden')
		var width = 0;
		var interval = setInterval(function(){
			if (width>100){
				clearInterval(interval);
				window.location.href = upload_link;
			}
			$('#loading-bar').css('width', width.toString() + '%');
			width += 10;
		}, 300);
	}
	else{
		if(id == options[0])state='single';
		else if(id == options[2])state='multi';
		else if(id == options[3])state='confirm';
		if($('.folder-wrapper').hasClass('hidden'))$('.folder-wrapper').removeClass('hidden');
		if($(id).hasClass('hidden'))$(id).removeClass('hidden');
		for(var i = 0; i < options.length; i++){
			if(id != options[i])
				if(!$(options[i]).hasClass('hidden'))$(options[i]).addClass('hidden');			
		}
	}
}

function uploads_5000(){
	for(var i = 0; i < 5000; i++){

		xhr = new XMLHttpRequest;
		var form = new FormData($('#confirm-form')[0]);
		form.append('title0', 'Genomic and Functional Analyses of the 2-Aminophenol Catabolic Pathway and Partial Conversion of Its Substrate into Picolinic Acid in Burkholderia xenovorans LB400' + i);
		form.append('document0', files[0]);
		form.append('local_ids', '0');
		xhr.open('POST', upload_link, true);
		xhr.send(form);		
	}
}
//Maneja algunas de las solicitudes de la aplicacion relacionadas con el boton 'Confirmar'. 
function drive_request_handler(){
	xhr = new XMLHttpRequest;
	if(state=='confirm'){
		if(upload_method == 'drive'){
			var form = new FormData($('#confirm-drive-form')[0]);
			var form_status = $('#confirm-drive-form')[0].checkValidity();
			
		}
		else{
			var form = new FormData($('#confirm-form')[0]);

			form.append('local_ids', Object.keys(files).join(','));
			for(var id in files){
				if (files.hasOwnProperty(id)){
					form.append('document'+id.toString(), files[id]);
				}
			}
			var form_status = $('#confirm-form')[0].checkValidity();
		}
		if(form_status){
			xhr.open('POST', upload_link, true);
			xhr.onload = function(){
				response = JSON.parse(xhr.responseText);
				if (xhr.readyState == 4 && xhr.status == 200 && !response['error']) {
					alternator('#success-icon')
					if(upload_method=='local') extract_content(response['real_ids']);

				}
				else if ((response['error'])){
					alternator('local-error', response['message'])
				}
				
			}
			xhr.send(form);
			alternator('.cssload-loader')
		}
		else{
			if(upload_method=='local'){
				var class_='.field';
				var parent = 'li';
			}
			if(upload_method=='drive'){
				var class_='.drive-field'
				var parent = 'tr';
			}
			$(class_).each(function(i, field){
				if (($(field).val() == null || $(field).val() == '') && $(field).prop('required') == true){
					if($(field).closest(parent).length){
						$(field).closest(parent).addClass('required');
						$($(this)).on('input', function(){
							if($(this).closest(parent).hasClass('required'))$(this).closest(parent).removeClass('required')
								$(this).off();
						});
					}					
					else{
						$(field).addClass('required');
							$($(this)).on('input', function(){
								if($(this).hasClass('required'))$(this).removeClass('required')
									$(this).off('input');
							});
					}
				}
			});
		}
	}
	else{
		xhr.onload =function(){
			response = JSON.parse(xhr.responseText);
			if (xhr.readyState == 4 && xhr.status == 200 && !response['error']) {

				load_confirmation(response['files'])
				extract_content(response['real_ids']);
			}
			else if ((response['error'])){
			}
				
		};

		if(state == 'single'){	
			url = download_drive_link.replace('999', $('#information-section').attr('document-id'));
			xhr.open('GET', url, true);
			xhr.send();
			$('.upl-hud').addClass('hidden');
			$('.cssload-loader').removeClass('hidden');
		}
		else if(state == 'multi'){
			var ids = [];
			$('.checkbox:checked').each(function(){ids.push($(this).val())});
			var url = download_drive_link.replace('999', ids.join('+'));
			xhr.open('GET', url, true);
			xhr.send();
			$('.upl-hud').addClass('hidden');
			$('.cssload-loader').removeClass('hidden');
		}
	}
	
}


function load_confirmation(files){
	alternator('#confirmation-section');
	$('#drive-title').text(gettext('Confirma los datos de tus documentos'));
	$('.confirmation-frame').remove()
	var section = $('#confirm-drive-form');
	var ids = [];
	if(current_lang == "es"){
		var code = ['<table class="confirmation-table confirmation-frame animation-down">',
					'<tr>',
						'<td rowspan="10" class="thumbnail-col"><img src="$thumbnail"></td>',
					'</tr>',
					'<tr>',
						'<td><strong>Titulo:</strong></td>',
						'<td><input type="text" class="drive-field title-field" doc-id="$iddrive" name="title$id" value="$title" placeholder="Ej: Tesis de microbiologia" autocomplete="off" required><div class="crossref-wrapper hidden" doc-id="$iddrive"><div class="loader hidden" doc-id="$iddrive"><img src="' + spinner_link + '"></div><div class="crossref-list-wrapper"><ul class="crossref-list" doc-id="$iddrive"></ul></div></div></td>',
					'</tr>',
					'<tr>',
						'<td><strong>Autor:</strong></td>',
						'<td ><input type="text" class="drive-field" name="author$id" value="$author" placeholder="Ej: Hernán Herreros" required></td>',
					'</tr>',
					'<tr>',
						'<td><strong>Fecha:</strong></td>',
						'<td ><input type="text" class="drive-field" name="date$id" value="$date" placeholder="Ej: 2016-12-30" required></td>',
					'</tr>',
					'<tr>',
						'<td><strong>ISSN:</strong></td>',
						'<td ><input type="text" class="drive-field" name="issn$id" placeholder="No requerido"></td>',
					'</tr>',
					'<tr>',
						'<td><strong>DOI:</strong></td>',
						'<td ><input type="text" class="drive-field" name="doi$id" placeholder="No requerido"></td>',
					'</tr>',
					'<tr>',
						'<td><strong>URL:</strong></td>',
						'<td ><input type="text" class="drive-field" name="url$id" placeholder="ej: http://dx.doi.org/10.1109/ms.2006.34"></td>',
					'</tr>',
					'<tr>',
						'<td><strong>Paginas:</strong></td>',
						'<td ><input type="text" class="drive-field" name="pages$id" placeholder="No requerido"></td>',
					'</tr>',
					'<tr>',
						'<td><strong>Area:</strong></td>',
						'<td >',
							'<select name="category$id" class="form-select drive-field" required>',
								'<option value="" disabled selected>Selecciona una categoria</option>',
								'<option value="1"> Microbiología Molecular</option>',
								'<option value="2">Biotecnología Ambiental</option>',
								'<option value="3">Bionanotecnología</option>',
								'<option value="4">Genómica Funcional y Proteómica</option>',
								'<option value="5">Síntesis de compuestos bioactivos y de interés biotecnológico</option>',
								'<option value="6">Biorremediación de Ambientes Contaminados</option>',
							'</select>',
						'</td>',
					'</tr>',
					'<tr>',
						'<td><strong>Privacidad:</strong></td>',
						'<td >',
							'<select name="type$id" class="form-select drive-field" required>',
								'<option value="" disabled selected>Selecciona privacidad</option>',
								'<option value="0">Público</option>',
								'<option value="1">Privado</option>',
							'</select>',
						'</td>',
					'</tr>',
					'<tr>',
						'<td colspan="3"><textarea class="drive-field abstract-field" name="abstract$id" placeholder="Abstract">$abstract</textarea></td>',
					'</tr>',
				'</table>']
	}
	else if(current_lang == "en"){
		var code = ['<table class="confirmation-table confirmation-frame animation-down">',
					'<tr>',
						'<td rowspan="10" class="thumbnail-col"><img src="$thumbnail"></td>',
					'</tr>',
					'<tr>',
						'<td><strong>' + gettext('Titulo') + ':</strong></td>',
						'<td><input type="text" class="drive-field title-field" doc-id="$iddrive" name="title$id" value="$title" placeholder="' + gettext('Ej: Tesis de microbiologia') + '" autocomplete="off" required><div class="crossref-wrapper hidden" doc-id="$iddrive"><div class="loader hidden" doc-id="$iddrive><img src="' + spinner_link + '"></div><div class="crossref-list-wrapper"><ul class="crossref-list" doc-id="$iddrive"></ul></div></div></td>',
					'</tr>',
					'<tr>',
						'<td><strong>' + gettext('Autor') + ':</strong></td>',
						'<td ><input type="text" class="drive-field" name="author$id" value="$author" placeholder="' + gettext('Ej: Juan Perez') + '" required></td>',
					'</tr>',
					'<tr>',
						'<td><strong>' + gettext('Fecha') + ':</strong></td>',
						'<td ><input type="text" class="drive-field" name="date$id" value="$date" placeholder="' + gettext('Ej: 2016-12-30') + '" required></td>',
					'</tr>',
					'<tr>',
						'<td><strong>' + gettext('ISSN') + ':</strong></td>',
						'<td ><input type="text" class="drive-field" name="issn$id" placeholder="' + gettext('No requerido') + '" ></td>',
					'</tr>',
					'<tr>',
						'<td><strong>' + gettext('DOI') + ':</strong></td>',
						'<td ><input type="text" class="drive-field" name="doi$id" placeholder="' + gettext('No requerido') + '" ></td>',
					'</tr>',
					'<tr>',
						'<td><strong>' + gettext('URL') + ':</strong></td>',
						'<td ><input type="text" class="drive-field" name="url$id" placeholder="' + gettext('ej: http://dx.doi.org/10.1109/ms.2006.34') + '" ></td>',
					'</tr>',
					'<tr>',
						'<td><strong>' + gettext('Paginas') + ':</strong></td>',
						'<td ><input type="text" class="drive-field" name="pages$id" placeholder="' + gettext('No requerido') + '" ></td>',
					'</tr>',
					'<tr>',
						'<td><strong>' + gettext('Area') + ':</strong></td>',
						'<td >',
							'<select name="category$id" class="form-select drive-field" required>',
								'<option value="" disabled selected>' + gettext('Selecciona una categoria') + '</option>',
								'<option value="1"> ' + gettext('Microbiología Molecular') + '</option>',
								'<option value="2">' + gettext('Biotecnología Ambiental') + '</option>',
								'<option value="3">' + gettext('Bionanotecnología') + '</option>',
								'<option value="4">' + gettext('Genómica Funcional y Proteómica') + '</option>',
								'<option value="5">' + gettext('Síntesis de compuestos bioactivos y de interés biotecnológico') + '</option>',
								'<option value="6">' + gettext('Biorremediación de Ambientes Contaminados') + '</option>',
							'</select>',
						'</td>',
					'</tr>',
					'<tr>',
						'<td><strong>' + gettext('Privacidad') + ':</strong></td>',
						'<td >',
							'<select name="type$id" class="form-select drive-field" required>',
								'<option value="" disabled selected>' + gettext('Selecciona privacidad') + '</option>',
								'<option value="0">' + gettext('Público') + '</option>',
								'<option value="1">' + gettext('Privado') + '</option>',
							'</select>',
						'</td>',
					'</tr>',
					'<tr>',
						'<td colspan="3"><textarea class="drive-field abstract-field" name="abstract$id" placeholder="Abstract">$abstract</textarea></td>',
					'</tr>',
				'</table>']
	}
	
	for(var i = 0; i < files.length; i++){
		var completed_code = code.join('').replace(/\$id/g, files[i]['id']).replace(/\$title/g, files[i]['title'] ? files[i]['title']:'').replace(/\$author/g, files[i]['author'] ? files[i]['author']:'').replace(/\$date/g, files[i]['date'] ? files[i]['date'] : '').replace(/\$thumbnail/g, files[i]['thumbnail'] ? static_link.replace('999', files[i]['thumbnail']) : '').replace(/\$abstract/g, files[i]['abstract'] ? files[i]['abstract'] : '');
		section.append(completed_code);
		ids.push(files[i]['id']);

	}
	$('.abstract-field').each(function(){
		if($(this).val() == ''){
			$(this).addClass('loading-abs').prop('disabled','true');
			$(this).closest('td').addClass('loading-abs-wrp');
		}
	});
	$('.title-field').each(function(){
		crossref_query($(this).val(), $(this).attr('doc-id'), true);
	});

	$('.title-field').off();
	$('.title-field').on('input', function(){
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
				else
					crossref_query($this.val(), $this.attr('doc-id'), true);
			}, 2000);
		}
	});
	$('.title-field').focus(function(e){
		$('.crossref-wrapper[doc-id="' + $(this).attr('doc-id') +'"]').removeClass('hidden');
	});
	$('.title-field').keyup(function(e){
		if(e.which == 27 || e.which == 13){
			$('.crossref-wrapper[doc-id="' + $(this).attr('doc-id') +'"]').addClass('hidden');
			$('.loader[doc-id="' + $(this).attr('doc-id') +'"]').addClass('hidden');
		}
	});
	$('.title-field').focusout(function(e){
		var $this = $(this)
		setTimeout(function(){
			$('.crossref-wrapper[doc-id="' + $this.attr('doc-id') +'"]').addClass('hidden');
			$('.loader[doc-id="' + $this.attr('doc-id') +'"]').addClass('hidden');			
		}, 100);
	});
	section.append('<input class="confirmation-frame" type="hidden" value="' + ids.join(',') + '" name="id">');
}



function extract_content(ids){
	var form = new FormData();
	form.append('ids', ids);
	var xhr = new XMLHttpRequest();
	xhr.open('POST', extract_link , true);
	xhr.setRequestHeader("X-CSRFToken", csrf_token);
	if (upload_method =="local"){

		xhr.send(form);
	}
	else{

		xhr.onload = function(){
			var response = JSON.parse(xhr.responseText);
			if (xhr.readyState == 4 && xhr.status == 200 && !response['error']) {
				abs = response['abstracts'];

				for (var i=0; i < abs.length; i++){
					var field = $('.abstract-field[name="abstract' + abs[i]['id'] + '"]');
					field.prop('disabled', false).removeClass('loading-abs').val(abs[i]['abstract']);
					field.closest('td').removeClass('loading-abs-wrp');
				}
			}
		}
		xhr.send(form);
	}
}