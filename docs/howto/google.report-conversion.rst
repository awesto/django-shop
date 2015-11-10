===========================
Report conversion to Google
===========================


The moment the customer clicks onto the button to purchase, the merchant may report this event as a
conversion to Google. This can be achieved by overriding the purchase button template.

In the project's template folder create a template named ``myshop/checkout/proceed-button.html`` and
add the following content:

.. code-block:: html

	{% extends "shop/checkout/proceed-button.html" %}
	{% load static sekizai_tags %}
	
	{% block proceed-button %}
	{% addtoblock "js" %}<script src="//www.googleadservices.com/pagead/conversion_async.js" type="text/javascript"></script>{% endaddtoblock %}
	{% addtoblock "js" %}<script src="{% static 'shop/js/google-report-conversion.js' %}" type="text/javascript"></script>{% endaddtoblock %}
	{% addtoblock "shop-ng-config" %}['googleReportConversionProvider', function(googleReportConversionProvider) { googleReportConversionProvider.setSnippetVars({google_conversion_id: 12345678, google_conversion_label: "abcDeFGHIJklmN0PQ", google_conversion_value: 12.34, google_conversion_currency: 'EUR', google_remarketing_only: false});}]{% endaddtoblock %}
	{% addtoblock "shop-ng-requires" %}django.shop.google_analytics{% endaddtoblock %}
	<button shop-dialog-proceed ng-click="proceedWithConversion('PURCHASE_NOW')" ng-disabled="stepIsValid===false"{% if instance_css_classes %} class="{{ instance_css_classes }}"{% endif %}{% if instance_inline_styles %} style="{{ instance_inline_styles }}"{% endif %}>{{ icon_left }}{{ instance.content }}{{ icon_right }}</button>
	{% endblock %}

Remember to replace the above snippet with your own ``google_conversion_id`` and
``google_conversion_label``.