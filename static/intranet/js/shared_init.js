$(document).ready(function(){
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
});