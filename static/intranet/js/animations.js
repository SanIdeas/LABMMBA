
//Remueve un elemento de la pantalla con una animacion
function hideElement(class_, remove){
	$(class_).removeClass("animation enter down");
	$(class_).addClass("animation exit up");
	if(remove){
		setTimeout(function(){
			$(class_)[0].remove();	
		}, 200);
	}
}

function addElement(class_){
	$(class_).removeClass("animation exit up");
	$(class_).addClass('animation enter down');
}

// Show hace que solo se muestre. Por lo tanto si el cuadro ya es visible no desaparecera
function toggleCrossref(index, show = false, setfocus = true){
	var cr = $('.crossref[doc-index="$index"'.replace('$index', index));
	if(show){
		cr.removeClass("hidden").addClass("display");
		if(setfocus)
			$('.field[name="title' + index + '"]').focus();
	}
	else{
		cr.removeClass("display").addClass("hidden");
	}
}
