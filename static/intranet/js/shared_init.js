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

$('#search').submit(function(e){
	e.preventDefault()
	if($('#searchPhrase').val() != '')
		window.open($(this).attr('url').replace('999', encodeURIComponent($('#searchPhrase').val())), '_self');
});