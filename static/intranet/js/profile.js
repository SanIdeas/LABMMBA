function closeForm(){
    $('#picture-input').wrap('<form>').closest('form').get(0).reset();
	$('#picture-input').unwrap();
}

function readURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function (e) {
            $('#picture-circle').attr('src', e.target.result);
        }

        reader.readAsDataURL(input.files[0]);
    }
}
