$(document).ready(function(){
	// Si es un telefono o tablet, se ajusta la altura con js
	var is_safari = navigator.userAgent.indexOf("Safari") > -1;
	if(window.mobilecheck() || is_safari){
		var body = $('section#content');
		var h = $(window).height() - $('header').height()-$('.bar').height();
		body.height(h + 'px');
		$(window).resize(function(){
			if(!	$('.mobile-nav').is(':visible')){
				var body = $('section#content');
				var h = $(window).height() - $('header').height()-$('.bar').height();
				body.height(h + 'px');
			}
		});
	}

});

$('#search').submit(function(e){
	e.preventDefault()
	if($('#searchPhrase').val().trim() != '')
		window.open($(this).attr('url').replace('999', encodeURIComponent($('#searchPhrase').val().trim())), '_self');
});

