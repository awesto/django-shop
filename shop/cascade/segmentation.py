from cmsplugin_cascade.segmentation.mixins import EmulateUserModelMixin, EmulateUserAdminMixin
from shop.admin.customer import CustomerProxy
from shop.models.customer import CustomerModel, VisitingCustomer


class EmulateCustomerModelMixin(EmulateUserModelMixin):
    UserModel = CustomerProxy

    def get_context_override(self, request):
        """
        Override the request object with an emulated customer.
        """
        context_override = super().get_context_override(request)
        if request.user.is_staff:
            try:
                context_override['customer'] = context_override['user'].customer
            except CustomerModel.DoesNotExist:
                context_override['customer'] = VisitingCustomer()
            except KeyError:
                pass
        return context_override


class EmulateCustomerAdminMixin(EmulateUserAdminMixin):
    UserModel = CustomerProxy
