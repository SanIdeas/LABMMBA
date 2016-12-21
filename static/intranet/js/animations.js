
//Remueve un elemento de la pantalla con una animacion
function hideElement(class_, remove){

	element = $(class_);
	element.removeClass("upload animation enter down");
	element.addClass("upload animation exit up");
	if(remove){
		setTimeout(function(){
			$(class_)[0].remove();

		}, 200);
	}
	else{
		$(class_).addClass("hidden");

		}
}

function addElement(class_){

	element = $(class_);
	element.removeClass("hidden").removeClass("dn"); //Por si acaso
	element.removeClass("upload animation exit up");
	element.addClass('upload animation enter down');
}
