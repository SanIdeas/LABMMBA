var touched;
$(document).ready(function(){
	var setup = $('#setup');
	var h =  $(window).height() - $('#header').height() - 50 - $('#lower-bar').height();
	console.log(h);
	setup.height(h + 'px');
	$(window).resize(function(){
		var setup = $('#setup');
		var h =  $(window).height() - $('#header').height() - 50 - $('#lower-bar').height();
		setup.height(h + 'px');
	});
});

$('.adm-selector').click(function(){
	if(!$(this).hasClass('disabled')){
		var $this = $(this);
		$.ajax({
			url: setup_link.replace('999', $(this).attr('setup-action')),
			method: 'POST',
			beforeSend: function(xhr){
				xhr.setRequestHeader("X-CSRFToken", csrf_token);
			}
		}).done(function(html){
			$('#adm-selectors-wpr').addClass('setup-hidden');
			$('#setup-title').text($this.attr('setup-title'));
			$('#setup-icon').removeClass().addClass($this.attr('setup-icon'));
			$('#setup-container').removeClass('setup-hidden');
			$('#main-wrapper').addClass('overflow-hidden');
			$('#setup').children().remove();
			$('#setup').append(html);
		});
	}
});

$('#setup-return-btn').click(function(){
	$('#adm-selectors-wpr').removeClass('setup-hidden');
	$('#setup-container').addClass('setup-hidden');
	$('#main-wrapper').removeClass('overflow-hidden');
})