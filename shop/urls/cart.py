from django.conf.urls.defaults import url, patterns

from shop.views.cart import CartDetails, CartItemDetail


urlpatterns = patterns('',
    url(r'^delete/$', CartDetails.as_view(action='delete'),  # DELETE
        name='cart_delete'),
    url(r'^item/$', CartDetails.as_view(action='post'),  # POST
        name='cart_item_add'),
    url(r'^$', CartDetails.as_view(), name='cart'),  # GET
    url(r'^update/$', CartDetails.as_view(action='put'),
        name='cart_update'),

    # CartItems
    url(r'^item/(?P<id>[0-9]+)$', CartItemDetail.as_view(),
        name='cart_item'),
    url(r'^item/(?P<id>[0-9]+)/delete$',
        CartItemDetail.as_view(action='delete'),
        name='cart_item_delete'),
)
