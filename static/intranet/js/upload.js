(function($){
	//Resetea el input de archivo
	$.fn.resetInput = function(){
		this.wrap('<form>').closest('form').get(0).reset();
		this.unwrap();
	};
})(jQuery);



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
	console.log(object);
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
		var date = day + '/' + month + '/' + year;

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

function getMeta(file){
	var reader  = new FileReader();
				
	reader.addEventListener("load", function () {
		PDFJS.getDocument(convertDataURIToBinary(reader.result)).then(function (pdfDoc_) {
		    pdfDoc = pdfDoc_;   
		    pdfDoc.getMetadata().then(function(stuff) {
		        //console.log(stuff); // Metadata object here
		        replaceValues(stuff['info']);
		    }).catch(function(err) {
		       console.log('Error getting meta data');
		       console.log(err);
		    });

		   // Render the first page or whatever here
		   // More code . . . 
		}).catch(function(err) {
		    console.log('Error getting PDF from ' + url);
		    console.log(err);
		});
	}, false);

	reader.readAsDataURL(file);
}