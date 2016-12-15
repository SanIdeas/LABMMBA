var imgIndex = 0;
var content = {};
var editor;
window.addEventListener('load', function() {
    ContentTools.IMAGE_UPLOADER = imageUploader;
    ContentTools.StylePalette.add([
	    new ContentTools.Style('Author', 'author', ['p']),
	    new ContentTools.Style('Align to left', 'alignleft', ['img']),
	    new ContentTools.Style('Align to right', 'alignright', ['img'])
	]);
	editor = ContentTools.EditorApp.get();
	editor.init('*[data-editable]', 'data-name');

	// Accionado cuando el usuario desea guardar los cambios de la noticia
	editor.addEventListener('saved', function (ev) {
	    var name, payload, regions, xhr;

	    // Si no hubo cambios se salta el proceso
	    regions = ev.detail().regions;
	    if (Object.keys(regions).length == 0) {
	        return;
	    }	    

	    // Editor ocupado mientras se actualizan los datos
	    editor.busy(true);
	    // Se obtienen las imagenes del area editable
	    var object = getImages();

	    // Si hay imagenes estas se envian antes que el contenido
	    if(objectLength(object) > 0){
	    	var form = new FormData();
			form.append('csrfmiddlewaretoken', csrf_token);
			form.append('info', JSON.stringify({'author': author, 'news_id': id}));

			// Se guardan los binarios de las imagenes en el formulario
			for (var property in object) {
			    if (object.hasOwnProperty(property)) {
			        form.append(property,object[property], 'filename.jpg');
			    }
			}
			$.ajax({
				url: save_images_url,
				method: "POST",
				data: form,
				processData: false,
				contentType: false,
			}).done(function(response){
				if(!response['error']){
					editor.busy(false);
					sendPayload(regions, response['urls']);
				}
			}).error(function(){
				editor.busy(false);
			});
	    }
	    else{
	    	sendPayload(regions);
	    }
	});
});
// Para rotar una imagen
function rotateImage(direction, dialog) {
	var img = new Image();
	img.src = image.url;
	var cw = img.width, ch = img.height, cx = 0, cy = 0, rotation = 90;

	var canvas = document.createElement('canvas');
	var context = canvas.getContext('2d');

	//   Calculate new canvas size and x/y coorditates for image
	switch(direction){
	     case 'CW':
	          cw = img.height;
	          ch = img.width;
	          cy = img.height * (-1);
	          break;
	     case 'CCW':
	          cw = img.height;
	          ch = img.width;
	          cx = img.width * (-1);
	          rotation *= -1
	          break;
	}

	//  Rotate image
	canvas.setAttribute('width', cw);
	canvas.setAttribute('height', ch);
	context.rotate(rotation * Math.PI / 180);
	context.drawImage(img, cx, cy);

    // Obtiene la url de la imagen ingresada por el input
    var reader = new FileReader();

    // Define functions to handle upload progress and completion
    	reader.onprogress = function (ev) {
        // Set the progress for the upload
        dialog.progress((ev.loaded / ev.total) * 100);
    }
    

    reader.onload = function (e) {
    	var img = new Image();
    	img.src = e.target.result;
    	// Store the image details
        image = {
        	size: [img.width, img.height], 
            url: e.target.result
            };
        // Populate the dialog
        dialog.populate(image.url, image.size);
        // Free the dialog from its busy state
    	dialog.busy(false);
    }    
	// Set the dialog to busy while the rotate is performed
        dialog.busy(true);

    canvas.toBlob(function(blob){
    	reader.readAsDataURL(blob);
    });

}

