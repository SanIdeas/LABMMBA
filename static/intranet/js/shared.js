function helper(query){
	var code = [,'<li class="helper-row">',
					'<a href="$link">',
						'<h4>$title</h4>',
						'<h6>$author</h6>',
					'</a>',
				'</li>'].join('');
	xhr = new XMLHttpRequest;
	xhr.open('GET', helper_link.replace('999', query), true);
	xhr.onload =function(){
		response = JSON.parse(xhr.responseText);
		console.log(response);
		if (xhr.readyState == 4 && xhr.status == 200 && !response['error']) {
			var list = response['list'];
			$('.helper-row').remove();
			var helper = $('#helper');
			for(var i = 0; i < list.length; i++){
				var link = document_link.replace('888', list[i]['author']).replace('999', list[i]['title']);
				var row = code.replace('$link', link).replace('$title', list[i]['title']).replace('$author', list[i]['author'])
				helper.append(row);
			}
			$('#helper-wrapper').removeClass('hidden');
		}
	};
	xhr.send();
}
