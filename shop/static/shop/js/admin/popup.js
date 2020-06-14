(function($) {
	'use strict';

	function shopShowAdminPopup(href, name) {
		var win = window.open(href, name, 'height=500,width=800,resizable=yes,scrollbars=yes');
		win.focus();
		return false;
	}

    window.shopShowAdminPopup = shopShowAdminPopup;
})(django.jQuery);