function imageUploader(dialog){
	dialog.addEventListener('imageuploader.cancelupload', function () {
        // Cancel the current upload

        // Set the dialog to empty
        dialog.state('empty');
    });

	// Se limpia el cuadro con la imagen
    dialog.addEventListener('imageuploader.clear', function () {
        // Clear the current image
        dialog.clear();
        image = null;
    });

	// Obtiene la imagen ingresada por el usuario
	dialog.addEventListener('imageuploader.fileready', function (ev) {
        // Upload a file to the server
        var formData;
        var file = ev.detail().file;

        // Obtiene la url de la imagen ingresada por el input
        var reader = new FileReader();

        // Define functions to handle upload progress and completion
        reader.onprogress = function (ev) {
            // Set the progress for the upload
            dialog.progress((ev.loaded / ev.total) * 100);
        }
        

	    reader.onload = function (e) {
	    	var img = new Image();
	    	img.src = e.target.result;
	    	// Store the image details
                image = {
                	size: [img.width, img.height], 
                    url: e.target.result
                    };

                // Populate the dialog
                dialog.populate(image.url, image.size);
	    }      

        // Set the dialog state to uploading and reset the progress bar to 0
        dialog.state('uploading');
        dialog.progress(0);

        reader.readAsDataURL(file);
    });

    dialog.addEventListener('imageuploader.rotateccw', function () {
        rotateImage('CCW', dialog);
    });

    dialog.addEventListener('imageuploader.rotatecw', function () {
        rotateImage('CW', dialog);
    });

    // La imagen se agrega al documento
    dialog.addEventListener('imageuploader.save', function () {
    	var img = new Image();
    	img.src = image.url
        // Set the dialog to busy while the rotate is performed
        dialog.busy(true);
        max = 1;
        if (img.width > 300){
        	max = 300/img.width
        }
        dialog.save(
	        image.url,
	        [img.width*max, img.height*max],
	        {
	            'data-ce-max-width': img.width*max,
	            'image-id': imgIndex++,
	        });
        // Free the dialog from its busy state
    	dialog.busy(false);

    });

}

function getImages() {
	images = {};
	$('.content').find('img[image-id]').each(function(){
		images[$(this).attr('image-id')] = convertDataURIToBinary($(this).attr('src'));
	});
    return images;
}

function convertDataURIToBinary(dataURI) {
	// convert base64 to raw binary data held in a string
    // doesn't handle URLEncoded DataURIs - see SO answer #6850276 for code that does this
    var byteString = atob(dataURI.split(',')[1]);
    // separate out the mime component
    var mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];
    // write the bytes of the string to an ArrayBuffer
    var ab = new ArrayBuffer(byteString.length);
    var dw = new DataView(ab);
    for(var i = 0; i < byteString.length; i++) {
        dw.setUint8(i, byteString.charCodeAt(i));
    }
    // write the ArrayBuffer to a blob, and you're done
    return new Blob([ab], {type: mimeString});
}

// Se encarga de asociar las url de las imagenes retornadas por el servidor al contenido editable
// y luego enviarlo devuelta al servidor
function sendPayload(regions, pictures={}){
	// Se recolecta el contenido de las areas editables
    payload = new FormData();
    payload.append('csrfmiddlewaretoken', csrf_token);
    for (name in regions) {
        if (regions.hasOwnProperty(name)) {
        	if (name == 'news-content')
            	payload.append(name, formatContent(regions[name], pictures)); // Solo se almacenan imagenes del cuerpo
            else{
            	var title = formatTitle(regions[name]);
            	console.log('title', title);
            	payload.append(name + '-html', title['html']);
            	payload.append(name, title['text']);
            }
        }
    }

    $.ajax({
		url: news_editor_url,
		method: "POST",
		data: payload,
		processData: false,
		contentType: false,
	}).done(function(response){
		if(!response['error']){
			editor.busy(false);
			new ContentTools.FlashUI('ok');
		}
	}).error(function(){
		editor.busy(false);
		new ContentTools.FlashUI('no');
	});
}

function formatContent(content, pictures){
	var body = $(content);
	// Se recorren las url de las imagenes y se asocian a sus img respectivos
	for (var i = 0; i < pictures.length; i++) {
		body.closest('img[image-id="' + pictures[i]['client_side_id'] +'"]').attr('src', pictures[i]['url']).attr('image-id', null);
	}
	return body.map(function(){return $(this).prop('outerHTML')}).get().join('\n');
}

function formatTitle(content){
	var title = $(content).text();
	console.log('title', title);
	if(title != undefined)
		title = title.trim().replace(/\s+/g,' ');
	else
		title = '';
	return {'html': '<h1 class="c12">' + title + '</h1>', 'text': title};
}

// Retorna el largo de un objeto
function objectLength(object){
	var count=0;
	for(i in object){
		if(object.hasOwnProperty(i))
			count++;
	}
	return count;
}