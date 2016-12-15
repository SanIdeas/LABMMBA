var last_cr_query = {};
var crossref_timeout, crossref_busy = false;
// Escucha los clicks de la pagina
// Usada para cerrar o no los cuadros de crossref
$(window).click(function(e){
	var target = $(e.target);
	var index = (target.parents('.crossref').length > 0) ? target.closest('.crossref').attr('doc-index') : target.attr('doc-index');
	$('.crossref').each(function(){
		if($(this).attr('doc-index') != index){
			closeCrossref($(this).attr('doc-index'));
		}
	})
});

function openCrossref(index){
	var cr = $('.crossref[doc-index="$index"]'.replace('$index', index));
	if(cr.hasClass('hidden')){
		cr.removeClass("hidden").addClass("display");
	}
}

function closeCrossref(index){
	var cr = $('.crossref[doc-index="$index"]'.replace('$index', index));
	if(cr.hasClass('display')){
		cr.removeClass("display").addClass("hidden");
	}
}

function enableCrossref(){

	// Cuando se ingresa texto al campo de titulo
	$('.field[field-name="title"]').off();
	$('.field[field-name="title"]').on('input', function(){
		last_cr_query[parseInt($(this).attr('doc-index'))] = $(this).val();
		if(!crossref_busy){
			crossref_busy = true;

			openCrossref($(this).attr('doc-index'));
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
		var cr = $(this).siblings('.crossref');
		if(cr.find('.records.list').find('li').length > 0)
			openCrossref($(this).attr('doc-index'));
	});
	
	// Cuando se presiona esc o enter, se esconde el cuadro.
	$('.field[field-name="title"]').keyup(function(e){
		if(e.which == 27 || e.which == 13){
			$(this).blur();
			closeCrossref($(this).attr('doc-index'));
		}
	});
}

function crossref_query(query, doc_id, open = true){
	// Se muestra el icono que gira y se remueve el check
	$('.fa-check[doc-index="' + doc_id +'"]').addClass('hidden');
	$('.loader[doc-index="' + doc_id +'"]').removeClass('hidden');

	$.ajax({
		url: crossref_link.replace('999', query.trim()),
		method: 'GET'
		/*beforeSend: function(xhr){
			xhr.setRequestHeader("X-CSRFToken", csrf_token);
		}*/
	}).done(function(response){
		if(!response['error']) {
			$('.records.root[doc-index="' + doc_id +'"]').children().remove();
			$('.records.root[doc-index="' + doc_id +'"]').append(response);

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
				closeCrossref(index);
			});
			// Se meuestra el icono check
			$('.fa-check[doc-index="' + doc_id +'"]').removeClass('hidden');
		}
		$('.loader[doc-index="' + doc_id +'"]').addClass('hidden');
		//Comprueba si hubo un cambio en el campo de texto desde que mando la solicitud
		if(last_cr_query[doc_id] != undefined){
			if(last_cr_query[doc_id].localeCompare(query) != 0){
				crossref_query(last_cr_query[doc_id], doc_id);
			}
			else
				crossref_busy = false;
		}

	});		
}