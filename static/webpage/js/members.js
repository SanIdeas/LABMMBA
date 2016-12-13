$(document).ready(function() {

	/* This is basic - uses default settings */
	
	$("a#single_image").fancybox();
	
	/* Using custom settings */
	$('.member').click(function(){
		$('#fancy-name').text($(this).attr('name'));
		$('#fancy-description').text($(this).attr('description'));
		$('#fancy-img').attr("src",($(this).attr('member-img')));
		console.log($(this).attr('member-img'));
	});
	$("div.member").fancybox({
		'hideOnContentClick': true,
		'autoSize' : false,
    	'width'    : "80%",
    	'height'   : "auto"
	});

	/* Apply fancybox to multiple items */
	
	$("member.group").fancybox({
		'transitionIn'	:	'elastic',
		'transitionOut'	:	'elastic',
		'speedIn'		:	600, 
		'speedOut'		:	200, 
		'overlayShow'	:	false
	});
	
});