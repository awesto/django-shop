from shop.payment.modifiers import PayInAdvanceModifier
from django.utils.translation import gettext_lazy as _


class ComplexPayInAdvanceModifier(PayInAdvanceModifier):
    identifier = "complex-pay-in-advance-modifier"
    def get_choice(self):
        return (self.identifier, _("Pay in advance with complex payment system X"))
