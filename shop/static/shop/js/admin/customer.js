django.jQuery(function($) {
'use strict';

// be more intuitive, reorganize layout by moving fieldset 'Customers' on the top
$('#customer-group').insertAfter($('#customerproxy_form fieldset:first-child').first());

});
