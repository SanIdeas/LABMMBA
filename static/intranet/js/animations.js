
//Remueve un elemento de la pantalla con una animacion
function hideElement(class_, remove){
	element = $(class_);
	element.removeClass("upload animation enter down");
	element.addClass("upload animation exit up");
	setTimeout(function(){
		if(remove){
			$(class_)[0].remove();
			console.log("remove");
		}
		else
			$(class_).addClass("hidden");	
	}, 200);
}

function addElement(class_){
	element = $(class_);
	element.removeClass("hidden").removeClass("dn"); //Por si acaso
	element.removeClass("upload animation exit up");
	element.addClass('upload animation enter down');
}

// Show hace que solo se muestre. Por lo tanto si el cuadro ya es visible no desaparecera
function toggleCrossref(index, show = false, setfocus = true){
	var cr = $('.crossref[doc-index="$index"]'.replace('$index', index));
	if(show){
		cr.removeClass("hidden").addClass("display");
		if(setfocus)
			$('.field[name="title' + index + '"]').focus();
	}
	else{
		cr.removeClass("display").addClass("hidden");
	}
}
