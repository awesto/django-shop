# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from cms.wizards.wizard_base import Wizard
from cms.wizards.wizard_pool import wizard_pool


if settings.SHOP_TUTORIAL in ('commodity', 'i18n_commodity'):
    from shop.models.defaults.commodity import Commodity
    from shop.forms.wizards import CommodityWizardForm

    commodity_wizard = Wizard(
        title=_("New Commodity"),
        weight=200,
        form=CommodityWizardForm,
        description=_("Create a new Commodity instance"),
        model=Commodity,
        template_name='shop/wizards/create_product.html'
    )
    wizard_pool.register(commodity_wizard)
