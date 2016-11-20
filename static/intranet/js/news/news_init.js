$(document).ready(function(){
	$('a.add').fancybox({
		width: 600,
		height: 'auto',
		autoSize: false,
		closeBtn: false,
	});
	$('a.delete.modal').fancybox({
		autoSize: true,
		beforeShow:function(links, index){
			var self = $(this.element);
			$('.confirm[type="title"]').attr('data', self.attr('data-title')).html(self.attr('data-title'));
			$('.confirm[type="date"]').attr('data', self.attr('data-date')).html(self.attr('data-date'));
			$('.confirm[type="send"]').attr('href', delete_url.replace('888', self.attr('data-id')));
		}
	});
});
