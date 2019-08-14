
django.jQuery(function($) {
	'use strict';

	django.cascade.ShopLinkPlugin = ring.create(eval(django.cascade.ring_plugin_bases.ShopLinkPlugin), {
		constructor: function() {
			this.$super();

			// be more intuitive, reorganize layout by moving 'Link Target'
			$('.form-row.field-link_target').before($('.form-row.field-product'));
		},
		initializeLinkTypes: function() {
			this.$super();
			this.linkTypes['product'] = new this.LinkType('.form-row.field-product', true);
		}
	});
});
