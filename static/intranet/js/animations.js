
//Remueve un elemento de la pantalla con una animacion
function hideElement(class_, remove){
	console.log("se elimina: " + class_);
	element = $(class_);
	element.removeClass("upload animation enter down");
	element.addClass("upload animation exit up");
	if(remove){
		setTimeout(function(){
			$(class_)[0].remove();
			console.log("remove");
		}, 200);
	}
	else{
		$(class_).addClass("hidden");
		console.log("add hidden to: " + class_);
		}
}

function addElement(class_){
	console.log("se agrega: " + class_);
	element = $(class_);
	element.removeClass("hidden").removeClass("dn"); //Por si acaso
	element.removeClass("upload animation exit up");
	element.addClass('upload animation enter down');
}
