var interval;

$(document).ready(function(){
	var body = $('#content-wrapper');
	var h = $(window).height() - $('#header').height()-$('#lower-bar').height();
	body.height(h + 'px');
	$(window).resize(function(){
		var body = $('#content-wrapper');
		var h = $(window).height() - $('#header').height()-$('#lower-bar').height();
		body.height(h + 'px');
	});
});

$('#resp-btn-menu').click(function(){
	if($('#responsive-menu').hasClass('responsive-menu-close'))
		$('#responsive-menu').removeClass('responsive-menu-close').addClass('responsive-menu-open-v2');
	else
		$('#responsive-menu').addClass('responsive-menu-close').removeClass('responsive-menu-open-v2');				
});


$('#search-field').keypress(function(e){
	if(e.which == 13 && $(this).val() != ''){
		window.location.href = "/intranet/search/999/".replace('999', $(this).val());
	}
});

$('#search-field').on('input', function(){
	//clearTimeout(interval);
	var $this = $(this)
	interval = setTimeout(function(){
		if($this.val() == ''){
			$('#helper-wrapper').addClass('hidden');
		}
		else
			helper($this.val());
	}, 1000);
});