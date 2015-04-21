django.jQuery(function($) {
	'use strict';

	var $title = $('#id_glossary_page_title');
	var $slug = $('#id_glossary_slug');

	function update(){
		var value = $title.val();
		if (window.UNIHANDECODER) {
			value = UNIHANDECODER.decode(value);
		}
		$slug.val(URLify(value, 64));
	};
	$title.keyup(update);
	update();
});
