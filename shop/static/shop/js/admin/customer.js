django.jQuery(function($) {
'use strict';

// be more intuitive, reorganize layout by moving fieldset 'Customers' on the top
$('fieldset:first-child').before($('#customer-group'));

});
