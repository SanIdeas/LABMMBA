var clicked, moved = false, clickX, prev_pos,xcoord, direction, speed = 0, updateScrollPos = function(e) {
	if(clickX - e.pageX != 0){
	    $('#categories').scrollLeft( prev_pos + clickX - e.pageX);
        moved = true;
	}
}
var mrefreshinterval = 50; // update display every 500ms
var lastmousex=-1;
$('html').mousemove(function(e) {
 var mousex = e.pageX;
     xcoord += mousex-lastmousex;
 lastmousex = mousex;
});

setInterval(function(){
	speed = xcoord / 0.5;
	xcoord = 0;
}, mrefreshinterval);


$('#categories-list').on({
    'mousemove': function(e) {
        clicked && updateScrollPos(e);
    },
    'mousedown': function(e) {
    	$('#categories').finish();
		prev_pos = $('#categories').scrollLeft();
        clicked = true;
        clickX = e.pageX;
    },
    'mouseup': function(e) {
        clicked = false;
        $('#categories').animate({scrollLeft: $('#categories').scrollLeft() - speed}, 1000, "easeOutQuint");
    }
});

$('.category-label').click(function(e){
	if(moved){
		moved = false;
		e.preventDefault();
	}
});

$('.category-checkbox').on('change', function(){
	if($(this).prop('checked')){
		$('.check-background[cat-num="' + $(this).attr('cat-num') + '"]').removeClass('hidden');
	}
	else{
		$('.check-background[cat-num="' + $(this).attr('cat-num') + '"]').addClass('hidden');
	}
});

$('#filter-btn').click(function(){
	var filters = $('#filters')
	if(filters.hasClass('filters-hidden')) filters.removeClass('filters-hidden').addClass("filters-visible");
	else filters.addClass('filters-hidden').removeClass("filters-visible");
});