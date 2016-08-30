/*
Description: JavaScript / jQuery functions for USM
Version: 1.0
Author: ILOGICA
Author URI: http://www.ilogica.cl
*/

var slider;
$(document).ready(function(){

	/* scrollTop Button */
	$(function () {
		$(window).scroll(function () {
			if ($(this).scrollTop() > 300) {
				$('#top').fadeIn();
			} else {
				$('#top').fadeOut();
			}
		});
		$('#top').click(function () {
			$('body,html').animate({
				scrollTop: 0
			}, 800);
			return false;
		});
	});

	$('a').filter(function(){
		return this.hostname && this.hostname !== location.hostname;
	}).addClass('external');
	$('a.external').attr('target', '_blank');
	$('a[href^="mailto:"]').addClass('mail');

	// Slider.
	if($('.royalSlider').length > 0){
		$('.royalSlider').hide();
		setTimeout(function() {
			$('.royalSlider').royalSlider({
				arrowsNav: false, 
				loop: false, 
				keyboardNavEnabled: true, 
				controlsInside: false, 
				arrowsNavAutoHide: false, 
				autoScaleSlider: true, 
				autoHeight: true, 
				autoScaleSliderWidth: 1600, 
				autoScaleSliderHeight: 525, 
				controlNavigation: 'bullets', 
				thumbsFitInViewport: false, 
				navigateByClick: false, 
				slidesSpacing: 0, 
				block: {
					moveEffect: 'none', 
					fadeEffect: true, 
					speed: 600, 
					moveOffset: 100
				},
				autoPlay: {
					enabled: true,
					pauseOnHover: true,
					delay: 6000,
					stopAtAction: false
				}
			}).show();
			slider = $(".royalSlider").data('royalSlider');
			slider.ev.on('rsAfterSlideChange', function(event) {
				slider.updateSliderSize();     
			});
		}, 600);
	}

	setTimeout(function() {
		if($('.royalSlider .rsContent').length == 1){
			$('.royalSlider span.more').css({'margin-bottom':'0'});
		}
		if($('.royalSlider .rsContent').length > 1){
			$('.royalSlider .rsNav').show();
		}
	}, 800);

	setTimeout(function() {
		slider = $(".royalSlider").data('royalSlider');
		slider.updateSliderSize();
	}, 1000);

	// Modal
	$('.single .post a:has(img)').attr('rel', 'post');
	$('#gallery a:has(img)').attr('rel', 'gallery');
	$('a.modal, .single .post a:has(img)').fancybox({
		padding: 2,
		loop: false,
 		helpers: {media: true, overlay: null, title: {type: 'inside'}, overlay: {css: {'background':'rgba(0,0,0,0.6)'}}}
 	});
 	$('#gallery a:has(img)').fancybox({
		padding: 2,
		loop: false,
 		helpers: {media: true, overlay: null, title: {type: 'inside'}, overlay: {css: {'background':'rgba(0,0,0,0.6)'}}},
 		beforeShow: function() {this.title = '<span>'+(this.index + 1) + '/' + this.group.length+'</span>' + (this.title ? ' - ' + this.title : '');}
 	});

 	// Eventos
    $('.evento a.closed .icon').text('+');
	$('.evento a.closed').click(function(){
		$(this).toggleClass('false').next().stop().slideToggle();
		if ($(this).hasClass('false')){
			$(this).children('.icon').text('-');
		} else {
			$(this).children('.icon').text('+');
		}
	});

	// Responsive tables
	;(function($, window, document, undefined) {
		$.fn.responsiveTables = function() {
			var head_col_count = $('thead th').size();
			if ($(head_col_count).length) {
				return this.each(function() {
					var $element = $(this);
					for (i = 0; i <= head_col_count; i++) {
						var head_col_label = $element.find($('thead th:nth-child(' + i + ')')).text();          
						$element.find($('tr td:nth-child(' + i + ')')).attr("data-label", head_col_label);
					};
				});
			};
		};
	})(jQuery, window, document);
	$('.responsive-table').responsiveTables();

	// Smooth animation on click an anchor on the same page.
	$('.anchor').click(function(){
		if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'')&& location.hostname == this.hostname) {
			var $target = $(this.hash);
			target2 = this.hash;
			$target = $target.length && $target || $('[name=' + this.hash.slice(1) +']');
			if ($target.length) {
				var targetOffset = $target.offset().top;
				$('html,body').animate({
					scrollTop: targetOffset
				}, 1000,function(){
					$(target2).addClass('active');
					setTimeout(function() {
						$(target2).removeClass('active');
					}, 800);
				});
				return false;
			}
		}
		return true;
	});

	// Set placeholder value to input fields.
	$('[placeholder]').focus(function() {
		var input = $(this);
		if (input.val() == input.attr('placeholder')) {
			input.val('');
			input.removeClass('placeholder');
		}
	}).blur(function() {
		var input = $(this);
		if (input.val() == '' || input.val() == input.attr('placeholder')) {
			input.addClass('placeholder');input.val(input.attr('placeholder'));
		}
	}).blur().parents('form').submit(function() {
		$(this).find('[placeholder]').each(function() {
			var input = $(this);
			if (input.val() == input.attr('placeholder')) {
				input.val('');
			}
		})
	});

	// Accordion
	$('.accordion .acc-header').append('<span class="icon">+</span>');
	$('.accordion .acc-header .icon').text('+');
	$('.accordion .acc-content').hide();
	$('.accordion .acc-header').click(function(){
		$(this).toggleClass('active').next().stop().slideToggle();
		if ($(this).hasClass('active')){
			$(this).children('.icon').text('-');
		} else {
			$(this).children('.icon').text('+');
		}
	});

	// Mobile nav accordion.
	$('#header a#mobile-nav').click(function(){
		$('#header .mobile-nav').stop().slideToggle();
	});

	// Tablet nav accordion.
	$('#header a.tablet-nav').click(function(){
		$('#header ul.top-nav').stop().slideToggle();
	});

});

$(window).resize(function() {

	// Updata RoyalSlider Size
	$('.royalSlider').royalSlider('updateSliderSize',true);

	// Show/hide tablet accordion top navigation
	var windowResizeWidth = $(window).width();
	if (windowResizeWidth<1000) {
		$('#header ul.top-nav').hide();
	} 
	else {
		$('#header ul.top-nav').show();
		$('#header ul.top-nav a');
	}

});